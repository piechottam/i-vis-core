__MAJOR__ = 0
__MINOR__ = 1
__PATCH__ = 2
__SUFFIX__ = ""

__VERSION__ = ".".join(map(str, (__MAJOR__, __MINOR__, __PATCH__))) + (
    "-" + __SUFFIX__ if __SUFFIX__ else ""
)
