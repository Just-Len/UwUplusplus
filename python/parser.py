from enum import Enum

from tokenizer import *

ExpressionType = Enum("ExpressionType", "Boolean Identifier If Number Nya Operation String")
Operator = Enum("Operator", """And Bang DoubleEquals Equals GreaterEquals Group
                               LessEquals Minus Not Or Plus Slash Star""")

class CustomIterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.peeked = None

    def next(self):
        if self.peeked is not None:
            peeked = self.peeked
            self.peeked = None
            return peeked

        return next(self.iterator, None)

    def peek(self):
        if self.peeked is None:
            self.peeked = next(self.iterator, None) 

        return self.peeked

class Expression:
    def __init__(self, type: ExpressionType, operator: Operator | None = None, \
                 value: str | float | None = None, operands = None):
        self.type = type
        self.operator = operator
        self.value = value
        self.operands = operands

    def create_value(type: ExpressionType, value: str | float | None):
        return Expression(type, value = value)

    def create_nya():
        return Expression(ExpressionType.Nya)

    def create_operation(operator: Operator, operands: list):
        return Expression(ExpressionType.Operation, operator, operands = operands)

class ParserError:
    def __init__(self, message: str):
        self.message = message

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def process(self):
        token_iterator = CustomIterator(iter(self.tokens))
        return self.process_expression(token_iterator, 0)

    def process_expression(self, token_iterator: list[Token], minimum_precedence: int) -> Result[Expression, ParserError]:
        token = token_iterator.next()

        if token is None:
            return parser_error_result("Expected a token.")
        
        match token.kind:
            case TokenKind.Keyword if token.value in value_tokens:
                if token.value == "nya":
                    left_expression = Result(Expression.create_nya())
                else:
                    left_expression = Result(Expression.create_value(ExpressionType.Boolean, token.value))
            case TokenKind.Number:
                left_expression = Result(Expression.create_value(ExpressionType.Number, token.value))
            case TokenKind.String:
                left_expression = Result(Expression.create_value(ExpressionType.String, token.value))
            case TokenKind.LeftParenthesis:
                inner_expression_result = self.process_expression(token_iterator, 0)

                if not inner_expression_result.is_ok():
                    return inner_expression_result

                next_token = token_iterator.next()
                if next_token is None or next_token.kind != TokenKind.RightParenthesis:
                    return parser_error_result('Expected ")" after parenthesized expression.')

                inner_expression = inner_expression_result.value
                left_expression = Result(Expression.create_operation(Operator.Group, [inner_expression]))
            case TokenKind.Bang | TokenKind.Minus | TokenKind.Not:
                operator = Operator[token.kind.name]
                operator_precedence = 10

                inner_expression_result = parse_expression(token_iterator, operator_precedence)
                if not inner_expression_result.is_ok:
                    return inner_expression_result

                inner_expression = inner_expression_result.value
                left_expression = Result(Expression.create_operation(operator, inner_expression))
            case _:
                return parser_error_result("Unexpected token.")

        while True:
            token = token_iterator.peek()
            if token is None:
                break

            match token.kind:
                case TokenKind.Keyword if token.original == "and":
                    operator = Operator.And
                case TokenKind.Keyword if token.original == "or":
                    operator = Operator.Or
                case TokenKind.Keyword if token.original == "not":
                    operator = Operator.Not
                case TokenKind.DoubleEquals | TokenKind.Equals | TokenKind.GreaterEquals | \
                        TokenKind.LessEquals | TokenKind.Minus | TokenKind.Plus | TokenKind.Slash | \
                        TokenKind.Star:
                    operator = Operator[token.kind.name]
                case _:
                    return parser_error_result("Unexpected token.")

            operator_precedence: tuple[int, int] = infix_operator_precedence(operator)
            if operator_precedence is None or operator_precedence[0] < minimum_precedence:
                break

            token_iterator.next()
            right_expression_result = self.process_expression(token_iterator, operator_precedence[1])
            if not right_expression_result.is_ok:
                return right_expression_result

            left_expression = Result(Expression.create_operation(operator, [left_expression.value, right_expression_result.value]))
            continue

        return left_expression

def operator_string(operator: Operator) -> str | None:
    match operator:
        case Operator.And:
            return "and"
        case Operator.Bang:
            return "!"
        case Operator.DoubleEquals:
            return "=="
        case Operator.Equals:
            return "="
        case Operator.GreaterEquals:
            return ">="
        case Operator.Group:
            return "group"
        case Operator.LessEquals:
            return ">="
        case Operator.Minus:
            return "-"
        case Operator.Not:
            return "not"
        case Operator.Or:
            return "or"
        case Operator.Plus:
            return "+"
        case Operator.Slash:
            return "/"
        case Operator.Star:
            return "*"

def expression_string(expression: Expression) -> str:
    match expression.type:
        case ExpressionType.Nya:
            return "nya"
        case ExpressionType.Boolean | ExpressionType.Number | ExpressionType.String:
            return expression.value
        case ExpressionType.Operation:
            return f'({operator_string(expression.operator)} {expression_string(expression.operands[0])} {expression_string(expression.operands[1])})'

def print_expression(expression: Expression):
    print(expression_string(expression))

def infix_operator_precedence(operator: Operator) -> tuple[int, int] | None:
    match operator:
        case Operator.Equals:
            return (2, 1)
        case Operator.DoubleEquals | Operator.GreaterEquals | Operator.LessEquals:
            return (4, 3)
        case Operator.Plus | Operator.Minus:
            return (5, 6)
        case Operator.Slash | Operator.Star:
            return (7, 8)
        case _:
            return None

def parser_error_result(message: str) -> Result[Expression, ParserError]:
    return Result(error = ParserError(message))
