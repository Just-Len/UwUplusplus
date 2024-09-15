#pragma once

#include <algorithm>

template <typename T, typename E>
class Result
{
	bool _is_ok;
	union
	{
		T _value;
		E _error;
	};

public:
    bool is_ok() const
    {
        return _is_ok;
    }

    const E& error() const
    {
        return _error;
    }

    const T& value() const
    {
        return _value;
    }
    
	Result(T &value) : _is_ok(true)
	{
		new(&this->_value) T(value);
	}

	Result(E &error) : _is_ok(false)
	{
		new(&this->_error) E(error);
	}

    Result(T&& value) : _is_ok(true)
    {
        new(&this->_value) T(std::move(value));
    }

    Result(E&& error) : _is_ok(false)
    {
        new(&this->_error) E(std::move(error));
    }

    ~Result()
    {
        if (_is_ok)
        {
            _value.~T();
        }
        else
        {
            _error.~E();
        }
    }

    Result(const Result&) = delete;
    Result& operator=(const Result&) = delete;

	Result(Result&& other) noexcept : _is_ok(other._is_ok)
    {
        if (_is_ok)
        {
            new(&_value) T(std::move(other._value));
        }
        else
        {
            new(&_error) E(std::move(other._error));
        }
    }

    Result& operator=(Result&& other) noexcept
    {
        if (this != &other)
        {
            if (_is_ok)
            {
                _value.~T();
            }
            else
            {
                _error.~E();
            }

            _is_ok = other._is_ok;
            if (_is_ok)
            {
                new(&_value) T(std::move(other._value));
            }
            else
            {
                new(&_error) E(std::move(other._error));
            }
        }

        return *this;
    }
};
