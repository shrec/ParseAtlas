"""Generation 1 grammar registry."""

from dataclasses import dataclass
from itertools import permutations

OPERATORS = ("+", "-", "*", "/")


@dataclass(frozen=True)
class Grammar:
    """A global precedence grammar, listed from highest to lowest."""

    id: str
    precedence: tuple[str, ...]
    levels: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        if not self.levels:
            object.__setattr__(self, "levels", tuple((operator,) for operator in self.precedence))

    @property
    def binding_power(self) -> dict[str, int]:
        return {operator: len(self.precedence) - index for index, operator in enumerate(self.precedence)}


def strict_grammars() -> tuple[Grammar, ...]:
    return tuple(
        Grammar(f"G{index:02d}", ordering)
        for index, ordering in enumerate(permutations(OPERATORS), start=1)
    )


def control_grammar() -> Grammar:
    return Grammar("G0", ("*", "/", "+", "-"), (("*", "/"), ("+", "-")))


def all_grammars() -> tuple[Grammar, ...]:
    return (control_grammar(), *strict_grammars())
