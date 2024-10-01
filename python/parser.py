from enum import Enum

from tokenizer import *

ExpressionType = Enum("ExpressionType", "Boolean Identifier If Number Nya Operation String")
Operator = Enum("Operator", """And Bang DoubleEquals Equals Greater GreaterEquals Group
                                           Less LessEquals Minus Not Or Plus Slash Star
                                           Print UnUReversa TwTPotencia owoValorTotal UwUMaximo UnUMinimo
                                           UwUCima UnUSuelo EwEMedia TwTSuma OwOLazo UnUMezcla""")


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
    def __init__(self, type: ExpressionType, operator: Operator | None = None,
                 value: str | float | None = None, operands = None, condition = None, if_body = None, else_body = None):
        self.type = type
        self.operator = operator
        self.value = value
        self.operands = operands
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

    @staticmethod
    def create_value(type: ExpressionType, value: str | float | None):
        return Expression(type, value = value)

    @staticmethod
    def create_if(condition, if_body, else_body):
        return Expression(ExpressionType.If, condition = condition, if_body = if_body, else_body = else_body)

    @staticmethod
    def create_nya():
        return Expression(ExpressionType.Nya)

    @staticmethod
    def create_operation(operator: Operator, operands: list):
        return Expression(ExpressionType.Operation, operator, operands = operands)


class ParserError:
    def __init__(self, message: str):
        self.message = message


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def process(self) -> list[Result[Expression, ParserError]]:
        token_iterator = CustomIterator(iter(self.tokens))
        expressions: list[Result[Expression, ParserError]] = []

        while token_iterator.peek() is not None:
            expressions.append(self.process_expression(token_iterator, 0, False))

        return expressions

    def process_expression(self, token_iterator: CustomIterator, minimum_precedence: int, parenthesized: bool, argument_list = False, block = False) -> Result[Expression, ParserError] | None:
        token = None
        token_kind = None
        while (token := token_iterator.peek()) is not None and token.kind == TokenKind.Eol:
            if not parenthesized and minimum_precedence > 0:
                return parser_error_result("Unexpected end of line in expression.")
            else:
                token_iterator.next()
                token_kind = token.kind

        if token is None:
            if token_kind == TokenKind.Eol:
                token_iterator.next()
                return Result(Expression.create_nya())

            return parser_error_result("Expected a token.")
        elif token.kind == TokenKind.RightBrace:
            if block:
                return Result(Expression.create_nya())
            else:
                token_iterator.next()
                return parser_error_result("Unexpected token.")

        token_iterator.next()
        match token.kind:
            case TokenKind.Keyword if token.value in value_keywords:
                if token.value == "nya":
                    left_expression = Result(Expression.create_nya())
                else:
                    left_expression = Result(Expression.create_value(ExpressionType.Boolean, token.value))

            case TokenKind.Keyword if token.original in built_in_functions:
                arguments: list[Expression] = []

                while (next_token := token_iterator.peek()) is not None and next_token.kind != TokenKind.Eol and next_token.kind != TokenKind.RightParenthesis:
                    argument_expression_result = self.process_expression(token_iterator, 0, parenthesized, True)
                    if not argument_expression_result.is_ok:
                        return argument_expression_result

                    arguments.append(argument_expression_result.value)

                if token.original == PRINT_KEYWORD:
                    operator = Operator.Print
                else:
                    operator = Operator[token.original]

                left_expression = Result(Expression.create_operation(operator, arguments))

            case TokenKind.Keyword if token.original == IF_KEYWORD:
                condition_expression_result = self.process_expression(token_iterator, 0, False)
                if not condition_expression_result.is_ok:
                    return condition_expression_result

                next_token = token_iterator.next()

                if next_token is None or next_token.kind != TokenKind.LeftBrace:
                    return parser_error_result('Expected "{" after "si" condition.')

                if_body: list[Expression] = []
                while (next_token := token_iterator.peek()) is not None and next_token.kind != TokenKind.RightBrace:
                    result = self.process_expression(token_iterator, 0, False, block = True)
                    if not result.is_ok:
                        return result
                    elif result.value.type == ExpressionType.Nya:
                        continue

                    if_body.append(result.value)

                if next_token is None or next_token.kind != TokenKind.RightBrace:
                    return parser_error_result('Expected "}" after "si" expression body.')

                token_iterator.next() # Discard right brace
                else_body: list[Expression] | None = None
                skip_eol(token_iterator)
                next_token = token_iterator.peek()
                if next_token is not None and next_token.kind == TokenKind.Keyword and next_token.original == ELSE_KEYWORD:
                    token_iterator.next() # Discard else keyword
                    next_token = token_iterator.next()
                    if next_token is None or next_token.kind != TokenKind.LeftBrace:
                        return parser_error_result('Expected "{" after "si" condition.')

                    else_body = []
                    while (next_token := token_iterator.peek()) is not None and next_token.kind != TokenKind.RightBrace:
                        result = self.process_expression(token_iterator, 0, False, block = True)
                        if not result.is_ok:
                            return result
                        elif result.value.type == ExpressionType.Nya:
                            continue

                        else_body.append(result.value)

                    next_token = token_iterator.next()
                    if next_token is None or next_token.kind != TokenKind.RightBrace:
                        return parser_error_result('Expected "}" after "sino" expression body.')

                if len(if_body) == 0:
                    if_body.append(Expression.create_nya())
                if else_body is not None and len(else_body) == 0:
                    else_body.append(Expression.create_nya())

                return Result(Expression.create_if(condition_expression_result.value, if_body, else_body))

            case TokenKind.Number:
                left_expression = Result(Expression.create_value(ExpressionType.Number, token.value))

            case TokenKind.String:
                left_expression = Result(Expression.create_value(ExpressionType.String, token.value))

            case TokenKind.Identifier:
                left_expression = Result(Expression.create_value(ExpressionType.Identifier, token.original))

            case TokenKind.LeftParenthesis:
                inner_expression_result = self.process_expression(token_iterator, 0, True, argument_list)

                if not inner_expression_result.is_ok:
                    return inner_expression_result

                next_token = token_iterator.next()
                if next_token is None or next_token.kind != TokenKind.RightParenthesis:
                    return parser_error_result('Expected ")" after parenthesized expression.')

                inner_expression = inner_expression_result.value
                left_expression = Result(Expression.create_operation(Operator.Group, [inner_expression]))

            case TokenKind.Keyword if token.original == NOT_KEYWORD:
                operator_precedence = 10
                inner_expression_result = self.process_expression(token_iterator, operator_precedence, parenthesized, argument_list)
                if not inner_expression_result.is_ok:
                    return inner_expression_result

                inner_expression = inner_expression_result.value
                left_expression = Result(Expression.create_operation(Operator.Not, [inner_expression]))

            case TokenKind.Bang | TokenKind.Minus | TokenKind.Keyword:
                operator = Operator[token.kind.name]
                operator_precedence = 10

                inner_expression_result = self.process_expression(token_iterator, operator_precedence, parenthesized, argument_list)
                if not inner_expression_result.is_ok:
                    return inner_expression_result

                inner_expression = inner_expression_result.value
                left_expression = Result(Expression.create_operation(operator, [inner_expression]))

            case _:
                return parser_error_result("Unexpected token.")

        while True:
            token = token_iterator.peek()
            if token is None:
                break

            match token.kind:
                case TokenKind.Eol:
                    if parenthesized:
                        token_iterator.next()
                        continue
                    else:
                        break
                case TokenKind.LeftBrace | TokenKind.RightParenthesis | TokenKind.RightBrace:
                    break
                case TokenKind.Keyword if token.original == AND_KEYWORD:
                    operator = Operator.And
                case TokenKind.Keyword if token.original == OR_KEYWORD:
                    operator = Operator.Or
                case TokenKind.Keyword if token.original == NOT_KEYWORD:
                    operator = Operator.Not
                case TokenKind.BangEquals | TokenKind.DoubleEquals | TokenKind.Equals | TokenKind.Greater | \
                     TokenKind.GreaterEquals | TokenKind.Less | TokenKind.LessEquals | TokenKind.Minus | TokenKind.Plus | \
                     TokenKind.Slash | TokenKind.Star:
                    operator = Operator[token.kind.name]
                case _:
                    if argument_list:
                        break

                    return parser_error_result("Unexpected token.")

            operator_precedence: tuple[int, int] = infix_operator_precedence(operator)
            if operator_precedence is None or operator_precedence[0] < minimum_precedence:
                break

            token_iterator.next()
            right_expression_result = self.process_expression(token_iterator, operator_precedence[1], parenthesized, argument_list)
            if not right_expression_result.is_ok:
                return right_expression_result

            left_expression = Result(Expression.create_operation(operator, [left_expression.value, right_expression_result.value]))
            continue

        return left_expression


