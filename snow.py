# Author: Peter Sovietov
from random import seed, randrange
from asm import *

W, H = 256, 256


def code(a):
    addr = a.addr

    inc = get_1d(a, addr('inc'))
    dec = get_1d(a, addr('dec'))
    eq_0 = get_1d(a, addr('eq_0'))
    set_eq = set_2d(a, addr('eq'))
    eq = get_2d(a, addr('eq'))
    get_counters = get_1d(a, addr('counters'))
    set_counters = set_1d(a, addr('counters'))
    get_xs = get_2d(a, addr('xs'))
    set_xs = set_2d(a, addr('xs'))
    get_random = get_1d(a, addr('random'))
    get_random1 = get_1d(a, addr('random1'))
    get_pixel = get_2d(a, addr('video'))
    set_pixel = set_2d(a, addr('video'))
    get_image = get_2d(a, addr('image'))

    def const(n):
        return addr('const') + (n & 255)

    def addr_to_labs(addr):
        return set(k for k, v in a.labels.items() if v == addr)

    def set_jumps(lab1, lab2, table):
        assert lab1 & 0xffff00 == lab2 & 0xffff00, (
            addr_to_labs(lab1) | addr_to_labs(lab2))
        a.move(const(lab1), table)
        a.move(const(lab2), table + 1)

    def jump_eq_0(x, label, table):
        p = a.here() + CMD_SIZE * 2
        eq_0(x, p + 2)
        a.cmd(table, p + 8, label)

    def jump_eq(x, y, label, table):
        p = a.here() + CMD_SIZE * 3
        eq(x, y, p + 2)
        a.cmd(table, p + 8, label)

    def reset_and_wait(label):
        a.move(const(label >> 8), addr('reset') + 1)
        a.cmd(const(label), addr('reset') + 2, a.here())

    EMPTY = const(0)
    DOT = const(215)

    seed(42)

    a.i16(0)

    a.label('reset')
    a.i24(addr('setup'))
    a.i8(addr('video') >> 16)
    a.i16(0)

    def setup():
        a.label('setup')

        a.move(const(0), addr('i'))
        set_jumps(addr('eq_false'), addr('eq_true'), addr('loop_jumps'))
        a.label('eq_false')
        set_eq(addr('i'), addr('i'), const(1))
        inc(addr('i'), addr('i'))
        jump_eq_0(addr('i'), addr('eq_false'), addr('loop_jumps'))
        a.label('eq_true')

        reset_and_wait(addr('digits'))

    def digits():
        a.label('digits')

        set_jumps(addr('image_false'), addr(
            'image_true'), addr('loop_jumps'))
        set_jumps(addr('page_false'), addr(
            'page_true'), addr('loop2_jumps'))

        a.move(const(addr('image') >> 8), addr('mx'))

        a.cmd(const(12), addr('i'), addr('image_false'))

        a.align(256)
        a.label('image_false')
        dec(addr('i'), addr('i'))

        a.move(const(0), addr('p'))
        a.label('page_false')
        get_image(addr('p'), addr('mx'), addr('x'))
        inc(addr('p'), addr('p'))
        get_image(addr('p'), addr('mx'), addr('y'))
        inc(addr('p'), addr('p'))
        set_pixel(addr('x'), addr('y'), const(0x59))
        jump_eq_0(addr('p'), addr('page_false'), addr('loop2_jumps'))

        a.label('page_true')

        inc(addr('mx'), addr('mx'))
        jump_eq_0(addr('i'), addr('image_false'), addr('loop_jumps'))

        a.label('image_true')

        set_jumps(addr('image2_false'), addr(
            'image2_true'), addr('loop_jumps'))
        set_jumps(addr('page2_false'), addr(
            'page2_true'), addr('loop2_jumps'))

        a.cmd(const(12), addr('i'), addr('image2_false'))

        a.label('image2_false')
        dec(addr('i'), addr('i'))

        a.move(const(0), addr('p'))
        a.label('page2_false')
        get_image(addr('p'), addr('mx'), addr('x'))
        inc(addr('p'), addr('p'))
        get_image(addr('p'), addr('mx'), addr('y'))
        inc(addr('p'), addr('p'))
        set_pixel(addr('x'), addr('y'), const(0x65))
        jump_eq_0(addr('p'), addr('page2_false'), addr('loop2_jumps'))

        a.label('page2_true')

        inc(addr('mx'), addr('mx'))
        jump_eq_0(addr('i'), addr('image2_false'), addr('loop_jumps'))

        a.label('image2_true')

        set_jumps(addr('loop_next'), addr(
            'loop_exit'), addr('loop_jumps'))
        set_jumps(addr('loop2_next'), addr(
            'loop2_exit'), addr('loop2_jumps'))
        set_jumps(addr('random_erase'), addr(
            'random_skip'), addr('random_jumps'))
        set_jumps(addr('check_dot'), addr(
            'check_empty'), addr('check_jumps'))

        reset_and_wait(addr('snow'))

    setup()
    digits()

    a.label('snow')

    get_random(addr('p'), addr('y'))
    get_counters(addr('y'), addr('counters[y]'))
    jump_eq_0(addr('counters[y]'), addr(
        'random_erase'), addr('random_jumps'))

    a.align(256)
    a.label('random_erase')
    dec(addr('counters[y]'), addr('counters[y]'))
    set_counters(addr('y'), addr('counters[y]'))
    get_xs(addr('counters[y]'), addr('y'), addr('x'))
    set_pixel(addr('x'), addr('y'), EMPTY)

    a.label('random_skip')

    set_jumps(addr('random2_erase'), addr(
        'random2_skip'), addr('random_jumps'))

    inc(addr('p'), addr('p'))
    get_random(addr('p'), addr('y'))
    get_counters(addr('y'), addr('counters[y]'))
    jump_eq_0(addr('counters[y]'), addr(
        'random2_erase'), addr('random_jumps'))

    a.align(256)
    a.label('random2_erase')
    dec(addr('counters[y]'), addr('counters[y]'))
    set_counters(addr('y'), addr('counters[y]'))
    get_xs(addr('counters[y]'), addr('y'), addr('x'))
    set_pixel(addr('x'), addr('y'), EMPTY)

    a.label('random2_skip')

    a.move(const(H - 1), addr('y'))

    a.label('loop_next')
    dec(addr('y'), addr('y-1'))
    a.cmd(const(0), addr('i'), addr('loop2_next2'))

    a.label('loop2_exit2')
    a.move(addr('y-1'), addr('y'))
    jump_eq_0(addr('y'), addr('loop_next'), addr('loop_jumps'))

    a.label('loop_exit')
    get_random(addr('p'), addr('xs'))
    set_pixel(addr('xs'), const(0), DOT)
    a.cmd(const(1), addr('counters'), a.here())

    a.align(256)
    a.label('loop2_exit')
    a.jump(addr('loop2_exit2'))

    a.label('loop2_next2')
    get_counters(addr('y-1'), addr('counters[y-1]'))
    jump_eq(addr('i'), addr(
        'counters[y-1]'), addr('loop2_next'), addr('loop2_jumps'))

    a.label('loop2_next')
    get_xs(addr('i'), addr('y-1'), addr('x'))

    get_random1(addr('p'), addr('mx'))
    dec(addr('x'), addr('x-1'))
    eq_0(addr('mx'), a.here() + CMD_SIZE * 2 + 2)
    a.move(addr('x'), addr('mx'))

    get_pixel(addr('mx'), addr('y'), addr('x-1'))
    jump_eq_0(addr('x-1'), addr('check_dot'), addr('check_jumps'))

    a.label('check_dot')
    inc(addr('i'), addr('i'))
    a.org(a.here() - 3)
    a.i24(addr('loop2_next2'))

    a.label('check_empty')
    inc(addr('p'), addr('p'))
    set_pixel(addr('mx'), addr('y'), DOT)
    set_pixel(addr('x'), addr('y-1'), EMPTY)
    get_counters(addr('y'), addr('counters[y]'))
    set_xs(addr('counters[y]'), addr('y'), addr('mx'))

    inc(addr('counters[y]'), addr('counters[y]'))
    set_counters(addr('y'), addr('counters[y]'))
    dec(addr('counters[y-1]'), addr('counters[y-1]'))
    set_counters(addr('y-1'), addr('counters[y-1]'))

    get_xs(addr('counters[y-1]'), addr('y-1'), addr('x'))
    set_xs(addr('i'), addr('y-1'), addr('x'))
    a.org(a.here() - 3)
    a.i24(addr('loop2_next2'))


