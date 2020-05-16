"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.stack_pointer = 7
        self.E = 0  # equals flag
        self.L = 0  # less than flag
        self.G = 0  # greater than flag
        self.command = {
            "HLT":  0b00000001,
            "PRN":  0b01000111,
            "LDI":  0b10000010,
            "MUL":  0b10100010,
            "ADD":  0b10100000,
            "PUSH": 0b01000101,
            "POP":  0b01000110,
            "SUB":  0b10100001,
            "DIV":  0b10100011,
            "JMP":  0b01010100,
            "JEQ":  0b01010101,
            "JNE":  0b01010110,
            "CALL": 0b01010000,
            "RET":  0b00010001,
            "CMP":  0b10100111,
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("Need proper file name passed!")
            sys.exit(1)

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]
        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                split_line = line.split("#")
                num = split_line[0].strip()
                if num == '':
                    continue
                print(num)

                self.ram[address] = int(num, 2)
                address += 1

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == "SUB":
            self.register[reg_a] -= self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "DIV":
            self.register[reg_a] /= self.register[reg_b]
        elif op == "CMP":
            if self.register[reg_a] == self.register[reg_b]:
                self.E == 1
            elif self.register[reg_a] < self.register[reg_b]:
                self.L == 1
            elif self.register[reg_a] > self.register[reg_b]:
                self.G == 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            command = self.ram[self.pc]

            if command == self.command["HLT"]:
                running = False
                self.pc += 1
            elif command == self.command["PRN"]:
                num = self.ram[self.pc+1]
                print(num)
                self.pc += 2
            elif command == "LDI":
                val1 = self.ram[self.pc + 1]
                val2 = self.ram[self.pc + 2]
                self.register[val1] = val2
                self.pc += 3

            elif command == self.command["MUL"]:
                val1 = self.ram[self.pc + 1]
                val2 = self.ram[self.pc + 2]

                self.alu('MUL', val1, val2)
                self.pc += 3
            elif command == self.command["ADD"]:
                val1 = self.ram[self.pc + 1]
                val2 = self.ram[self.pc + 2]

                self.alu('ADD', val1, val2)
                self.pc += 3

            elif command == self.command["PUSH"]:
                val1 = self.ram[self.pc + 1]
                value = self.register[val1]
                self.stack_pointer -= 1

                self.ram[self.stack_pointer] = value
                self.pc += 2

            elif command == self.command["POP"]:
                val1 = self.ram[self.pc + 1]
                value = self.ram[self.stack_pointer]

                self.register[val1] = value
                self.stack_pointer += 1
                self.pc += 2

            elif command == self.command["CMP"]:
                val1 = self.ram[self.pc + 1]
                val2 = self.ram[self.pc + 2]

                self.alu("CMP", val1, val2)
                self.pc += 3

            elif command == self.command["JMP"]:
                val1 = self.ram[self.pc + 1]
                self.pc = self.register[val1]

            elif command == self.command["JEQ"]:
                if self.E == 1:
                    val1 = self.ram[self.pc + 1]
                    self.pc = self.register[val1]
                else:
                    self.pc += 2

            elif command == self.command["JNE"]:
                if self.E == 0:
                    val1 = self.ram[self.pc + 1]
                    self.pc = self.register[val1]
                else:
                    self.pc += 2

            elif command == self.command["CALL"]:
                reg1 = self.register[self.ram[self.pc + 1]]
                self.stack_pointer -= 1
                self.ram[self.stack_pointer] = self.pc + 2
                self.pc = reg1

            elif command == self.command["RET"]:
                address = self.ram[self.stack_pointer]
                self.ram[self.stack_pointer] += 1
                self.pc = address

            else:
                print(f"Unknown instruction {command}")
                sys.exit(1)

    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, index, value):
        self.ram[index] = value

# CMP, instruction with an equal flag?
# JMP, instruction
# JEQ, JNE instructions
