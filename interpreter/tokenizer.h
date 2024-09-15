#pragma once

#include <optional>
#include <string>
#include <string_view>
#include <vector>

#include "result.h"

struct TokenizerError
{
	size_t		line_number;
	std::string	error_message;
};

enum TokenKind
{
    Bang,
    BangEqual,
    Comma,     
    DoubleEqual,
    Dot,       
    Equal,
    Greater,
    GreaterEqual,
    LeftBrace,
    LeftParen,
    Less,
    LessEqual,
    Minus,     
    Plus,      
    RightBrace,
    RightParen,
    Semicolon, 
    Slash,     
    Star,

    Keyword,
    Identifier,
    Number,
    String,
};

struct Token
{
	TokenKind			kind;
	std::string_view	original;
};

class Tokenizer
{
	std::string_view	input;
	std::size_t			index;

public:
	Tokenizer(const std::string &input) :
		input(input),
		index(0)
	{ }

    std::vector<Result<Token, TokenizerError>> process();

	void process_token_kind(std::vector<Result<Token, TokenizerError>> &tokens, TokenKind token_kind, std::string_view original) const;

	std::optional<std::tuple<char, TokenKind, Token>> get_continuation_token(TokenKind token_kind, std::string_view original) const;

    void print(const std::vector<Result<Token, TokenizerError>> &tokens) const;

	std::optional<double> parse_number(std::string_view number_string) const;
};
