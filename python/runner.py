from evaluator import *
from parser import *
from tokenizer import *


class Runner:
    def __init__(self, code: str, output_destination):
        self.code = code
        self.output_destination = output_destination

    def run_code(self):
        tokenizer = Tokenizer(self.code)
        tokens = tokenizer.process()

        errors = False
        for token_result in tokens:
            if not token_result.is_ok:
                errors = True
                error = token_result.error
                self.output_destination.write(f'[Line {error.line_number}] {error.error_message}')

        if errors:
            return 1

        tokens = map(lambda t: t.value, tokens)

        parser = Parser(tokens)
        expression_results = parser.process()

        for result in expression_results:
            if not result.is_ok:
                errors = True
                error = result.error
                self.output_destination.write(error.message)

        if errors:
            return 1

        expressions = map(lambda e: e.value, expression_results)

        evaluator = Evaluator(expressions, self.output_destination)
        evaluator.process()