import unittest

from pyC import CLoad


lib = CLoad("libcmodule.so", "test/c/module.h")


class TestBasic(unittest.TestCase):
    def test_simple_functions(self):
        self.assertEqual(lib.add(12, 15), 27)
        self.assertEqual(lib.copy_int(9, 90), 90)
        self.assertEqual(lib.concat('Vipul ', 'Cariappa'), "Vipul Cariappa")
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
        self.assertEqual(result_rect.x, 30)
        self.assertEqual(result_rect.y, 36)
        self.assertEqual(result_rectptr.x, 36)
        self.assertEqual(result_rectptr.y, 48)

    def test_simple_functions_datatype(self):
        # simple datatypes
        self.assertEqual(lib.check_short(-3), -3)
        self.assertEqual(lib.check_int(-3), -3)
        self.assertEqual(lib.check_long(3), 3)
        self.assertEqual(lib.check_long_long(3), 3)
        self.assertAlmostEqual(lib.check_float(3.14), 3.14, delta=1e-6)
        self.assertAlmostEqual(lib.check_double(-3.14), -3.14, delta=1e-6)
        self.assertEqual(lib.check_unsigned_short(3), 3)
        self.assertEqual(lib.check_unsigned_int(3), 3)
        self.assertEqual(lib.check_unsigned_long(3), 3)
        self.assertEqual(lib.check_unsigned_long_long(3), 3)
        self.assertEqual(lib.check_char("#"), "#")
        
        # with const
        self.assertEqual(lib.check_const_short(-3), 3)
        self.assertEqual(lib.check_const_int(-3), 3)
        self.assertEqual(lib.check_const_long(3), 3)
        self.assertEqual(lib.check_const_long_long(3), 3)
        self.assertAlmostEqual(lib.check_const_float(3.14), 3.14, delta=1e-6)
        self.assertAlmostEqual(lib.check_const_double(-3.14), 3.14, delta=1e-6)
        self.assertEqual(lib.check_const_unsigned_short(3), 3)
        self.assertEqual(lib.check_const_unsigned_int(3), 3)
        self.assertEqual(lib.check_const_unsigned_long(3), 3)
        self.assertEqual(lib.check_const_unsigned_long_long(3), 3)
        self.assertEqual(lib.check_const_char("#"), "!")

    def test_simple_functions_with_ptr_datatypes(self):
        # simple pointer datatypes
        self.assertEqual(lib.check_short_ptr(-6), -5)
        self.assertEqual(lib.check_int_ptr(6), 7)
        self.assertEqual(lib.check_long_ptr(6), 7)
        self.assertEqual(lib.check_long_long_ptr(-6), -5)
        self.assertAlmostEqual(lib.check_float_ptr(-3.14), -2.14, delta=1e-6)
        self.assertAlmostEqual(lib.check_double_ptr(3.14), 4.14, delta=1e-6)
        self.assertEqual(lib.check_unsigned_short_ptr(6), 7)
        self.assertEqual(lib.check_unsigned_int_ptr(6), 7)
        self.assertEqual(lib.check_unsigned_long_ptr(6), 7)
        self.assertEqual(lib.check_unsigned_long_long_ptr(6), 7)
        self.assertEqual(lib.check_char_ptr("This is Cool"), "!")
        # self.assertEqual(lib.check_void_ptr(None), None)

        # const pointer
        self.assertEqual(lib.check_const_short_ptr(-6), -7)
        self.assertEqual(lib.check_const_int_ptr(-6), -7)
        self.assertEqual(lib.check_const_long_ptr(6), 5)
        self.assertEqual(lib.check_const_long_long_ptr(6), 5)
        self.assertAlmostEqual(lib.check_const_float_ptr(3.14), 2.14, delta=1e-6)
        self.assertAlmostEqual(lib.check_const_double_ptr(-3.14), -4.14, delta=1e-6)
        self.assertEqual(lib.check_const_unsigned_short_ptr(6), 5)
        self.assertEqual(lib.check_const_unsigned_int_ptr(6), 5)
        self.assertEqual(lib.check_const_unsigned_long_ptr(6), 5)
        self.assertEqual(lib.check_const_unsigned_long_long_ptr(6), 5)
        self.assertEqual(lib.check_const_char_ptr("Z"), "Y")
        # self.assertEqual(lib.check_const_void_ptr(None), None)

        # pointer const
        self.assertEqual(lib.check_short_ptr_const(18), -3)
        self.assertEqual(lib.check_int_ptr_const(18), -3)
        self.assertEqual(lib.check_long_ptr_const(18), -3)
        self.assertEqual(lib.check_long_long_ptr_const(-18), -3)
        self.assertAlmostEqual(lib.check_float_ptr_const(3.14), -3.14, delta=1e-6)
        self.assertAlmostEqual(lib.check_double_ptr_const(3.14), -3.14, delta=1e-6)
        self.assertEqual(lib.check_unsigned_short_ptr_const(18), 3)
        self.assertEqual(lib.check_unsigned_int_ptr_const(18), 3)
        self.assertEqual(lib.check_unsigned_long_ptr_const(18), 3)
        self.assertEqual(lib.check_unsigned_long_long_ptr_const(18), 3)
        self.assertEqual(lib.check_char_ptr_const("#"), "!")
        # self.assertEqual(lib.check_void_ptr_const(None), None)

        # const pointer const
        self.assertEqual(lib.check_const_short_ptr_const(-3), -3)
        self.assertEqual(lib.check_const_int_ptr_const(-3), -3)
        self.assertEqual(lib.check_const_long_ptr_const(3), 3)
        self.assertEqual(lib.check_const_long_long_ptr_const(3), 3)
        self.assertAlmostEqual(lib.check_const_float_ptr_const(3.14), 3.14, delta=1e-6)
        self.assertAlmostEqual(lib.check_const_double_ptr_const(-3.14), -3.14, delta=1e-6)
        self.assertEqual(lib.check_const_unsigned_short_ptr_const(3), 3)
        self.assertEqual(lib.check_const_unsigned_int_ptr_const(3), 3)
        self.assertEqual(lib.check_const_unsigned_long_ptr_const(3), 3)
        self.assertEqual(lib.check_const_unsigned_long_long_ptr_const(3), 3)
        self.assertEqual(lib.check_const_char_ptr_const("#"), "#")
        # self.assertEqual(lib.check_const_void_ptr_const(None), None)




if __name__ == "__main__":
    unittest.main()
