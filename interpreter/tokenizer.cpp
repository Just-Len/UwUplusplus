#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <optional>
#include <ostream>
#include <sstream>

#include "string_iterator.h"
#include "tokenizer.h"

std::vector<Result<Token, TokenizerError>> Tokenizer::process()
{
	std::vector<Result<Token, TokenizerError>> tokens;
	size_t line_number = 0;

	while (true) {
		std::string_view input_left = this->input.substr(this->index);
		StringIterator input_iterator(input_left);

		std::optional<char> current_character = input_iterator.next();
		if (current_character.has_value()) {
			size_t current_index = 0;
			char character = current_character.value();

			enum Initial
			{
				Alphabetic,
				ContinuationToken,
				Digit,
				Quote,
				SingleSymbol
			};

			Initial initial_token;
			TokenKind initial_token_kind;

			if (std::isdigit(character)) {
				initial_token = Initial::Digit;
			}
			else if (std::isalpha(character) || character == '_') {
				initial_token = Initial::Alphabetic;
			}
			else if (std::isblank(character) || std::isspace(character)) {
				if (character == '\n') {
					line_number += 1;
				}

				this->index += 1;
				continue;
			}
			else {
				switch (character) {
					case ',':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Comma;
						break;
					case '.':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Dot;
						break;
					case '{':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::LeftBrace;
						break;
					case '(':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::LeftParen;
						break;
					case '-':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Minus;
						break;
					case '+':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Plus;
						break;
					case '}':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::RightBrace;
						break;
					case ')':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::RightParen;
						break;
					case ';':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Semicolon;
						break;
					case '*':
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Star;
						break;
					case '/':
					{
						std::optional<char> next_character = input_iterator.next();
						if (next_character.has_value() && next_character.value() == '/') {
							size_t newline_index = input_left.find("\n");
							this->index += newline_index == std::string_view::npos ? input_left.length() : newline_index + 1;
							line_number += 1;
							continue;
						}
							
						initial_token = Initial::SingleSymbol;
						initial_token_kind = TokenKind::Slash;

						break;
					}

					case '!':
						initial_token = Initial::ContinuationToken;
						initial_token_kind = TokenKind::Bang;
						break;
					case '=':
						initial_token = Initial::ContinuationToken;
						initial_token_kind = TokenKind::Equal;
						break;
					case '>':
						initial_token = Initial::ContinuationToken;
						initial_token_kind = TokenKind::Greater;
						break;
					case '<':
						initial_token = Initial::ContinuationToken;
						initial_token_kind = TokenKind::Less;
						break;

					case '"':
						initial_token = Initial::Quote;
						break;

					default: 
						std::stringstream message;
						message << "Unexpected character: " << character;
						Result<Token, TokenizerError> result(TokenizerError { line_number, message.str() });
						tokens.push_back(std::move(result));
						this->index += 1;
						continue;
				}
			}

			switch (initial_token) {
				case Initial::SingleSymbol:
					this->process_token_kind(tokens, initial_token_kind, input_left.substr(0, 1));
					this->index += 1;
					break;

				case Initial::ContinuationToken:
				{
					auto continuation_token = this->get_continuation_token(initial_token_kind, input_left.substr(0, 1));
					std::optional<char> next_character;
					if (continuation_token.has_value()
						&& (next_character = input_iterator.next()).has_value()
						&& next_character.value() == std::get<0>(continuation_token.value())
					) {
						this->process_token_kind(tokens, std::get<1>(continuation_token.value()), input_left.substr(0, 2));
						this->index += 2;
					}
					else if (continuation_token.has_value()) {
						auto &tuple = continuation_token.value();
						Result<Token, TokenizerError> result(std::get<2>(tuple));
						tokens.push_back(std::move(result));
						this->index += 1;
					}
					else {
						// TODO: This does make sense, what does NOT make sense is the way I
						// handle the continuation things, those shouldn't be Options
						this->process_token_kind(tokens, initial_token_kind, input_left.substr(0, 1));
						this->index += 1;
					}

					break;
				}

				case Initial::Alphabetic:
				{
					auto item_ptr = std::find_if(input_left.begin(), input_left.end(), [](const char &c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_'; });
					size_t identifier_end_index = item_ptr == input_left.end() ? input_left.length() : std::distance(input_left.begin(), item_ptr); 

					std::string_view word = input_left.substr(0, identifier_end_index);

					if (word == "and" || word == "class" || word == "else" || word == "false" || word == "for" || word == "fun" || word == "if" || word == "nil" || word == "or" || word == "print" || word == "return" || word == "super" || word == "this" || word == "true" || word == "var" || word == "while") {
						this->process_token_kind(tokens, TokenKind::Keyword, word);
					}
					else {
						this->process_token_kind(tokens, TokenKind::Identifier, word);
					}

					this->index += word.length();
					break;
				}

				case Initial::Digit:
				{
					size_t end_index = current_index;
					bool dot_found = false;

					std::optional<char> opt;
					while ((opt = input_iterator.next()).has_value()) {
						char next_character = opt.value();

						if (next_character == '.') {
							if (dot_found) {
								break;
							}

							dot_found = true;
							end_index += 1;
						}
						else if ((next_character >= '0' && next_character <= '9') || next_character == '_') {
							end_index += 1;
						}
						else {
							break;
						}
					}

					if (input_left[end_index] == '.') {
						end_index -= 1;
					}

					std::string_view number_substring = input_left.substr(0, end_index + 1);
					this->process_token_kind(tokens, TokenKind::Number, number_substring);
					this->index += number_substring.length();
					break;
				}

				case Initial::Quote:
				{
					size_t closing_quote_index = input_left.find("\"", 1);
					
					if (closing_quote_index != std::string_view::npos) {
						std::string_view string_value = input_left.substr(current_index, closing_quote_index + 1);
						this->process_token_kind(tokens, TokenKind::String, string_value);
						this->index += string_value.length();
					}
					else {
						Result<Token, TokenizerError> result(TokenizerError { line_number, "Unterminated string." });
						tokens.push_back(std::move(result));
						this->index += input_left.length();
					}

					break;
				}
			}
		}
		else {
			break;

		}
	}

	return tokens;
}

void Tokenizer::process_token_kind(std::vector<Result<Token, TokenizerError>> &tokens, TokenKind token_kind, std::string_view original) const
{
	Token token = { token_kind, original };

	tokens.push_back(Result<Token, TokenizerError>(token));
}

std::optional<std::tuple<char, TokenKind, Token>> Tokenizer::get_continuation_token(TokenKind token_kind, std::string_view original) const
{
	Token token_no_match = { token_kind, original };
	std::tuple<char, TokenKind, Token> tuple;

	switch (token_kind)
	{
		case TokenKind::Bang:
			tuple = std::tuple('=', TokenKind::BangEqual, token_no_match);
			break;
		case TokenKind::Equal:
			tuple = std::tuple('=', TokenKind::DoubleEqual, token_no_match);
			break;
		case TokenKind::Greater:
			tuple = std::tuple('=', TokenKind::GreaterEqual, token_no_match);
			break;
		case TokenKind::Less:
			tuple = std::tuple('=', TokenKind::LessEqual, token_no_match);
			break;
		default:
			return std::nullopt;
	}

	return std::optional(tuple);
}

void Tokenizer::print(const std::vector<Result<Token, TokenizerError>> &tokens) const
{
	for (auto &token_result : tokens)
	{
		if (!token_result.is_ok()) {
			const TokenizerError &error = token_result.error();

			fprintf(stderr, "[line %llu] Error: %s\n", error.line_number, error.error_message.c_str());
			continue;
		}

		const Token &token = token_result.value();
		std::tuple<std::string, std::optional<std::string_view>> token_string_tuple;

		switch (token.kind)
		{
			case TokenKind::Bang:
				token_string_tuple = std::tuple("BANG", std::nullopt);
				break;
			case TokenKind::BangEqual:
				token_string_tuple = std::tuple("BANG_EQUAL", std::nullopt);
				break;
			case TokenKind::Comma:
				token_string_tuple = std::tuple("COMMA", std::nullopt);
				break;
			case TokenKind::DoubleEqual:
				token_string_tuple = std::tuple("EQUAL_EQUAL", std::nullopt);
				break;
			case TokenKind::Dot:
						token_string_tuple = std::tuple("DOT", std::nullopt);
				break;
			case TokenKind::Equal:
				token_string_tuple = std::tuple("EQUAL", std::nullopt);
				break;
			case TokenKind::Greater:
				token_string_tuple = std::tuple("GREATER", std::nullopt);
				break;
			case TokenKind::GreaterEqual:
				token_string_tuple = std::tuple("GREATER_EQUAL", std::nullopt);
				break;
			case TokenKind::LeftBrace:
				token_string_tuple = std::tuple("LEFT_BRACE", std::nullopt);
				break;
			case TokenKind::LeftParen:
					token_string_tuple = std::tuple("LEFT_PAREN", std::nullopt);
				break;
			case TokenKind::Less:
				token_string_tuple = std::tuple("LESS", std::nullopt);
				break;
			case TokenKind::LessEqual:
				token_string_tuple = std::tuple("LESS_EQUAL", std::nullopt);
				break;
			case TokenKind::RightBrace:
				token_string_tuple = std::tuple("RIGHT_BRACE", std::nullopt);
				break;
			case TokenKind::RightParen:
				token_string_tuple = std::tuple("RIGHT_PAREN", std::nullopt);
				break;
			case TokenKind::Semicolon:
				token_string_tuple = std::tuple("SEMICOLON", std::nullopt);
				break;
			case TokenKind::Minus:
				token_string_tuple = std::tuple("MINUS", std::nullopt);
				break;
			case TokenKind::Plus:
				token_string_tuple = std::tuple("PLUS", std::nullopt);
				break;
			case TokenKind::Slash:
				token_string_tuple = std::tuple("SLASH", std::nullopt);
				break;
			case TokenKind::Star:
				token_string_tuple = std::tuple("STAR", std::nullopt);
				break;

			case TokenKind::Keyword:
			{
				std::string token_name;
				token_name.resize(token.original.length(), '\0');
				token.original.copy(token_name.data(), token.original.length());

				token_string_tuple = std::tuple(token_name, std::nullopt);
				break;
			}
			case TokenKind::Identifier:
				token_string_tuple = std::tuple("IDENTIFIER", std::nullopt);
				break;
			case TokenKind::Number:
			{
				std::stringstream token_value_str;
				double number = parse_number(token.original).value();  // NOLINT(bugprone-unchecked-optional-access)

				if (number == std::trunc(number)) {
					token_value_str << number << ".0";
				}
				else {
					token_value_str << token.original;
				}

				token_string_tuple = std::tuple("NUMBER", std::optional(token_value_str.str()));
				break;
			}
			case TokenKind::String:
				token_string_tuple = std::tuple("STRING", std::optional(token.original.substr(1, token.original.length() - 2)));
				break;
		}

		std::string token_value(std::get<1>(token_string_tuple).value_or("null"));
		std::cout	<< std::get<0>(token_string_tuple).c_str()
					<< ' ' << token.original
					<< ' ' << token_value.c_str()
					<< '\n';
	}
}

std::optional<double> Tokenizer::parse_number(std::string_view number_string) const
{
	uint32_t 	decimal_places = 0,
			 	digit_count = 0,
			 	exponent = 0;
	auto		iterator = number_string.rbegin();
	double		number = 0;

	for (; iterator != number_string.rend(); ++iterator) {
		char number_character = *iterator;

		if (std::isdigit(number_character)) {
			if (number_character != '0' || decimal_places != 0) {
				int digit = number_character - '0';
				number += (digit * std::pow(10, exponent));
			}

			exponent += 1;
		}
		else if (number_character == '.') {
			decimal_places = digit_count;
			continue;
		}
		else if (number_character == '_') {
			continue;
		}
		else {
			return std::nullopt;
		}

		digit_count += 1;
	}

	number /= std::pow(10, decimal_places);

	return std::optional(number);
}
