"""Tokenizer for the binary Generation 1 expression language."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


_TOKEN = re.compile(r"\s*(?:(?P<number>\d+(?:/\d+)?)|(?P<name>[A-Za-z_]\w*)|(?P<operator>[+\-*/])|(?P<left>\()|(?P<right>\)))")


def tokenize(source: str) -> tuple[Token, ...]:
    tokens: list[Token] = []
    position = 0
    while position < len(source):
        match = _TOKEN.match(source, position)
        if not match:
            raise ValueError(f"Unexpected character at position {position}: {source[position]!r}")
        kind = match.lastgroup
        assert kind is not None
        tokens.append(Token(kind, match.group(kind)))
        position = match.end()
    tokens.append(Token("eof", ""))
    return tuple(tokens)
