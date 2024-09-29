import operator as python_operator

from parser import *
from result import *

Nya = object()


class VariableData:
    def __init__(self, value, type: ExpressionType):
        self.value = value
        self.type: ExpressionType = type


class EvaluatorError:
    def __init__(self, message: str):
        self.message = message

class Evaluator:
    def __init__(self, expressions: list[Expression]):
        self.expressions = expressions
        self.variables: dict[str, VariableData] = {}

    def process(self):
        for expression in self.expressions:
            result = self.process_expression(expression)
            if not result.is_ok:
                print(f'FATAL ERROR: {result.error.message}')
                return

    def process_expression(self, expression: Expression) -> Result[any, EvaluatorError]:
        result: Result[any, EvaluatorError] = None
        match expression.type:
            case ExpressionType.Nya:
                return Result(Nya)

            case ExpressionType.Boolean | ExpressionType.Number | ExpressionType.String:
                return Result(expression.value)

            case ExpressionType.Identifier:
                variable_data = self.variables.get(expression.value, None)
                if variable_data is None:
                    return evaluator_error_result(f'Variable {expression.value} is not defined.')

                return Result(variable_data)

            case ExpressionType.Operation:
                match expression.operator:
                    case Operator.Group:
                        result = self.process_expression(expression.operands[0])

                    case Operator.Print:
                        self.process_print(expression)
                        result = Result(Nya)

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

    def process_assignment(self, expression: Expression):
        identifier_expression = expression.operands[0]
        if identifier_expression.type != ExpressionType.Identifier:
            return evaluator_error_result("Expected identifier for the left hand side of assignment expression.")

        value_expression = expression.operands[1]
        actual_value_result = self.process_expression(value_expression)
        if not actual_value_result.is_ok:
            return actual_value_result

        variable_name = expression.operands[0].value
        actual_value = actual_value_result.value
        # TODO: Still not the right way to get its type
        self.variables[variable_name] = VariableData(actual_value, value_expression.type)
        return Result(self.variables[variable_name])

    def process_binary_operation(self, expression: Expression, operator):
        left_expression = expression.operands[0]
        right_expression = expression.operands[1]

        left_expression_value_result = self.process_expression(left_expression)
        if not left_expression_value_result.is_ok:
            return left_expression_value_result

        right_expression_value_result = self.process_expression(right_expression)
        if not right_expression_value_result.is_ok:
            return right_expression_value_result

        if self.expression_actual_type(left_expression) != self.expression_actual_type(right_expression):
            return evaluator_error_result(f'Operand types do not match for binary operation. Got {left_expression.type.name} and {right_expression.type.name}.')

        left_value = self.actual_value(left_expression_value_result.value)
        right_value = self.actual_value(right_expression_value_result.value)

        return Result(operator(left_value, right_value))

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

    def actual_value(self, expression_value):
        actual_value = expression_value
        if type(actual_value) == VariableData:
            actual_value = actual_value.value

        return actual_value

    def expression_actual_type(self, expression: Expression) -> ExpressionType:
        expression_type = expression.type
        if expression_type == ExpressionType.Identifier:
            expression_type = self.variables[expression.value].type

        return expression_type


def evaluator_error_result(message: str) -> Result[any, EvaluatorError]:
    return Result(error = EvaluatorError(message))
