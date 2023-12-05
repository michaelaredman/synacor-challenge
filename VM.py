import sys


class Memory:

    def __init__(self, size):
        self.memory = [0 for _ in range(size)]

    def __setitem__(self, address, value):
        self.memory[address] = value

    def __getitem__(self, address):
        return self.memory[address]


class VM:
    memory = Memory(2**15)

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
            19: self.out
        }
        self.op_codes_2 = {
            15: self.rmem
        }
        self.op_codes_3 = {
            13: self.orr
        }

    def __call__(self):
        pc = 0  # program counter
        while pc < 2**15-1:
            instruction = self.memory[pc]
            if instruction in self.op_codes_0:
                self.op_codes_0[instruction]()
            elif instruction in self.op_codes_1:
                pc += 1
                a = self.memory[pc]
                self.op_codes_1[instruction](a)
            elif instruction in self.op_codes_2:
                pc += 1
                a = self.memory[pc]
                pc += 1
                b = self.memory[pc]
                self.op_codes_2[instruction](a, b)
            elif instruction in self.op_codes_3:
                pc += 1
                a = self.memory[pc]
                pc += 1
                b = self.memory[pc]
                pc += 1
                c = self.memory[pc]
                self.op_codes_3[instruction](a, b, c)
            else:
                print("Unimplemented: ", instruction)
            pc += 1

    def halt(self):
        print('Halting!')
        sys.exit(1)

    def orr(self, a, b, c):
        print(a, "=", b, " | ", c)
        self.memory[a] = b | c

    def rmem(self, a, b):
        print("memory[", a, "] = ", b)
        self.memory[a] = b

    def out(self, a):
        print(chr(a), end="")

    def noop(self):
        pass


vm = VM('challenge.bin')
vm()
