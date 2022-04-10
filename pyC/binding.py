from ast import arg
import _ctypes
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
    c_bool,
    c_char_p,
    c_double,
    c_float,
    c_longdouble,
    c_void_p,
    POINTER,
    pointer
)

import os
import sys
import subprocess as cmd

from pycparser import parse_file, c_ast
from pycparser.c_ast import PtrDecl, TypeDecl, EllipsisParam, Struct, Enum, ArrayDecl, FuncDecl


def ptr_converter(c_ptr_type): return lambda data: c_ptr_type(
    c_ptr_type._type_(data))


class cASTVisitor(c_ast.NodeVisitor):
    def __init__(self, funcs, structs, typedef):
        self.funcs_list = funcs
        self.structs_list = structs
        self.typedefs = typedef
        super().__init__()

    def change_datatype(self, node):
        if isinstance(node.type, PtrDecl):
            # TODO: add support for pointer of pointer
            if isinstance(node.type.type, PtrDecl):
                return c_void_p

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
            elif datatype_name == ["short"] or datatype_name == ["signed", "short"]:
                return POINTER(c_short)
            elif datatype_name == ["unsigned", "short"]:
                return POINTER(c_ushort)
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
            elif datatype_name == ["short"] or datatype_name == ["signed", "short"]:
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
            elif datatype_name[-1] == "bool":
                return c_bool
            elif datatype_name == ["void"]:
                return None

        if isinstance(node.type, ArrayDecl):
            array_len = int(node.type.dim.value)
            if (t := self.change_datatype(node.type)) != Structure:
                return t * array_len

            # TODO: implement proper array of pointer to struct of typedef
            if isinstance(node.type.type, PtrDecl):
                return c_void_p * array_len

            for i in self.structs_list:
                if i.__name__ == node.type.type.type.names[0]:
                    return i * array_len

            for i in self.typedefs:
                if i[0] == node.type.type.type.names[0]:
                    return i[1] * array_len

        return Structure

    def visit_FuncDecl(self, node):
        args_type = []
        return_type = None
        name = None

        # Paser Arguments Type
        for i in node.args.params:
            # TODO: add support for variable number of argument
            if not isinstance(i, EllipsisParam):
                if (t := self.change_datatype(i)) != Structure:
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
        function_returns_ptr_of_ptr = isinstance(node.type.type, PtrDecl)
        if (t := self.change_datatype(node)) != Structure:
            return_type = t

        # logic for struct
        else:
            for j in self.structs_list:
                if function_returns_ptr_of_ptr:
                    if j.__name__ == node.type.type.type.type.names[0]:
                        return_type = POINTER(j)
                elif function_returns_ptr:
                    if j.__name__ == node.type.type.type.names[0]:
                        return_type = POINTER(j)
                else:
                    if j.__name__ == node.type.type.names[0]:
                        return_type = j

        if function_returns_ptr_of_ptr:
            name = node.type.type.type.declname
        elif function_returns_ptr:
            name = node.type.type.declname
        else:
            name = node.type.declname

        # print((name, args_type, return_type))
        self.funcs_list.append((name, args_type, return_type))

    def visit_Typedef(self, node):
        # TODO: datatype convertions
        # TODO: function pointers
        if isinstance(node.type.type, Struct):
            self.visit_Struct(node.type.type)
        elif isinstance(node.type.type, Enum):
            pass
        elif isinstance(node.type.type, FuncDecl):
            pass
        else:
            if (t := self.change_datatype(node)) == Structure:
                for i in self.structs_list:
                    if i.__name__ == node.type.type.names[0]:
                        self.typedefs.append((node.name, i))
                        break
                else:
                    for i in self.typedefs:
                        if i[0] == node.type.type.names[0]:
                            self.typedefs.append((node.name, i[1]))
                            break
                    else:
                        ...
            else:
                self.typedefs.append((node.name, self.change_datatype(node)))

    def visit_Struct(self, node):
        datatypes = []
        if node.decls:
            for i in node.decls:
                name = i.name
                datatype = None
                if (t := self.change_datatype(i)) != Structure:
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
                                for j in i.type.type.type.names:
                                    if "atomic" in j:
                                        return
                                else:
                                    for j in self.typedefs:
                                        if j[0] == i.type.type.type.names[0]:
                                            if j[1] != Structure:
                                                datatype = POINTER(j[1])
                                            else:
                                                datatype = c_void_p
                                            break
                                    else:
                                        raise TypeError(
                                            f"Could Not determine the type of {i.type.type.type.names}"
                                        )

                    else:
                        if node.name == i.type.type.names[0]:
                            datatype = "self"

                        else:
                            for j in self.structs_list:
                                if j.__name__ == i.type.type.names[0]:
                                    datatype = j
                                    break
                            else:
                                for j in i.type.type.names:
                                    if "atomic" in j:
                                        return
                                else:
                                    for j in self.typedefs:
                                        if j[0] == i.type.type.names[0]:
                                            datatype = j[1]
                                            break
                                    else:
                                        raise TypeError(
                                            f"Could Not determine the type of {i.type.type.names}")

                datatypes.append((name, datatype))

            self.structs_list.append(type(node.name, (Structure,), {}))

            # parsing self refering datatypes
            for i in range(len(datatypes)):
                if datatypes[i][-1] == "self":
                    datatypes[i] = (datatypes[i][0], self.structs_list[-1])
                elif datatypes[i][-1] == "ptrself":
                    datatypes[i] = (datatypes[i][0], POINTER(
                        self.structs_list[-1]))

            self.structs_list[-1]._fields_ = datatypes

        else:
            self.typedefs.append((node.name, Structure))


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
        c_args = []

        # TODO: handle convertion of arrays / pointer to arrays
        for i in range(len(self.args_type)):
            if self.args_type[i] == None:
                c_args.append(None)
            elif type(args[i]) == self.args_type[i]:
                c_args.append(args[i])
            elif _ctypes.Structure in self.args_type[i].__bases__:  # Structure
                c_args.append(
                    self.args_type[i](args[i])
                )
            elif _ctypes._Pointer in self.args_type[i].__bases__:  # pointer
                # Structure Pointer
                if _ctypes.Structure in self.args_type[i]._type_.__bases__:
                    # TODO: if arg is not Structure already
                    c_args.append(
                        pointer(args[i])
                    )
                else:   # normal pointer
                    c_args.append(
                        self.args_type[i](
                            self.args_type[i]._type_(args[i])
                        )
                    )
            else:
                c_args.append(
                    self.args_type[i](args[i])
                )

        return self.func(*c_args)


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
        m = []
        v = cASTVisitor(l, k, m)
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
        cmd.Popen(
            f"gcc -E -std=c99 -I/opt/pycparser/utils/fake_libc_include/ -o {header}.tmp {header}", shell=True).wait()
        return CModule(library, header + ".tmp")
    if os.name == "nt":
        return CModule(library, header)


if __name__ == "__main__":
    l = CLoad(sys.argv[1], sys.argv[2])
    print(*(l.functions), sep="\n")
    print(*(l.structs), sep="\n")
    # print(sys.argv)
