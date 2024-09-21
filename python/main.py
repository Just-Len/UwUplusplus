import sys

from tokenizer import *

if __name__ == "__main__":
    command = sys.argv[1]
    filepath = sys.argv[2]
    with open(filepath, "r") as file:
        file_contents = file.read()

    tokenizer = Tokenizer(file_contents)
    tokens = tokenizer.process()
    print_tokens(tokens)
