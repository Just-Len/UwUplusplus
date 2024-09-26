import sys

from evaluator import Evaluator
from parser import *
from tokenizer import *

def read_file(filepath: str) -> str:
    try:
        file = open(filepath)
    except FileNotFoundError:
        print(f'Error while opening {filepath}')
        sys.exit(1)
    else:
        with file:
            return file.read()


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

    file_contents = read_file(filepath)
    match command:
        case "tokenize":
            tokenizer = Tokenizer(file_contents)
            tokens = tokenizer.process()
            print_tokens(tokens)
            return 0
        case "parse":
            tokenizer = Tokenizer(file_contents)
            tokens = tokenizer.process()
            tokens = map(lambda t: t.value, tokens)

            parser = Parser(tokens)
            expression_results = parser.process()

            for result in expression_results:
                if result.is_ok:
                    print_expression(result.value)
                else:
                    print(result.error.message)
            return 0
        case "evaluate":
            tokenizer = Tokenizer(file_contents)
            tokens = tokenizer.process()
            tokens = map(lambda t: t.value, tokens)

            parser = Parser(tokens)
            expression_results = parser.process()
            expressions = map(lambda e: e.value, expression_results)

            evaluator = Evaluator(expressions)
            evaluator.process()
        case _:
            print("Unrecognized command.")
            return 1


if __name__ == "__main__":
    result_value = main()
    sys.exit(result_value)
