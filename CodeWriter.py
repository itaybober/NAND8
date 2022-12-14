"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    STATIC_COUNTER = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.cur_static = CodeWriter.STATIC_COUNTER
        self.filename = ""
        self.output_file = output_stream
        self.dict = {"static": str(100 + self.cur_static), "local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT",
                     "temp": "5", "pointer": "3", "heap": "2048"}
        self.jump_var = 0
        self.cur_func = ""

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        input_filename, input_extension = os.path.splitext(os.path.basename(filename))
        self.filename = input_filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command == "add":
            self.output_file.write(self.write_add())
        elif command == "sub":
            self.output_file.write(self.write_sub())
        elif command == "neg":
            self.output_file.write(self.write_neg())
        elif command == "eq":
            self.output_file.write(self.write_eq())
        elif command == "gt":
            self.output_file.write(self.write_gt())
        elif command == "lt":
            self.output_file.write(self.write_lt())
        elif command == "and":
            self.output_file.write(self.write_and())
        elif command == "or":
            self.output_file.write(self.write_or())
        elif command == "not":
            self.output_file.write(self.write_not())

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        output = "// " + command + " " + segment + " " + str(index) + "\n"
        if command == "C_PUSH":
            output += self.push_command(segment, index)
        else:
            output += self.pop_command(segment, index)
        self.output_file.write(output)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        output = "// write label\n"
        if self.cur_func == "":
            output += '(' + label + ')' + "\n"
        else:
            output += "(" + str(self.cur_func) + "$" + label + ')' + "\n"
        self.output_file.write(output)

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        output = "// write goto\n"
        if self.cur_func == "":
            output += '@' + label + "\n"
        else:
            output += "@" + str(self.cur_func) + "$" + label + "\n"
        output += "0;JMP\n"
        self.output_file.write(output)

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        output = "// write if goto\n" \
                 "@SP\n" \
                 "M=M-1\n" \
                 "A=M\n" \
                 "D=M\n"
        if self.cur_func == "":
            output += '@' + label + "\nD;JNE\n"
        else:
            output += "@" + str(self.cur_func) + "$" + label + "\nD;JNE\n"
        self.output_file.write(output)


    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.cur_func = function_name
        output = "// function " + function_name + " " + str(n_vars)
        output += "\n(" + function_name + ")\n" \
                                        "@" + str(n_vars) + "\n" \
                                                            "D=A\n" \
                                                            "@SP\n" \
                                                            "M=M+D\n" \
                                                            "A=M-D\n"
        for i in range(n_vars):
            output += "M=0\n" \
                      "A=A+1\n"
        self.output_file.write(output)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code

        self.jump_var += 1
        # sve return address
        output = "// Call " + function_name + " " + str(n_args)
        output += "\n@RETURN" + str(self.jump_var) + function_name + \
                  "\nD=A\n" \
                  "@SP\n" \
                  "M=M+1\n" \
                  "A=M-1\n" \
                  "M=D\n" + \
                  self.save("LCL") + \
                  self.save("ARG") + \
                  self.save("THIS") + \
                  self.save("THAT") + \
                  "@SP\n" \
                  "D=M\n" \
                  "@LCL\n" \
                  "M=D\n" \
                  "@ARG\n" \
                  "M=D\n"
        for i in range(n_args + 5):
            output += "M=M-1\n"
        output += "@" + function_name + "\n" \
                                        "0;JMP\n" \
                                        "(RETURN" + str(self.jump_var) + function_name + ")\n"
        self.output_file.write(output)

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.jump_var += 1
        output = "// write return " + self.cur_func +  \
                 "\n@LCL\n" \
                 "D=M\n" \
                 "@FRAME" + str(self.jump_var) + "\n" \
                 "M=D\n" \
                 "@5\n" \
                 "D=A\n" \
                 "@FRAME" + str(self.jump_var) + "\n" \
                 "D=M-D\n" \
                 "A=D\n" \
                 "D=M\n" \
                 "@RETADDR" + str(self.jump_var) + "\n" \
                 "M=D\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "D=M\n" \
                 "@ARG\n" \
                 "A=M\n" \
                 "M=D\n" \
                 "D=A+1\n" \
                 "@SP\n" \
                 "M=D\n" \
                 "@FRAME" + str(self.jump_var) + "\n" \
                 "A=M\n" \
                 "A=A-1\n" \
                 "D=M\n" \
                 "@THAT\n" \
                 "M=D\n" \
                "@FRAME" + str(self.jump_var) + "\n" \
                 "A=M\n" \
                 "A=A-1\n" \
                "A=A-1\n" \
                "D=M\n" \
                "@THIS\n" \
                "M=D\n" \
                "@FRAME" + str(self.jump_var) + "\n" \
                 "A=M\n" \
                 "A=A-1\n" \
                "A=A-1\n" \
                "A=A-1\n" \
                "D=M\n" \
                "@ARG\n" \
                "M=D\n" \
                "@FRAME" + str(self.jump_var) + "\n" \
                 "A=M\n" \
                 "A=A-1\n" \
                "A=A-1\n" \
                "A=A-1\n" \
                "A=A-1\n" \
                "D=M\n" \
                "@LCL\n" \
                "M=D\n" \
                "@RETADDR" + str(self.jump_var) + "\n" \
                "A=M\n" \
                "0;JMP\n"
        self.output_file.write(output)



    def write_add(self):
        return "// add\n" \
               "@SP\n" \
               "M=M-1\n" \
               "A=M\n" \
               "D=M\n" \
               "A=A-1\n" \
               "D=D+M\n" \
               "M=D\n"

    # THIS IS A TEST

    def write_sub(self):
        return "// sub\n" \
               "@SP\n" \
               "M=M-1\n" \
               "A=M\n" \
               "D=M\n" \
               "A=A-1\n" \
               "D=M-D\n" \
               "M=D\n"

    def write_neg(self):
        return "//neq\n" \
               "@SP\n" \
               "A=M-1\n" \
               "M=-M\n"

    def write_eq(self):
        self.jump_var += 1
        return "//eq\n" \
               + self.write_sub() \
               + "\n" + \
               "@EQUAL" + str(self.jump_var) + "\n" \
                                               "D;JEQ\n" \
                                               "@SP\n" \
                                               "A=M\n" \
                                               "A=A-1\n" \
                                               "M=0\n" \
                                               "@EQEND" + str(self.jump_var) + "\n" \
                                                                               "0;JMP\n" \
                                                                               "(EQUAL" + str(self.jump_var) + ")\n" \
                                                                                                               "@SP\n" \
                                                                                                               "A=M\n" \
                                                                                                               "A=A-1\n" \
                                                                                                               "M=-1\n" \
                                                                                                               "(EQEND" + str(
            self.jump_var) + ")\n"

    def write_gt(self):
        self.jump_var += 1
        return "//gt\n" \
               + self.write_sub() \
               + "\n" + \
               "@GREATER" + str(self.jump_var) + "\n" \
                                                 "D;JGT\n" \
                                                 "@SP\n" \
                                                 "A=M\n" \
                                                 "A=A-1\n" \
                                                 "M=0\n" \
                                                 "@GREATEREND" + str(self.jump_var) + "\n" \
                                                                                      "0;JMP\n" \
                                                                                      "(GREATER" + str(
            self.jump_var) + ")\n" \
                             "@SP\n" \
                             "A=M\n" \
                             "A=A-1\n" \
                             "M=-1\n" \
                             "(GREATEREND" + str(self.jump_var) + ")\n"

    def write_lt(self):
        self.jump_var += 1
        return "//lt\n" \
               + self.write_sub() \
               + "\n" + \
               "@LESSTHAN" + str(self.jump_var) + "\n" \
                                                  "D;JLT\n" \
                                                  "@SP\n" \
                                                  "A=M\n" \
                                                  "A=A-1\n" \
                                                  "M=0\n" \
                                                  "@LESSTEND" + str(self.jump_var) + "\n" \
                                                                                     "0;JMP\n" \
                                                                                     "(LESSTHAN" + str(
            self.jump_var) + ")\n" \
                             "@SP\n" \
                             "A=M\n" \
                             "A=A-1\n" \
                             "M=-1\n" \
                             "(LESSTEND" + str(self.jump_var) + ")\n"

    def write_and(self):
        self.jump_var += 1
        return "//and\n" \
               "@SP\n" \
               "M=M-1\n" \
               "A=M\n" \
               "D=M\n" \
               "A=A-1\n" \
               "M=D&M\n"

    def write_or(self):
        return "//or\n" + \
               "@SP\n" \
               "M=M-1\n" \
               "A=M\n" \
               "D=M\n" \
               "A=A-1\n" \
               "M=M|D\n"

    def write_not(self):
        return "//not\n" \
               "@SP\n" \
               "A=M-1\n" \
               "M=!M\n" \

    def push_command(self, segment, index):
        output = "@" + str(index) + "\nD=A\n"
        if segment in ["static", "pointer", "temp"]:
            output += "@" + self.dict[segment] + \
                      "\nA=D+A\n" + \
                      "D=M\n"
        elif segment in self.dict:
            output += "@" + self.dict[segment] + "\nA=M\n" + "A=D+A\n" \
                                                             "D=M\n"
        output += "@SP\n" \
                  "A=M\n" \
                  "M=D\n" \
                  "@SP\n" \
                  "M=M+1\n"
        return output

    def pop_command(self, segment, index):
        self.jump_var += 1
        if segment == "constant":
            return "@SP\n" \
                   "M=M-1\n"
        output = "@" + self.dict[segment]
        if segment in ["temp", "static", "pointer"]:
            if segment == "static":
                CodeWriter.STATIC_COUNTER += 1
            output += "\nD=A\n"
        else:
            output += "\nD=M\n"
        output += "@TAR" + str(self.jump_var) + "\n" \
                                                "M=D\n" \
                                                "@" + str(index) + \
                  "\nD=A\n" \
                  "@TAR" + str(self.jump_var) + "\n" \
                                                "M=D+M\n" \
                                                "@SP\n" \
                                                "M=M-1\n" \
                                                "A=M\n" \
                                                "D=M\n" \
                                                "@TAR" + str(self.jump_var) + "\n" \
                                                                              "A=M\n" \
                                                                              "M=D\n"
        return output

    def save(self, segment):
        return "@" + segment + "\n" \
                               "D=M\n" \
                               "@SP\n" \
                               "M=M+1\n" \
                               "A=M-1\n" \
                               "M=D\n"

    def write_init(self):
        output = "@256\n" \
                 "D=A\n" \
                 "@SP\n" \
                 "M=D\n"
        self.output_file.write(output)
        self.write_call("Sys.init",0)
