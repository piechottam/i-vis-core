from enum import Enum


class GenomeAssembly(Enum):
    GRCH37 = "GRCh37"
    GRCHJ38 = "GRCh38"


class Strand(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"
    UNKNOWN = "unknown"


API_TOKEN_LENGTH = 32
