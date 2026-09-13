"""Bounded symbolic verification of split Edge output loops (read-only).

Instruction addresses come from PE exception-directory function boundaries.
Only a small, explicitly modeled instruction subset is accepted. Unknown
instructions, branches, values or ambiguous loops reject the candidate.
"""
from collections import deque
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_REG, X86_OP_IMM, X86_OP_MEM

from gamma22_patcher import HDR_OUTPUT_HELPER_BYTES, PatchError, rva_to_offset


def family(ins, reg):
    name = ins.reg_name(reg)
    aliases = {'eax':'rax','ax':'rax','al':'rax','ecx':'rcx','cx':'rcx','cl':'rcx',
               'edx':'rdx','dx':'rdx','dl':'rdx','ebx':'rbx','bx':'rbx','bl':'rbx',
               'edi':'rdi','di':'rdi','dil':'rdi','esi':'rsi','si':'rsi','sil':'rsi'}
    if name.startswith('r') and name[1:-1].isdigit() and name[-1] in 'dbw':
        return name[:-1]
    return aliases.get(name, name)


def find_split_output_loop(dll, sections, text, text_rva):
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = True
    helpers = []
    pos = 0
    while (pos := text.find(HDR_OUTPUT_HELPER_BYTES, pos)) >= 0:
        helpers.append(text_rva + pos)
        pos += 1
    if len(helpers) != 1:
        raise PatchError('Semantic Edge analysis requires one exact output helper')
    helper = helpers[0]
    pdata = next((s for s in sections if s[0] == '.pdata'), None)
    if pdata is None:
        raise PatchError('Edge output loop analysis requires PE function boundaries')
    with dll.open('rb') as stream:
        stream.seek(pdata[3])
        entries = stream.read(pdata[4])
        def read(rva, size):
            stream.seek(rva_to_offset(sections, rva))
            return stream.read(size)

        calls_to_helper = []
        pos = 0
        while (pos := text.find(b'\xe8', pos)) >= 0:
            if pos + 5 <= len(text) and text_rva+pos+5+struct.unpack_from('<i',text,pos+1)[0] == helper:
                calls_to_helper.append(text_rva+pos)
            pos += 1
        results = []
        for offset in range(0, len(entries) - 11, 12):
            start, end, _ = struct.unpack_from('<III', entries, offset)
            if not (text_rva <= start < end <= text_rva + len(text)) or end-start > 65536:
                continue
            code = text[start-text_rva:end-text_rva]
            # Cheap prefilter only; instruction boundaries are decoded below.
            if not any(start <= call < end for call in calls_to_helper):
                continue
            instructions = list(decoder.disasm(code, start))
            by_address = {i.address:i for i in instructions}
            for n, zero in enumerate(instructions[:-2]):
                lea, jump = instructions[n+1:n+3]
                if not (zero.mnemonic == 'xor' and len(zero.operands)==2
                        and all(o.type==X86_OP_REG for o in zero.operands)
                        and zero.operands[0].reg==zero.operands[1].reg
                        and lea.mnemonic=='lea' and lea.operands[1].type==X86_OP_MEM
                        and lea.reg_name(lea.operands[1].mem.base)=='rip'
                        and jump.mnemonic=='jmp' and jump.operands[0].type==X86_OP_IMM):
                    continue
                index = family(zero,zero.operands[0].reg)
                table_reg = family(lea,lea.operands[0].reg)
                if index == table_reg or zero.operands[0].size not in (4,8):
                    continue
                table = lea.address+lea.size+lea.operands[1].mem.disp
                if read(table,3) != b'\x01\x02\x00':
                    continue
                regs = {index:('index',),table_reg:('table',)}
                # Resolve nonvolatile input addresses/constants from the nearest
                # preceding write; never skip over an unmodeled writer.
                for reg in ('rbx','rbp','rsi','rdi','r12','r13','r14','r15'):
                    if reg in regs:
                        continue
                    for prev in reversed(instructions[max(0,n-80):n]):
                        if prev.mnemonic.startswith('j') or prev.mnemonic in ('call','ret'):
                            break
                        if reg not in {family(prev,r) for r in prev.regs_access()[1]}:
                            continue
                        ops=prev.operands
                        if prev.mnemonic=='lea' and len(ops)==2 and ops[1].type==X86_OP_MEM and prev.reg_name(ops[1].mem.base)=='rsp' and not ops[1].mem.index:
                            regs[reg]=('stack',ops[1].mem.disp)
                        elif prev.mnemonic in ('mov','movabs') and len(ops)==2 and ops[1].type==X86_OP_IMM:
                            regs[reg]=ops[1].imm
                        break
                try:
                    limit = verify_paths(by_address,jump.operands[0].imm,regs,index,helper)
                except ValueError:
                    continue
                # Keep all decoded function bytes as evidence, excluding the
                # mutable loop limit. This also covers resolved input writers.
                checks = [("Edge semantic function prefix",start,code[:limit.address-start]),
                          ("Edge semantic function suffix",limit.address+limit.size,code[limit.address+limit.size-start:])]
                results.append(dict(loop_limit_rva=limit.address,usage_table_rva=table,
                                    output_helper_rva=helper,loop_context=b'',
                                    loop_original=bytes(limit.bytes),
                                    loop_patched=bytes(limit.bytes[:limit.imm_offset])+b'\x03'+bytes(limit.bytes[limit.imm_offset+1:]),
                                    semantic_checks=checks))
        unique = {r['loop_limit_rva']:r for r in results}
        if len(unique)!=1 or len(results)!=1:
            raise PatchError(f'Expected one verified semantic Edge output loop; found {len(results)}')
        return next(iter(unique.values()))


