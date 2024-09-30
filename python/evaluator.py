import math
import operator as python_operator
from audioop import reverse

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
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number, ValueType.String],
                                                              1, UnUReversa)

                    case Operator.TwTPotencia:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              2, TwTPotencia)

                    case Operator.owoValorTotal:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              1, owoValorTotal)

                    case Operator.UwUMaximo:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              2, UwUMaximo, True)

                    case Operator.UnUMinimo:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              2, UwUMinimo, True)

                    case Operator.UwUCima:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              1, UwUCima)

                    case Operator.UnUSuelo:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              1, UnUSuelo)

                    case Operator.EwEMedia:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              2, EwEMedia, True)

                    case Operator.TwTSuma:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.Number],
                                                              2, TwTSuma, True)

                    case Operator.OwOLazo:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.String],
                                                              1,OwOLazo)

                    case Operator.UnUMezcla:
                        result = self.process_n_ary_operation(expression,
                                                              [ValueType.String],
                                                              2,UnUMezcla)


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

        return Result(ValueData.number_value(operator(left_value_data.value, right_value_data.value)))

    def process_n_ary_operation(self, expression: Expression, expected_operand_types: list[ValueType],
                                expected_operand_count: int | None, built_in_function, multi_value = False) -> Result[ValueData, EvaluatorError]:
        operand_count = len(expression.operands)
        if (expected_operand_count is not None and operand_count != expected_operand_count) and not multi_value:
            return evaluator_error_result(f'Invalid number of arguments for {expression.type.name}. Expected {expected_operand_count}, got {operand_count}.')

        index = 0
        operand_values_data: list[ValueData] = []
        for operand in expression.operands:
            operand_value_result = self.process_expression(operand)
            if not operand_value_result.is_ok:
                return operand_value_result

            operand_value_data = operand_value_result.value
            if operand_value_data.type == ValueType.Nya:
                return evaluator_error_result(f'nya~~ value passed through {index}th parameter to {expression.type.name} function.')
            if operand_value_data.type not in expected_operand_types:
                type_names_joined = " or ".join(expected_operand_types)
                return evaluator_error_result(f'Invalid argument type for {expression.type.name} function. Expected {type_names_joined}, got {operand_value_data.type}.')

            operand_values_data.append(operand_value_result.value)

        built_in_function_arguments = []
        if expected_operand_count == 1:
            built_in_function_arguments = operand_values_data[0]
            return Result(ValueData(built_in_function(built_in_function_arguments), expected_operand_types))
        else:
            built_in_function_arguments = operand_values_data
            return Result(ValueData(built_in_function(*built_in_function_arguments), expected_operand_types))



    def process_print(self, expression: Expression):
        for argument in expression.operands:
            argument_value_result = self.process_expression(argument)
            if not argument_value_result.is_ok:
                return argument_value_result

            value_data = argument_value_result.value
            print(value_data.value, sep = None)


def evaluator_error_result(message: str) -> Result[any, EvaluatorError]:
    return Result(error = EvaluatorError(message))


def UnUReversa(value_data: ValueData) -> any:
    actual_value = value_data.value
    if value_data.type == ValueType.Number:
        return UnUReversa_number(actual_value)
    elif value_data.type == ValueType.String:
        return UnUReversa_string(actual_value)

    raise RuntimeError("Invalid value type for UnUReversa function.")


def UnUReversa_string(value: str):
    return value[::-1]


def UnUReversa_number(value: float):
    reverse_number = 0
    while value > 0:
        digit = value % 10
        reverse_number = reverse_number * 10 + digit
        value //= 10
    return reverse_number

def TwTPotencia(value_number: ValueData, value_power: ValueData) -> any:
    actual_value_number = value_number.value
    actual_value_power = value_power.value
    return actual_value_number ** actual_value_power

def owoValorTotal(value_data: ValueData) -> any:
    return abs(value_data.value)

def UwUMaximo(*numbers: ValueData) -> any:
    max_value = 0
    for number in numbers:
        if number.value > max_value:
            max_value = number.value

    return max_value

def UwUMinimo(*numbers: ValueData) -> any:
    min_value = 0
    for number in numbers:
        if number.value < min_value:
            min_value = number.value

    return min_value

def UwUCima(value_data: ValueData) -> any:
    return math.ceil(value_data.value)

def UnUSuelo(value_data: ValueData) -> any:
    return math.floor(value_data.value)

def EwEMedia(*numbers: ValueData) -> any:
    total = 0
    for number in numbers:
        total += number.value

    return total / len(numbers)

def TwTSuma(*numbers: ValueData) -> any:
    total = 0
    for number in numbers:
        total += number.value

    return total

def OwOLazo(value_data: ValueData) -> any:
    if value_data.value.lower() == value_data.value[::-1].lower():
        return "Chi"
    return "Ño"

def UnUMezcla(first_value_data: ValueData, second_value_data: ValueData) -> any:
    if sorted(first_value_data.value.lower()) == sorted(second_value_data.value.lower()):
        return "Chi"
    return "Ño"