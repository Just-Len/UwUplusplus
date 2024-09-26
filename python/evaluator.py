from parser import *
from result import *


class EvaluatorError:
    def __init__(self, message: str):
        self.message = message

class Evaluator:
    def __init__(self, expressions: list[Expression]):
        self.expressions = expressions

    def process(self):
        variables: dict[str, any] = {}

        for expression in self.expressions:
            self.process_expression(expression, variables)

    def process_expression(self, expression: Expression, variables: dict[str, any]) -> Result[any, EvaluatorError]:
        result: Result[any, EvaluatorError] = None
        match expression.type:
            case ExpressionType.Identifier:
                variable_value = variables.get(expression.value, None)
                if variable_value is None:
                    # TODO: Need to distinguish between None and nya in some way
                    return Result(error = EvaluatorError(f'Variable {expression.value} is not defined.'))

                return Result(variable_value)

            case ExpressionType.Operation:
                match expression.operator:
                    case Operator.Equals:
                        identifier_expression = expression.operands[0]
                        if identifier_expression.type != ExpressionType.Identifier:
                            return Result(error = EvaluatorError("Expected identifier for the left hand side of assignment expression."))

                        value_expression = expression.operands[1]
                        actual_value_result = self.process_expression(value_expression, variables)
                        if not actual_value_result.is_ok:
                            return actual_value_result

                        variable_name = expression.operands[0].value
                        variables[variable_name] = actual_value_result.value
                        result = Result(variables[variable_name])

                    case Operator.Plus:
                        left_expression = expression.operands[0]
                        right_expression = expression.operands[1]

                        if left_expression.type != right_expression.type:
                            return Result(error = EvaluatorError("Operand types do not match for add operation."))

                        left_expression_value_result = self.process_expression(left_expression, variables)
                        if not left_expression_value_result.is_ok:
                            return left_expression_value_result

                        right_expression_value_result = self.process_expression(right_expression, variables)
                        if not right_expression_value_result.is_ok:
                            return right_expression_value_result

                        left_value = left_expression_value_result.value
                        right_value = right_expression_value_result.value

                        result = left_value + right_value

            case ExpressionType.Boolean | ExpressionType.Number | ExpressionType.String:
                return Result(expression.value)

        return result
