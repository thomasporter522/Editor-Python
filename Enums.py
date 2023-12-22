from enum import Enum


class Direction(Enum):
    FREE = 1
    BOUND = 2

    default = FREE


class Rotation(Enum):
    INLINE = 1
    NEWLINE = 2

    default = INLINE

    def other(r):
        if r == Rotation.INLINE:
            return Rotation.NEWLINE
        if r == Rotation.NEWLINE:
            return Rotation.INLINE
        return None


class HoleType(Enum):
    ANY = 1
    NEWLITERAL = 2
    FUNCTION = 3
    TYPE = 4

    default = ANY


class NodeType(Enum):
    RootNode = 1
    LetNode = 2
    TypeNode = 3
    IdNode = 4
    HoleNode = 5
    PositionNode = 6
    FunNode = 7
    AppNode = 8
    ProductNode = 9
    AccessNode = 10
    EqualityNode = 11
    InductiveNode = 12
    UniverseNode = 13
