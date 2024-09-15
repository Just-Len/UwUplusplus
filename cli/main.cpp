#include <cstring>
#include <fstream>

#include "tokenizer.h"

std::optional<const char*> next_arg(const char **&args, int &argsCount)
{
	if (argsCount > 0) {
		const char *arg = *args;
		argsCount -= 1;
		args += 1;
		return std::optional(arg);
	}

	return std::nullopt;
}

int main(int argsCount, const char **args)
{
	next_arg(args, argsCount);
	auto opt = next_arg(args, argsCount);
	int exit_code = 0;

	if (opt.has_value()) {
		const char *arg = opt.value();
		if (std::strcmp(arg, "tokenize") == 0) {
			opt = next_arg(args, argsCount);
			if (!opt.has_value()) {
				std::printf("Expected filename.\n");
				return 1;
			}

			auto filename = opt.value();
			std::ifstream file(opt.value());
			std::string file_contents;

			if (!file.is_open()) {
				std::printf("Couldn't open file %s\n", filename);
				return 1;
			}

			file >> file_contents;
			file.close();

			Tokenizer tokenizer(file_contents);
			auto tokens = tokenizer.process();

			for (auto &token : tokens) {
				if (!token.is_ok()) {
					exit_code = 65;
					break;
				}
			}

			tokenizer.print(tokens);
		}
	}
	else {
		std::printf("No command given.\n");
		exit_code = 1;
	}

	return exit_code;
}
