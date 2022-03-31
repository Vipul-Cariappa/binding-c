from ctypes import CDLL
from ctypes import c_int, c_char, c_char_p, c_float, c_void_p, c_double, POINTER
from ctypes import Structure, Union

import sys
import subprocess as cmd

from pycparser import parse_file, c_ast
from pycparser.c_ast import PtrDecl, TypeDecl


class cASTVisitor(c_ast.NodeVisitor):
    def __init__(self, funcs, structs):
        self.funcs_list = funcs
        self.structs_list = structs
        super().__init__()

    def visit_FuncDecl(self, node):
        args_type = []
        return_type = None
        name = None

        for i in node.args.params:
            if isinstance(i.type, PtrDecl):
                if i.type.type.type.names[0] == "int":
                    args_type.append(POINTER(c_int))
                elif i.type.type.type.names[0] == "double":
                    args_type.append(POINTER(c_double))
                elif i.type.type.type.names[0] == "float":
                    args_type.append(POINTER(c_float))
                elif i.type.type.type.names[0] == "char":
                    args_type.append(c_char_p)

                # logic for struct
                else:
                    for j in self.structs_list:
                        if j.__name__ == i.type.type.type.names[0]:
                            args_type.append(POINTER(j))

            else:
                if i.type.type.names[0] == "int":
                    args_type.append(c_int)
                elif i.type.type.names[0] == "double":
                    args_type.append(c_double)
                elif i.type.type.names[0] == "float":
                    args_type.append(c_float)
                elif i.type.type.names[0] == "char":
                    args_type.append(c_char)

                # logic for struct
                else:
                    for j in self.structs_list:
                        if j.__name__ == i.type.type.names[0]:
                            args_type.append(j)

        if isinstance(node.type, PtrDecl):
            if node.type.type.type.names[0] == "int":
                return_type = POINTER(c_int)
            elif node.type.type.type.names[0] == "double":
                return_type = POINTER(c_double)
            elif node.type.type.type.names[0] == "float":
                return_type = POINTER(c_float)
            elif node.type.type.type.names[0] == "char":
                return_type = c_char_p

            # logic for struct
            else:
                for j in self.structs_list:
                    if j.__name__ == node.type.type.type.names[0]:
                        return_type = POINTER(j)


            name = node.type.type.declname

        else:
            if node.type.type.names[0] == "int":
                return_type = c_int
            elif node.type.type.names[0] == "double":
                return_type = c_double
            elif node.type.type.names[0] == "float":
                return_type = c_float
            elif node.type.type.names[0] == "char":
                return_type = c_char

            # logic for struct
            else:
                for j in self.structs_list:
                    if j.__name__ == node.type.type.names[0]:
                        return_type = j

            name = node.type.declname

        self.funcs_list.append((name, args_type, return_type))

    def visit_Struct(self, node):
        datatypes = []
        if node.decls:
            for i in node.decls:
                name = i.name
                datatype = None
                if isinstance(i.type, PtrDecl):
                    if i.type.type.type.names[0] == "int":
                        datatype = POINTER(c_int)
                    elif i.type.type.type.names[0] == "double":
                        datatype = POINTER(c_double)
                    elif i.type.type.type.names[0] == "float":
                        datatype = POINTER(c_float)
                    elif i.type.type.type.names[0] == "char":
                        datatype = (c_char_p)
                    elif node.name == i.type.type.type.names[0]:
                        datatype = "ptrself"
                    
                    # logic for struct
                    else:
                        # print(i.type.type.type)

                        for j in self.structs_list:
                            if j.__name__ == i.type.type.type.names[0]:
                                datatype = POINTER(j)
                                break
                        

                else:
                    if i.type.type.names[0] == "int":
                        datatype = c_int
                    elif i.type.type.names[0] == "double":
                        datatype = c_double
                    elif i.type.type.names[0] == "float":
                        datatype = c_float
                    elif i.type.type.names[0] == "char":
                        datatype = c_char
                    elif node.name == i.type.type.names[0]:
                        datatype = "self"

                    # logic for struct
                    else:
                        for j in self.structs_list:
                            if j.__name__ == i.type.type.names[0]:
                                datatype = j

                datatypes.append((name, datatype))
            
            self.structs_list.append(type(node.name, (Structure,), {}))
            
            # parsing datatypes
            for i in range(len(datatypes)):
                if datatypes[i][-1] == "self":
                    datatypes[i] = (datatypes[i][0], self.structs_list[-1])
                elif datatypes[i][-1] == "ptrself":
                    datatypes[i] = (datatypes[i][0], POINTER(self.structs_list[-1]))

            # print(datatypes)
            self.structs_list[-1]._fields_ = datatypes


class CFunc:
    def __init__(self, name, func=None, arg_type=[], return_type=None):
        self.name = name
        self.func = func
        self.args_type = arg_type
        self.return_type = return_type

        # initialising function
        self.func.argstype = self.args_type
        self.func.restype = self.return_type
    

    def __call__(self, *args):
        tmp = []
        c_args = []
        for i in range(len(self.args_type)):
            if self.args_type[i] == POINTER(c_int):
                tmp.append(
                    c_int(args[i])
                )
                c_args.append(
                    self.args_type[i](tmp[-1])
                )
            else:
                if type(args[i]) == self.args_type[i]:
                    c_args.append(args[i])
                else:
                    c_args.append(
                        self.args_type[i](args[i])
                    )

        result = self.func(*c_args)

        if not tmp:
            return result
        
        return result, tmp


class CModule:
    def __init__(self, library, header):
        self.library_name = library
        self.header_name = header
        self.library = CDLL(library)
        self.header_ast = parse_file(header)
        self.get_functions()

    def get_functions(self):
        l = []
        k = []
        v = cASTVisitor(l, k)
        v.visit(self.header_ast)
        self.functions = l
        self.structs = k


    def __getattr__(self, name):
        for i in self.functions:
            if i[0] == name:
                return CFunc(
                    name,
                    getattr(self.library, name),
                    i[1],
                    i[2]
                )

        for i in self.structs:
            if i.__name__ == name:
                return i

        raise TypeError(f"Could not find {name} in library")


def CLoad(library, header):
    cmd.Popen(f"gcc -E -std=c99 -I/opt/pycparser/utils/fake_libc_include/ -o {header}.tmp {header}", shell=True).wait()
    return CModule(library, header + ".tmp")


if __name__ == "__main__":
    l = CLoad(sys.argv[1], sys.argv[2])
    print(*(l.functions), sep="\n")
    print(*(l.structs), sep="\n")
    # print(sys.argv)
