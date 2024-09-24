import sys

from parser import *
from tokenizer import *

def main():
    iterator = iter(sys.argv)
    next(iterator)
    command = next(iterator, None)
    filepath = next(iterator, None)

    if command is None:
        print("Must provide one of two commands: tokenize, parse.")
        return 1

    if filepath is None:
        print("Must provide path to source file.")
        return 1

    match command:
        case "tokenize":
            with open(filepath, "r") as file:
                file_contents = file.read()

            tokenizer = Tokenizer(file_contents)
            tokens = tokenizer.process()
            print_tokens(tokens)
            return 0
        case "parse":
            with open(filepath, "r") as file:
                file_contents = file.read()

            tokenizer = Tokenizer(file_contents)
            tokens = tokenizer.process()
            tokens = map(lambda t: t.value, tokens)

            parser = Parser(tokens)
            result = parser.process()
            print_expression(result.value)
            return 0
        case _:
            print("Unrecognized command.")
            return 1


if __name__ == "__main__":
    result_value = main()
    sys.exit(result_value)