def skip_eol(token_iterator: CustomIterator) -> Token | None:
    while (token := token_iterator.peek()) is not None and token.kind == TokenKind.Eol:
        token_iterator.next()

    return token


def operator_string(operator: Operator) -> str | None:
    match operator:
        case Operator.And:
            return AND_KEYWORD
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
            return NOT_KEYWORD
        case Operator.Or:
            return OR_KEYWORD
        case Operator.Plus:
            return "+"
        case Operator.Slash:
            return "/"
        case Operator.Star:
            return "*"
        case _:
            return operator.name


def expression_string(expression: Expression) -> str:
    match expression.type:
        case ExpressionType.If:
            expression_str = f'(si {expression_string(expression.condition)} {{'

            for body_expression in expression.if_body:
                expression_str += f' {expression_string(body_expression)} .'

            expression_str += ' }'

            if expression.else_body is not None:
                expression_str += f' sino {{'

                for body_expression in expression.if_body:
                    expression_str += f' {expression_string(body_expression)} .'

                expression_str += ' }'

            expression_str += ')'
            return expression_str

        case ExpressionType.Nya:
            return NIL_KEYWORD
        case ExpressionType.Boolean | ExpressionType.Identifier | ExpressionType.Number | ExpressionType.String:
            return expression.value
        case ExpressionType.Operation:
            expression_str = f'({operator_string(expression.operator)}'
            for operand in expression.operands:
                expression_str += f' {expression_string(operand)}'

            expression_str += ")"
            return expression_str


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
