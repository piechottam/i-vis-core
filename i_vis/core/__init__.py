from .__version__ import __MAJOR__, __MINOR__, __PATCH__, __SUFFIX__
from .version import Default as DefaultVersion

VERSION = DefaultVersion(
    major=__MAJOR__, minor=__MINOR__, patch=__PATCH__, suffix=__SUFFIX__
)
