"""Precedence-parameterized parser for binary arithmetic expressions."""

from dataclasses import dataclass
from fractions import Fraction

from .grammar import Grammar
from .tokenizer import Token, tokenize


@dataclass(frozen=True)
class Number:
    value: Fraction


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class Binary:
    operator: str
    left: "Node"
    right: "Node"


Node = Number | Variable | Binary


class Parser:
    def __init__(self, tokens: tuple[Token, ...], grammar: Grammar) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.index = 0
        self._powers = {operator: len(grammar.levels) - level for level, group in enumerate(grammar.levels) for operator in group}

    def parse(self) -> Node:
        result = self._expression(0)
        if self._current.kind != "eof":
            raise ValueError(f"Unexpected token: {self._current.value!r}")
        return result

    @property
    def _current(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self._current
        self.index += 1
        return token

    def _expression(self, minimum_power: int) -> Node:
        left = self._primary()
        while self._current.kind == "operator" and self._powers[self._current.value] >= minimum_power:
            operator = self._advance().value
            left = Binary(operator, left, self._expression(self._powers[operator] + 1))
        return left

    def _primary(self) -> Node:
        token = self._advance()
        if token.kind == "number":
            if "/" in token.value:
                numerator, denominator = token.value.split("/", 1)
                return Number(Fraction(int(numerator), int(denominator)))
            return Number(Fraction(int(token.value)))
        if token.kind == "name":
            return Variable(token.value)
        if token.kind == "left":
            result = self._expression(0)
            if self._advance().kind != "right":
                raise ValueError("Expected closing parenthesis")
            return result
        raise ValueError(f"Expected number, variable, or parenthesized expression; got {token.value!r}")


def parse(source: str, grammar: Grammar) -> Node:
    return Parser(tokenize(source), grammar).parse()
