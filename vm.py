class VirtualMachine:
    def __init__(self, instructions, constants, functions):
        self.instructions = instructions
        self.constants = constants
        self.functions = functions
        self.stack = []
        self.vars = []
        self.ip = 0  # instruction pointer
        self.call_stack = []

    def run(self):
        while self.ip < len(self.instructions):
            instr = self.instructions[self.ip]
            op = instr[0]

            if op == "LOAD_CONST":
                idx = instr[1]
                self.stack.append(self.constants[idx])
            elif op == "LOAD_VAR":
                idx = instr[1]
                self.stack.append(self.vars[idx])
            elif op == "STORE_VAR":
                idx = instr[1]
                val = self.stack.pop()
                # Expand vars if needed
                while len(self.vars) <= idx:
                    self.vars.append(None)
                self.vars[idx] = val
            elif op == "BINARY_ADD":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif op == "BINARY_SUBTRACT":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == "BINARY_MULTIPLY":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == "BINARY_DIVIDE":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)
            elif op == "CALL_FUNCTION":
                fname = instr[1]
                argc = instr[2]
                args = [self.stack.pop() for _ in range(argc)][::-1]

                if fname == "print":  # Built-in function example
                    print(*args)
                    self.stack.append(None)
                else:
                    # Save current state
                    self.call_stack.append((self.ip, self.vars))
                    # Jump to function start
                    self.ip = self.functions[fname]
                    # Setup new locals for function params
                    self.vars = list(args)
                    continue  # Skip ip increment for jump
            elif op == "RETURN_VALUE":
                ret_val = self.stack.pop() if self.stack else None
                if not self.call_stack:
                    # End of program
                    return ret_val
                # Restore caller state
                self.ip, self.vars = self.call_stack.pop()
                self.stack.append(ret_val)
            else:
                raise RuntimeError(f"Unknown instruction {op}")

            self.ip += 1
