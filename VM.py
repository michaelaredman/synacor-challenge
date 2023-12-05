import sys
import logging
from collections import deque

logging.basicConfig(level=logging.ERROR)


class Memory:

    def __init__(self, size):
        self.memory = [0 for _ in range(size)]

    def __setitem__(self, address, value):
        self.memory[address] = value

    def __getitem__(self, address):
        return self.memory[address]


class VM:
    memory = Memory(2**15)
    stack = deque()
    register = [0 for _ in range(8)]

    def __init__(self, program):
        self.define_opcodes_()
        with open(program, 'rb') as f:
            binary = f.read(2)
            i = 0
            while binary:
                self.memory[i] = int.from_bytes(binary, byteorder='little')
                i += 1
                binary = f.read(2)

    def define_opcodes_(self):
        self.op_codes_0 = {
            0: self.halt,
            21: self.noop
        }
        self.op_codes_1 = {
            2: self.push,
            3: self.pop,
            6: self.jmp,
            17: self.call,
            19: self.out
        }
        self.op_codes_2 = {
            1: self.sets,
            7: self.jt,
            8: self.jf,
            14: self.nott,
            15: self.rmem
        }
        self.op_codes_3 = {
            4: self.eq,
            5: self.gt,
            9: self.add,
            10: self.mult,
            11: self.mod,
            12: self.andd,
            13: self.orr
        }

    def __call__(self):
        self.pc = 0  # program counter
        while self.pc < 2**15-1:
            instruction = self.memory[self.pc]
            if instruction in self.op_codes_0:
                self.op_codes_0[instruction]()
            elif instruction in self.op_codes_1:
                self.pc += 1
                a = self.memory[self.pc]
                self.op_codes_1[instruction](a)
            elif instruction in self.op_codes_2:
                self.pc += 1
                a = self.memory[self.pc]
                self.pc += 1
                b = self.memory[self.pc]
                self.op_codes_2[instruction](a, b)
            elif instruction in self.op_codes_3:
                self.pc += 1
                a = self.memory[self.pc]
                self.pc += 1
                b = self.memory[self.pc]
                self.pc += 1
                c = self.memory[self.pc]
                self.op_codes_3[instruction](a, b, c)
            else:
                logging.error(f"Unimplemented: {instruction}")
                self.pc += 1

    def get(self, a):
        if 0 <= a <= 32767:
            return a
        elif 32768 <= a <= 32775:
            return self.register[a - 32768]
        else:
            logging.CRITICAL(f"invalid number: {a}")
            return 0

    def set_reg(self, a, b):
        self.register[a - 32768] = b

    def halt(self):
        logging.warning('Halting!')
        sys.exit(1)

    def sets(self, a, b):
        logging.info(f"Setting register[{a}] = {b}")
        self.set_reg(a, self.get(b))
        self.pc += 1

    def push(self, a):
        logging.info(f"Pushing {self.get(a)}")
        self.stack.append(self.get(a))
        self.pc += 1

    def pop(self, a):
        popped = self.stack.pop()
        logging.info(f"Popping {popped} and writing to {self.get(a)}")
        self.set_reg(a, self.get(popped))
        self.pc += 1

    def eq(self, a, b, c):
        if self.get(b) == self.get(c):
            self.set_reg(a, 1)
        else:
            self.set_reg(a, 0)
        self.pc += 1

    def gt(self, a, b, c):
        if self.get(b) > self.get(c):
            self.set_reg(a, 1)
        else:
            self.set_reg(a, 0)
        self.pc += 1

    def jmp(self, a):
        logging.info(f"Jumping to {a}")
        self.pc = self.get(a)

    def jt(self, a, b):
        if self.get(a):
            logging.info(f"{a} is non-zero, so jumping to {b}")
            self.pc = self.get(b)
        else:
            logging.info(f"Argument is zero, not jumping")
            self.pc += 1

    def jf(self, a, b):
        if self.get(a):
            logging.info(f"{a} is non-zero, not jumping")
            self.pc += 1
        else:
            logging.info(f"Argument is zero, jumping to b")
            self.pc = self.get(b)

    def add(self, a, b, c):
        self.set_reg(a, (self.get(b) + self.get(c)) % 32768)
        self.pc += 1

    def mult(self, a, b, c):
        self.set_reg(a, (self.get(b) * self.get(c)) % 32768)
        self.pc += 1

    def mod(self, a, b, c):
        self.set_reg(a, self.get(b) % self.get(c))
        self.pc += 1

    def andd(self, a, b, c):
        self.set_reg(a, self.get(b) & self.get(c))
        self.pc += 1

    def orr(self, a, b, c):
        logging.info(a, "=", b, " | ", c)
        self.set_reg(a, self.get(b) | self.get(c))
        self.pc += 1

    def nott(self, a, b):
        self.set_reg(a, ~b & 0x7FFF)
        self.pc += 1

    def rmem(self, a, b):
        logging.info("memory[", a, "] = ", b)
        self.memory[a] = self.get(b)
        self.pc += 1

    def call(self, a):
        self.stack.append(self.pc + 1)
        self.pc = self.get(a)

    def out(self, a):
        logging.debug(f'out: {a}')
        print(chr(self.get(a)), end="")
        self.pc += 1

    def noop(self):
        logging.debug('noop')
        self.pc += 1
        pass


vm = VM('challenge.bin')
vm()
