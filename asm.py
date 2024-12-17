# Author: Peter Sovietov
MEM_SIZE = 2**24
CMD_SIZE = 9


class Asm:
    def __init__(self):
        self.mem = bytearray(MEM_SIZE)
        self.pc = 0
        self.labels = {}
        self.used = set()

    def here(self):
        return self.pc

    def org(self, addr):
        self.pc = addr

    def align(self, size):
        self.pc = ((self.pc + size - 1) // size) * size

    def skip(self, size):
        self.pc += size

    def label(self, name):
        self.labels[name] = self.pc

    def addr(self, name):
        self.used.add(name)
        return self.labels.get(name, 0)

    def write(self, data):
        self.mem[self.pc:self.pc + len(data)] = data
        self.pc += len(data)

    def incbin(self, filename):
        with open(filename, 'rb') as f:
            self.write(f.read())

    def i8(self, x):
        self.write([x & 255])

    def i16(self, x):
        self.write(x.to_bytes(2, 'big'))

    def i24(self, x):
        self.write(x.to_bytes(3, 'big'))

    def cmd(self, a, b, c):
        self.i24(a)
        self.i24(b)
        self.i24(c)

    def move(self, a, b):
        self.cmd(a, b, self.pc + CMD_SIZE)

    def jump(self, c):
        self.cmd(0, 0, c)


def get_1d(a, table):
    def func(x, r):
        a.move(x, a.pc + CMD_SIZE + 2)
        a.move(table, r)
    return func


def set_1d(a, table):
    def func(x, r):
        a.move(x, a.pc + CMD_SIZE + 3 + 2)
        a.move(r, table)
    return func


def get_2d(a, table):
    def func(x, y, r):
        p = a.pc + CMD_SIZE * 2
        a.move(y, p + 1)
        a.move(x, p + 2)
        a.move(table, r)
    return func


def set_2d(a, table):
    def func(x, y, r):
        p = a.pc + CMD_SIZE * 2
        a.move(y, p + 3 + 1)
        a.move(x, p + 3 + 2)
        a.move(r, table)
    return func


def assemble(prog):
    a = Asm()
    prog(a)
    prog(a)
    for u in a.used:
        assert u in a.labels, u
    return a


def get3(mem, i):
    return mem[i] << 16 | mem[i + 1] << 8 | mem[i + 2]


def sim(mem, cycles):
    pc = get3(mem, 2)
    for _ in range(cycles):
        a, b = get3(mem, pc), get3(mem, pc + 3)
        mem[b] = mem[a]
        pc = get3(mem, pc + 6)