def verify_paths(code, entry, initial, index, helper):
    queue=deque([(entry,dict(initial),{},[],set())])
    ends=[]
    steps=0
    while queue:
        pc,regs,stack,calls,visited=queue.popleft()
        while True:
            steps+=1
            if steps>256 or pc in visited or pc not in code:
                raise ValueError('unbounded or external control flow')
            visited.add(pc)
            ins=code[pc]; ops=ins.operands; pc+=ins.size
            def address(op):
                m=op.mem
                if ins.reg_name(m.base)=='rsp' and not m.index:
                    return ('stack',m.disp)
                values={regs.get(family(ins,r)) for r in (m.base,m.index) if r}
                if values=={('index',),('table',)} and m.scale==1 and m.disp==0:
                    return ('usage-address',)
                raise ValueError('unknown address')
            def value(op):
                if op.type==X86_OP_IMM: return op.imm
                if op.type==X86_OP_REG:
                    result=regs.get(family(ins,op.reg))
                    if result is None: raise ValueError('unknown register')
                    return result
                a=address(op)
                if a==('usage-address',) and op.size==1: return ('usage',)
                if a in stack: return stack[a]
                raise ValueError('unknown load')
            if ins.mnemonic in ('mov','movabs','lea'):
                result=address(ops[1]) if ins.mnemonic=='lea' else value(ops[1])
                if ops[0].type==X86_OP_REG: regs[family(ins,ops[0].reg)]=result
                elif ops[0].type==X86_OP_MEM: stack[address(ops[0])]=result
                else: raise ValueError('unsupported destination')
            elif ins.mnemonic=='xor' and ops[0].type==X86_OP_REG and ops[1].type==X86_OP_REG and ops[0].reg==ops[1].reg:
                regs[family(ins,ops[0].reg)]=0
            elif ins.mnemonic=='call' and ops[0].type==X86_OP_IMM:
                if ops[0].imm==helper:
                    args=tuple(regs.get(k) for k in ('rcx','rdx','r8','r9'))
                    if not (isinstance(args[0],tuple) and args[0][0]=='stack'
                            and args[1]==('usage',) and args[2]==len(calls)
                            and isinstance(args[3],tuple) and args[3][0]=='stack'
                            and stack.get(('stack',32)) in (0xe00000001,0x900000001)):
                        raise ValueError('incorrect output arguments')
                    calls.append(args)
                    if len(calls)>2: raise ValueError('extra output call')
                elif calls:
                    raise ValueError('unknown call after output')
                for reg in ('rax','rcx','rdx','r8','r9','r10','r11'): regs.pop(reg,None)
            elif ins.mnemonic=='inc' and ops[0].type==X86_OP_REG and family(ins,ops[0].reg)==index and regs.get(index)==('index',):
                regs[index]=('index-plus-one',)
            elif ins.mnemonic=='cmp':
                if ops[0].type==X86_OP_REG and family(ins,ops[0].reg)==index:
                    if not (ops[1].type==X86_OP_IMM and ops[1].imm==2 and ins.imm_size==1
                            and regs.get(index)==('index-plus-one',) and len(calls)==2
                            and calls[0][0]==calls[1][0]):
                        raise ValueError('invalid loop termination')
                    branch=code.get(pc)
                    if not (branch and branch.mnemonic=='je' and branch.operands[0].type==X86_OP_IMM
                            and branch.operands[0].imm in code and pc+branch.size==entry):
                        raise ValueError('invalid loop back edge')
                    ends.append(ins); break
                if not (ops[0].type==X86_OP_REG and family(ins,ops[0].reg)=='rax'
                        and ops[1].type==X86_OP_IMM):
                    raise ValueError('unmodeled condition')
                branch=code.get(pc)
                if not (branch and branch.mnemonic in ('jl','jge') and branch.operands[0].type==X86_OP_IMM):
                    raise ValueError('unmodeled branch')
                queue.append((branch.operands[0].imm,dict(regs),dict(stack),list(calls),set(visited)))
                pc+=branch.size
            elif ins.mnemonic=='jmp' and ops[0].type==X86_OP_IMM:
                pc=ops[0].imm
            else:
                raise ValueError('unmodeled instruction')
    if len(ends)!=2 or len({i.address for i in ends})!=1:
        raise ValueError('expected both output format paths')
    return ends[0]
