from enum import Enum
import typing

from result import *

class TokenizerError:
    def __init__(self, line_number: int, error_message: str):
        self.line_number    = line_number
        self.error_message  = error_message

TokenKind = Enum("TokenKind", """Bang Minus Plus Slash Star Equals Greater Less BangEquals
                                 DoubleEquals GreaterEquals LessEquals LeftParenthesis
                                 RightParenthesis Keyword Identifier Number String""")

class Token:
    def __init__(self, kind: TokenKind, original: str, value: float | str | None = None):
        self.kind       = kind
        self.original   = original
        self.value      = value

class Tokenizer:
    def __init__(self, input_string):
        self.input_string   = input_string
        self.index          = 0

    def process(self) -> list[Result[Token, TokenizerError]]:
        tokens: list[Result[Token, TokenizerError]] = []
        line_number = 0

        while True:
            input_left      = self.input_string[self.index:]
            input_iterator  = enumerate(input_left, 0)

            current_character_tuple = next(input_iterator, None)
            if current_character_tuple is None:
                break

            current_character = current_character_tuple[1]
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
                case '!':
                    initial_token = InitialToken.ContinuationToken
                    initial_token_kind = TokenKind.Bang
                case '+':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.Plus
                case '*':
                    initial_token = InitialToken.SingleSymbol
                    initial_token_kind = TokenKind.Star
                case '/':
                    next_character_tuple = next(input_iterator, None)
                    if next_character_tuple is not None and next_character_tuple[1] == '/':
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
                    tokens.append(Result(error = TokenizerError(line_number, f'Unexpected character: {current_character}')))
                    self.index += 1
                    continue

            match initial_token:
                case InitialToken.SingleSymbol:
                    tokens.append(Result(value = Token(initial_token_kind, input_left[:1])))
                    self.index += 1
                case InitialToken.ContinuationToken:
                    next_character_tuple = next(input_iterator, None)
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

                    if next_character_tuple is not None and next_character_tuple[1] == "=":
                        tokens.append(Result(Token(continuation_token_kind, input_left[:2])))
                        self.index += 2
                    else:
                        # If there are no more characters or if the character is not the continuation one
                        tokens.append(Result(Token(initial_token_kind, input_left[:1])))
                        self.index += 1

                case InitialToken.Alphabetic:
                    def invalid_character(character_tuple):
                        c = character_tuple[1]
                        return not ((c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or (c >= "0" and c <= "9") or c == "_")

                    identifier_end_index = next(filter(invalid_character, input_iterator), None)
                    identifier_end_index = identifier_end_index[0] if identifier_end_index is not None else len(input_left)
                    word = input_left[:identifier_end_index]
                    
                    match word:
                        case "and" | "else" | "if" | "or" | "print" | "var":
                            tokens.append(Result(Token(TokenKind.Keyword, word)))
                        case "true" | "false" | "nil":
                            tokens.append(Result(Token(TokenKind.Keyword, word, word)))
                        case _: tokens.append(Result(Token(TokenKind.Identifier, word)))

                    self.index += len(word)

                case InitialToken.Digit:
                    end_index = current_index
                    dot_found = False

                    for next_character_tuple in input_iterator:
                        next_character = next_character_tuple[1]
                        if next_character == '.':
                            if dot_found:
                                break

                            dot_found = True
                            end_index += 1
                        elif next_character.isdigit() or next_character == '_':
                            end_index += 1
                        else:
                            break

                    if input_left[end_index] == '.':
                        end_index -= 1

                    number_substring = input_left[:(end_index + 1)]
                    number = parse_number(number_substring)
                    tokens.append(Result(Token(TokenKind.Number, number_substring, number)))
                    self.index += len(number_substring)

                case InitialToken.Quote:
                    closing_quote_index = input_left.find('"', 1)

                    if closing_quote_index != -1:
                        original = input_left[current_index:(closing_quote_index + 1)]
                        value = original[1:-1]
                        tokens.append(Result(Token(TokenKind.String, original, value)))
                        self.index += len(original)
                    else:
                        tokens.append(Result(error = TokenizerError(line_number, "Unterminated string.")))
                        self.index += len(input_left)

        return tokens



def print_tokens(tokens: list[Result[Token, TokenizerError]]):
    for token_result in tokens:
        if not token_result.is_ok:
            error_value = token_result.error
            print(f'[line {error_value.line_number}] Error: {error_value.error_message}')
            continue

        print_token(token_result.value)

def print_token(token: Token):
    token_kind_name = token.kind.name.upper()
    token_value = token.value if token.value is not None else "null"

    print(f'{token_kind_name} {token.original} {token_value}')


def parse_number(string_value: str) -> float | None:
    decimal_places: int = 0
    digit_count:    int = 0
    exponent:       int = 0
    number:         float = 0
    iterator = enumerate(reversed(string_value))

    for number_character_tuple in iterator:
        number_character = number_character_tuple[1]
        if number_character.isdigit():
            if number_character != "0" or decimal_places != 0:
                digit = int(number_character)
                number += digit * pow(10, exponent)

            exponent += 1
        elif number_character == ".":
            decimal_places = digit_count
            continue
        elif number_character == "_":
            continue
        else:
            return None

        digit_count += 1

    number /= pow(10, decimal_places)
    return number
