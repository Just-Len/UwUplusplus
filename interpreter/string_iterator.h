#pragma once
#include <optional>
#include <string>

class StringIterator
{
    const char  *start,
                *end;

public:
    StringIterator(const std::string &input) :
        start(input.data()),
        end(input.data() + input.length())
    { }
    
    StringIterator(const std::string_view &input) :
        start(input.data()),
        end(input.data() + input.length())
    { }

    std::optional<char> next()
    {
        if (start != end) {
            char character = *start;
            start += 1;
            
            return std::optional(character);
        }

        return std::nullopt;
    }
};
