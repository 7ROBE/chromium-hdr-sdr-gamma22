import struct
import unittest

import gamma22_patcher as patcher


class ChromeOutputHookTests(unittest.TestCase):
    TEXT_RVA = 0x1000
    HELPER_OFFSET = 0x500

    def image(self, stack_object=0x230, output_table=0x660, hook_offsets=(0x100,)):
        text = bytearray(b"\xCC" * 0x800)
        text[
            self.HELPER_OFFSET : self.HELPER_OFFSET
            + len(patcher.HDR_OUTPUT_HELPER_BYTES)
        ] = patcher.HDR_OUTPUT_HELPER_BYTES
        helper_rva = self.TEXT_RVA + self.HELPER_OFFSET
        for hook_offset in hook_offsets:
            call_offset = hook_offset + len(patcher.HDR_OUTPUT_HOOK_ORIGINAL)
            text[hook_offset - 16 : hook_offset - 8] = (
                b"\x48\x8D\x8C\x24" + struct.pack("<I", stack_object)
            )
            text[hook_offset - 8 : hook_offset] = (
                b"\x4C\x8D\x8C\x24" + struct.pack("<I", output_table)
            )
            text[hook_offset:call_offset] = patcher.HDR_OUTPUT_HOOK_ORIGINAL
            displacement = helper_rva - (self.TEXT_RVA + call_offset + 5)
            text[call_offset:call_offset + 5] = b"\xE8" + struct.pack(
                "<i", displacement
            )
        return text

    def test_chrome_151_to_153_stack_layouts(self):
        for stack_object, output_table in ((0x230, 0x660), (0x220, 0x650)):
            with self.subTest(stack_object=stack_object):
                hook, helper = patcher.find_chrome_hdr_output_hook_in_text(
                    self.image(stack_object, output_table), self.TEXT_RVA
                )
                self.assertEqual(hook, self.TEXT_RVA + 0x100)
                self.assertEqual(helper, self.TEXT_RVA + self.HELPER_OFFSET)

    def test_missing_hook_is_rejected(self):
        with self.assertRaisesRegex(patcher.PatchError, "output hook, found 0"):
            patcher.find_chrome_hdr_output_hook_in_text(
                self.image(hook_offsets=()), self.TEXT_RVA
            )

    def test_ambiguous_hooks_are_rejected(self):
        with self.assertRaisesRegex(patcher.PatchError, "output hook, found 2"):
            patcher.find_chrome_hdr_output_hook_in_text(
                self.image(hook_offsets=(0x100, 0x200)), self.TEXT_RVA
            )

    def test_wrong_argument_register_is_rejected(self):
        text = self.image()
        text[0x100 - 16] = 0x49
        with self.assertRaisesRegex(patcher.PatchError, "output hook, found 0"):
            patcher.find_chrome_hdr_output_hook_in_text(text, self.TEXT_RVA)

    def test_wrong_call_target_is_rejected(self):
        text = self.image()
        call_offset = 0x100 + len(patcher.HDR_OUTPUT_HOOK_ORIGINAL)
        text[call_offset + 1 : call_offset + 5] = struct.pack("<i", 1)
        with self.assertRaisesRegex(patcher.PatchError, "output hook, found 0"):
            patcher.find_chrome_hdr_output_hook_in_text(text, self.TEXT_RVA)

    def test_missing_or_duplicate_helper_is_rejected(self):
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate):
                text = self.image()
                if duplicate:
                    text[0x650:0x650 + len(patcher.HDR_OUTPUT_HELPER_BYTES)] = (
                        patcher.HDR_OUTPUT_HELPER_BYTES
                    )
                    expected = "output helper, found 2"
                else:
                    text[self.HELPER_OFFSET] ^= 1
                    expected = "output helper, found 0"
                with self.assertRaisesRegex(patcher.PatchError, expected):
                    patcher.find_chrome_hdr_output_hook_in_text(text, self.TEXT_RVA)


if __name__ == "__main__":
    unittest.main()
