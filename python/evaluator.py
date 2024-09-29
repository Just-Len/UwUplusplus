import operator as python_operator

from parser import *
from result import *

Nya = object()

ValueType = Enum("ValueType", "Boolean Number Nya String")


class ValueData:
    def __init__(self, value, type: ValueType):
        self.value = value
        self.type = type

    @staticmethod
    def boolean_value(value):
        return ValueData(value, ValueType.Boolean)

    @staticmethod
    def number_value(value):
        return ValueData(value, ValueType.Number)

    @staticmethod
    def nya_value():
        return ValueData(Nya, ValueType.Nya)

    @staticmethod
    def string_value(value):
        return ValueData(value, ValueType.String)


class EvaluatorError:
    def __init__(self, message: str):
        self.message = message

class Evaluator:
    def __init__(self, expressions: list[Expression]):
        self.expressions = expressions
        self.variables: dict[str, ValueData] = {}

    def process(self):
        for expression in self.expressions:
            result = self.process_expression(expression)
            if not result.is_ok:
                print(f'FATAL ERROR: {result.error.message}')
                return

    def process_expression(self, expression: Expression) -> Result[ValueData, EvaluatorError]:
        result: Result[ValueData, EvaluatorError] = None
        match expression.type:
            case ExpressionType.Nya:
                result = Result(ValueData.nya_value())

            case ExpressionType.Boolean | ExpressionType.Number | ExpressionType.String:
                result = Result(ValueData(expression.value, ValueType[expression.type.name]))

            case ExpressionType.Identifier:
                value = self.variables.get(expression.value, None)
                if value is None:
                    return evaluator_error_result(f'Variable {expression.value} is not defined.')

                result = Result(value)

            case ExpressionType.Operation:
                match expression.operator:
                    case Operator.Group:
                        result = self.process_expression(expression.operands[0])

                    case Operator.Print:
                        self.process_print(expression)
                        result = Result(ValueData.nya_value())

                    case Operator.Equals:
                        result = self.process_assignment(expression)

                    case Operator.Minus:
                        result = self.process_binary_operation(expression, python_operator.sub)

                    case Operator.Plus:
                        result = self.process_binary_operation(expression, python_operator.add)

                    case Operator.Slash:
                        result = self.process_binary_operation(expression, python_operator.truediv)

                    case Operator.Star:
                        result = self.process_binary_operation(expression, python_operator.mul)

                    case Operator.And:
                        result = self.process_binary_operation(expression, python_operator.and_)

                    case Operator.Or:
                        result = self.process_binary_operation(expression, python_operator.or_)

                    case Operator.Not:
                        result = self.process_binary_operation(expression, python_operator.not_)

                    case Operator.UnUReversa:
                        result = self.process_reverse_operation(expression)

                    case Operator.TwTPotencia:
                        pass

        return result

    def process_assignment(self, expression: Expression) -> Result[ValueData, EvaluatorError]:
        identifier_expression = expression.operands[0]
        if identifier_expression.type != ExpressionType.Identifier:
            return evaluator_error_result("Expected identifier for the left hand side of assignment expression.")

        value_expression = expression.operands[1]
        actual_value_result = self.process_expression(value_expression)
        if not actual_value_result.is_ok:
            return actual_value_result

        variable_name = expression.operands[0].value
        value_data = actual_value_result.value

        self.variables[variable_name] = value_data
        return actual_value_result

    def process_binary_operation(self, expression: Expression, operator) -> Result[ValueData, EvaluatorError]:
        left_expression = expression.operands[0]
        right_expression = expression.operands[1]

        left_expression_value_result = self.process_expression(left_expression)
        if not left_expression_value_result.is_ok:
            return left_expression_value_result

        right_expression_value_result = self.process_expression(right_expression)
        if not right_expression_value_result.is_ok:
            return right_expression_value_result

        left_value_data = left_expression_value_result.value
        right_value_data = right_expression_value_result.value
        if left_value_data.type != right_value_data.type:
            return evaluator_error_result(f'Operand types do not match for binary operation. Got {left_value_data.type.name} and {right_value_data.type.name}.')

        return Result(operator(left_value_data.value, right_value_data.value))

    def process_reverse_operation(self, expression: Expression):
        match expression.operands[0].type:
            case ExpressionType.Identifier:
                variable_data = self.variables.get(expression.value, None)
                match variable_data.type:
                    case ExpressionType.String:
                        return Result(self.reverse_string(expression))
                    case ExpressionType.Number:
                        return Result(self.reverse_number(expression))
            case ExpressionType.String:
                return Result(self.reverse_string(expression))
            case ExpressionType.Number:
                return Result(self.reverse_number(expression))
            case ExpressionType.Boolean:
                return evaluator_error_result('Operand cannot be boolean.')

    def reverse_string(self, expression: Expression):
        return expression.operands[0].value[::-1]

    def reverse_number(self, expression: Expression):
        number_value = expression.operands[0].value
        reverse_number = 0
        while number_value > 0:
            digit = number_value % 10
            reverse_number = reverse_number * 10 + digit
            number_value //= 10
        return reverse_number

    def process_print(self, expression: Expression):
        for argument in expression.operands:
            argument_value_result = self.process_expression(argument)
            if not argument_value_result.is_ok:
                return argument_value_result

            print(argument_value_result.value, sep = None)


def evaluator_error_result(message: str) -> Result[any, EvaluatorError]:
    return Result(error = EvaluatorError(message))
