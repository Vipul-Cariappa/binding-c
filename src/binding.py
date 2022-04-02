from ctypes import CDLL
from ctypes import Structure, Union
from ctypes import (
    c_int,
    c_uint,
    c_long,
    c_ulong, 
    c_longlong,
    c_ulonglong,
    c_short, 
    c_ushort,
    c_char,
    c_char_p, 
    c_double, 
    c_float, 
    c_longdouble,
    c_void_p, 
    POINTER
)

import os
import sys
import subprocess as cmd

from pycparser import parse_file, c_ast
from pycparser.c_ast import PtrDecl, TypeDecl


def change_datatype(node):
    if isinstance(node.type, PtrDecl):
        datatype_name = node.type.type.type.names
        if datatype_name == ["int"] or datatype_name == ["signed", "int"]:
            return POINTER(c_int)
        elif datatype_name == ["unsigned", "int"]:
            return POINTER(c_uint)
        elif datatype_name == ["long"] or datatype_name == ["long", "int"] or datatype_name == ["signed", "long"] or datatype_name == ["signed", "long", "long"]:
            return POINTER(c_long)
        elif datatype_name == ["unsigned", "long"] or datatype_name == ["unsigned", "long", "long"]:
            return POINTER(c_ulong)
        elif datatype_name == ["long", "long"] or datatype_name == ["long", "long", "int"] or datatype_name == ["signed", "long", "long"] or datatype_name == ["signed", "long", "long", "int"]:
            return POINTER(c_longlong)
        elif datatype_name == ["unsigned", "long", "long"] or datatype_name == ["unsigned", "long", "long", "int"]:
            return POINTER(c_ulonglong)
        elif datatype_name == ["short"]  or datatype_name == ["signed", "short"]:
            return POINTER(c_short)
        elif datatype_name == ["unsigned", "short"]:
            return POINTER(c_ushort)
        elif datatype_name == ["char"]:
            return POINTER(c_char)
        elif datatype_name == ["double"]:
            return POINTER(c_double)
        elif datatype_name == ["float"]:
            return POINTER(c_float)
        elif datatype_name == ["long", "double"]:
            return POINTER(c_longdouble)
        elif datatype_name[-1] == "char":
            return c_char_p
        elif datatype_name == ["void"]:
            return c_void_p
    
    if isinstance(node.type, TypeDecl):
        datatype_name = node.type.type.names
        if datatype_name == ["int"] or datatype_name == ["signed", "int"]:
            return c_int
        elif datatype_name == ["unsigned", "int"]:
            return c_uint
        elif datatype_name == ["long"] or datatype_name == ["long", "int"] or datatype_name == ["signed", "long"] or datatype_name == ["signed", "long", "long"]:
            return c_long
        elif datatype_name == ["unsigned", "long"] or datatype_name == ["unsigned", "long", "long"]:
            return c_ulong
        elif datatype_name == ["long", "long"] or datatype_name == ["long", "long", "int"] or datatype_name == ["signed", "long", "long"] or datatype_name == ["signed", "long", "long", "int"]:
            return c_longlong
        elif datatype_name == ["unsigned", "long", "long"] or datatype_name == ["unsigned", "long", "long", "int"]:
            return c_ulonglong
        elif datatype_name == ["short"]  or datatype_name == ["signed", "short"]:
            return c_short
        elif datatype_name == ["unsigned", "short"]:
            return c_ushort
        elif datatype_name == ["char"]:
            return c_char
        elif datatype_name == ["double"]:
            return c_double
        elif datatype_name == ["float"]:
            return c_float
        elif datatype_name == ["long", "double"]:
            return c_longdouble
        elif datatype_name[-1] == "char":
            return c_char
        elif datatype_name == ["void"]:
            return None

    return Structure


class cASTVisitor(c_ast.NodeVisitor):
    def __init__(self, funcs, structs):
        self.funcs_list = funcs
        self.structs_list = structs
        super().__init__()

    def visit_FuncDecl(self, node):
        args_type = []
        return_type = None
        name = None

        # Paser Arguments Type
        for i in node.args.params:
            if (t := change_datatype(i)) != Structure:
                args_type.append(t)

            # logic for struct
            else:
                for j in self.structs_list:
                    if isinstance(i.type, PtrDecl):
                        if j.__name__ == i.type.type.type.names[0]:
                            args_type.append(POINTER(j))
                    else:
                        if j.__name__ == i.type.type.names[0]:
                            args_type.append(j)


        # Paser Return Type
        function_returns_ptr = isinstance(node.type, PtrDecl)
        if (t := change_datatype(node)) != Structure:
                return_type = t

        # logic for struct
        else:
            for j in self.structs_list:
                if function_returns_ptr:
                    if j.__name__ == node.type.type.type.names[0]:
                        return_type = POINTER(j)
                else:
                    if j.__name__ == node.type.type.names[0]:
                        return_type = j
        

        if function_returns_ptr:
            name = node.type.type.declname
        else:
            name = node.type.declname

        # print((name, args_type, return_type))
        self.funcs_list.append((name, args_type, return_type))
        

    def visit_Struct(self, node):
        datatypes = []
        if node.decls:
            for i in node.decls:
                name = i.name
                datatype = None
                if (t := change_datatype(i)) != Structure:
                    datatype = t
                
                # logic for struct
                else:
                    if isinstance(i.type, PtrDecl):
                        if node.name == i.type.type.type.names[0]:
                            datatype = "ptrself"

                        else:
                            for j in self.structs_list:
                                if j.__name__ == i.type.type.type.names[0]:
                                    datatype = POINTER(j)
                                    break
                            else:
                                raise TypeError(f"Could Not determine the type of {i.type.type.type.names}")
                        

                    else:
                        if node.name == i.type.type.names[0]:
                            datatype = "self"

                        else:
                            for j in self.structs_list:
                                if j.__name__ == i.type.type.names[0]:
                                    datatype = j
                            else:
                                raise TypeError(f"Could Not determine the type of {i.type.type.names}")

                datatypes.append((name, datatype))
            
            self.structs_list.append(type(node.name, (Structure,), {}))
            
            # parsing self refering datatypes
            for i in range(len(datatypes)):
                if datatypes[i][-1] == "self":
                    datatypes[i] = (datatypes[i][0], self.structs_list[-1])
                elif datatypes[i][-1] == "ptrself":
                    datatypes[i] = (datatypes[i][0], POINTER(self.structs_list[-1]))

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
            if self.args_type[i] == None:
                c_args.append(None)
            elif self.args_type[i] == POINTER(c_int):
                tmp.append(
                    c_int(args[i])
                )
                c_args.append(
                    self.args_type[i](tmp[-1])
                )
            elif self.args_type[i] == POINTER(c_char):
                c_args.append(
                    args[i]
                )

            elif type(args[i]) == self.args_type[i]:
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
        self.get_symbols()


    def get_symbols(self):
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
    if os.name == "posix":
        cmd.Popen(f"gcc -E -std=c99 -I/opt/pycparser/utils/fake_libc_include/ -o {header}.tmp {header}", shell=True).wait()
        return CModule(library, header + ".tmp")
    if os.name == "nt":
        return CModule(library, header)


if __name__ == "__main__":
    l = CLoad(sys.argv[1], sys.argv[2])
    print(*(l.functions), sep="\n")
    print(*(l.structs), sep="\n")
    # print(sys.argv)
