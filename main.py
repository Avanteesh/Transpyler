import sys
from os import path, getcwd
from re import search
from transpiler.codetransformer import CodeTransformer, Execution

if __name__ == "__main__":
    if sys.argv[1] == 'run':
        if len(sys.argv) < 3:
            print("InputError: file not provided!")
            sys.exit(-1)
        file = sys.argv[2]
        if search(r"\.rpy$",file) is None:
            print("Invalid file: {file}, must be a '*.rpy' file!")
            sys.exit(-1)
        transform = CodeTransformer(
            path.join(getcwd(),file),Execution.SCRIPT
        )  # execute code as a main script!
        transform()