def data(a):
    a.align(256)
    a.label('const')
    for x in range(256):
        a.i8(x)

    a.align(256)
    a.label('eq_0')
    for x in range(256):
        a.i8(x == 0)

    a.align(256)
    a.label('inc')
    for x in range(256):
        a.i8(x + 1)

    a.align(256)
    a.label('dec')
    for x in range(256):
        a.i8(x - 1)

    a.align(256)
    a.label('random')
    for _ in range(256):
        a.i8(randrange(256))

    a.align(256)
    a.label('random1')
    for _ in range(256):
        a.i8(randrange(2))

    a.align(256)
    a.label('image')
    a.incbin('2025_0x59.bin')
    a.incbin('2025_0x65.bin')

    a.label('end')

    a.label('y')
    a.skip(1)

    a.label('y-1')
    a.skip(1)

    a.label('i')
    a.skip(1)

    a.label('p')
    a.skip(1)

    a.label('counters[y-1]')
    a.skip(1)

    a.label('counters[y]')
    a.skip(1)

    a.label('mx')
    a.skip(1)

    a.align(256)
    a.label('x')
    a.skip(1)
    a.label('x-1')
    a.skip(1)

    a.align(256)
    a.label('loop_jumps')
    a.skip(2)

    a.align(256)
    a.label('loop2_jumps')
    a.skip(2)

    a.align(256)
    a.label('random_jumps')
    a.skip(2)

    a.align(256)
    a.label('check_jumps')
    a.skip(2)

    a.align(256)
    a.label('counters')
    a.skip(256)

    a.align(65536)
    a.label('eq')
    a.skip(65536)

    a.align(65536)
    a.label('xs')
    a.skip(65536)

    a.align(65536)
    a.label('video')


def prog(a):
    code(a)
    data(a)


a = assemble(prog)

with open('snow.bp', 'wb') as f:
    f.write(a.mem[:a.addr('end')])
