import unittest

from pyC import CLoad


lib = CLoad("libcmodule.so", "test/c/module.h")


class TestBasic(unittest.TestCase):
    def test_simple_functions(self):
        self.assertEqual(lib.add(12, 15), 27)
        self.assertEqual(lib.copy_int(9, 90), 90)
        self.assertEqual(lib.concat(b'Vipul ', b'Cariappa'), b"Vipul Cariappa")
        self.assertEqual(lib.pi(400), 3.1390926574960143)

    def test_structs_creations(self):
        # creating structs from c function
        rectptr_1 = lib.get_rect(12, 16)
        rectptr_2 = lib.get_rect(24, 32)

        # direct creation of structs
        rect1 = lib.RECT(10, 12)
        rect2 = lib.RECT(20, 24)

        # function with structs
        result_rect = lib.rect_add(rect1, rect2)
        result_rectptr = lib.rect_add(rectptr_1, rectptr_2)

        # testing
        self.assertEqual(result_rect.contents.x, 30)
        self.assertEqual(result_rect.contents.y, 36)
        self.assertEqual(result_rectptr.contents.x, 36)
        self.assertEqual(result_rectptr.contents.y, 48)


if __name__ == "__main__":
    unittest.main()
