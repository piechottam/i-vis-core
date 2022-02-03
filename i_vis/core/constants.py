"""Constants.
"""
from enum import Enum


class GenomeAssembly(Enum):
    GRCH37 = "GRCh37"
    GRCH38 = "GRCh38"


class Strand(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"
    UNKNOWN = "unknown"


#: Default length of API token.
API_TOKEN_LENGTH: int = 32
