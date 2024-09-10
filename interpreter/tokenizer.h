#pragma once

#include <optional>
#include <string>
#include <string_view>
#include <vector>

typedef std::tuple<size_t, std::string> TokenizerError;

template <typename T, typename E>
struct Result
{
	bool is_ok;
	union
	{
		T value;
		E error;
	};

	Result<T, E>(T &value) : is_ok(true)
	{
		new(&this->value) T(value);
	}

	Result<T, E>(E &error) : is_ok(false)
	{
		new(&this->error) E(error);
	}

    Result(T&& value) : is_ok(true)
    {
        new(&this->value) T(std::move(value));
    }

    Result(E&& error) : is_ok(false)
    {
        new(&this->error) E(std::move(error));
    }

    ~Result()
    {
        if (is_ok)
        {
            value.~T();
        }
        else
        {
            error.~E();
        }
    }

    Result(const Result&) = delete;
    Result& operator=(const Result&) = delete;

	Result(Result&& other) noexcept : is_ok(other.is_ok)
    {
        if (is_ok)
        {
            new(&value) T(std::move(other.value));
        }
        else
        {
            new(&error) E(std::move(other.error));
        }
    }

    Result& operator=(Result&& other) noexcept
    {
        if (this != &other)
        {
            if (is_ok)
            {
                value.~T();
            }
            else
            {
                error.~E();
            }

            is_ok = other.is_ok;
            if (is_ok)
            {
                new(&value) T(std::move(other.value));
            }
            else
            {
                new(&error) E(std::move(other.error));
            }
        }

        return *this;
    }
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
