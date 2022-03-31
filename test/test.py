from binding import CLoad


lib = CLoad("libcmodule.so", "test/module.h")


assert lib.add(12, 15) == 27
assert lib.copy_int(9, 90)[0] == 90
assert lib.concat(b'Vipul ', b'Cariappa') == b"Vipul Cariappa"
assert lib.pi(400) == 3.1390926574960143

rectptr_1 = lib.get_rect(12, 16)
rectptr_2 = lib.get_rect(24, 32)

rect1 = lib.RECT(10, 12)
rect2 = lib.RECT(20, 24)

result_rect = lib.rect_add(rect1, rect2)
result_rectptr = lib.rect_add(rectptr_1, rectptr_2)

assert result_rect.contents.x == 30
assert result_rect.contents.y == 36
assert result_rectptr.contents.x == 36
assert result_rectptr.contents.y == 48
