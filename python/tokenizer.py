from enum import Enum

from result import *

class TokenizerError:
    def __init__(self, line_number: int, error_message: str):
        self.line_number    = line_number
        self.error_message  = error_message

class TokenKind(Enum):
    Minus               = 1
    Plus                = 2
    Slash               = 3
    Star                = 4
    Equals              = 5
    Greater             = 6
    Less                = 7
    DoubleEquals        = 8
    GreaterEquals       = 9
    LessEquals          = 10
    LeftParenthesis     = 11
    RightParenthesis    = 12
    Identifier          = 13
    Number              = 14
    String              = 15

class Token:
    def __init__(self, kind: TokenKind, original: str, value = None):
        self.kind       = kind
        self.original   = original
        self.value      = value

class Tokenizer:
    def __init__(self, input_string):
        self.input_string   = input_string
        self.index          = 0

    def process() -> list[Result[Token, TokenizerError]]:
        tokens: list[Token] = []
        line_number = 0

        while True:
            input_left      = self.input_string[self.index:]
            input_iterator  = enumerate(input_string)

            current_character = next(input_iterator, None)
            if current_character is not None:
                current_index = 0

            InitialToken = Enum("InitialToken", "Alphabetic ContinuationToken Digit Quote SingleSymbol")

            initial_token: InitialToken
            initial_token_kind: TokenKind

            match current_character:
                case c if c.isdigit():
                    initial_token = InitialToken.Digit
                case c if c.isalpha() or c == "_":
                    initial_token = InitialToken.Alphabetic
                case c if c.isspace():
                    if c == "\n":
                        line_number += 1

                    self.index += 1
                    continue
                case '(':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.LeftParenthesis
                case ')':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.RightParenthesis
                case '-':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.Minus
                case '+':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.Plus
                case '*':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.Star
                case '/':
                    next_character = next(input_iterator, None)
                    if next_character == '/':
                        newline_index = input_left.find("\n")
                        self.index += (newline_index + 1) if newline_index != -1 else len(input_left)
                        line_number += 1
                        continue

                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.Slash
                case '=':
                    initial_token = InitialToken.ContinuationToken
                    initial_token_kind = TokenKind.Equals
                case '>':
                    initial_token = InitialToken.ContinuationToken
                    initial_token_kind = TokenKind.Greater
                case '<':
                    initial_token = InitialToken.ContinuationToken
                    initial_token_kind = TokenKind.Less
                case '"':
                    initial_token = InitialToken.Quote
                case _:
                    tokens.push(Result(error = TokenizerError(line_number, f'Unexpected character: {current_character}')))
                    self.index += 1
                    continue

            match initial_token:
                case InitialToken.SingleSymbol:
                    tokens.push(Result(value = Token(initial_token_kind, input_left[:1])))
                    self.index += 1
                case InitialToken.ContinuationToken:
                    next_character = next(input_iterator, None)
                    continuation_token_kind: TokenKind
                    match initial_token_kind:
                        case TokenKind.Bang:
                            continuation_token_kind = TokenKind.BangEquals
                        case TokenKind.Equals:
                            continuation_token_kind = TokenKind.DoubleEquals
                        case TokenKind.Greater:
                            continuation_token_kind = TokenKind.GreaterEquals
                        case TokenKind.Less:
                            continuation_token_kind = TokenKind.LessEquals

                    if next_character == "=":
                        tokens.push(Result(Token(continuation_token_kind, input_left[:2])))
                        self.index += 2
                    else:
                        # If there are no more characters or if the character is not the continuation one
                        tokens.push(Result(Token(initial_token_kind, input_left[:1])))
                        self.index += 1

                    break


def print_tokens(tokens: list[Token]):
    for token in tokens:
        print_token(token)

def print_token(token: Token):
    pass

def parse_number(string_value: str) -> int:
    pass
