__author__ = "Howard C Lovatt."
__copyright__ = "Howard C Lovatt, 2025 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT"
__repository__ = "https://github.com/hlovatt/nonesafe"
__version__ = "0.1.7"  # Version set by https://github.com/hlovatt/tag2ver

from collections.abc import Mapping, Iterable, Sequence, Callable
from typing import Any, Final


class _NSDictMarker:
    """Used as a marker for classes created by ``nsdict`` and helps type checking of ``nsdict``.

    Treat as an abstract class, but can't use ``ABC`` because the inherited classes are dynamically created.
    """

    # noinspection PyUnusedLocal
    def __init__(
        self,
        dict_values: Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None,
        **kw_values: Any,
    ):
        # Help type checker out! This `__init__` is never called!
        self.__orig_values__ = {}
        raise NotImplemented("This is a bug in `nonesafe`!")

    def todict(self) -> dict[str, Any]:
        raise NotImplemented("This is a bug in `nonesafe`!")


# Unfortunately can't use `__set_name__` instead of `name` arg because `__set_name__` only works inside classes.
def nsdict(
    name: str,
    dict_fields: Mapping[str, type] | Iterable[tuple[str, type]] | None = None,
    **kw_fields: type,
) -> type:
    """Create a new class with the given fields.

    See https://github.com/hlovatt/nonesafe/ for more details.
    """
    new: Final = type(name, (_NSDictMarker,), {})

    if not dict_fields and not kw_fields:
        raise ValueError("Both `{dict_fields=}` and `{kw_fields=}` cannot be empty.")

    fields: Final = {} if dict_fields is None else dict(dict_fields)
    fields.update(kw_fields)

    def _init(
        self: _NSDictMarker,
        dict_values: Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None,
        **kw_values: Any,
    ):
        self.__orig_values__ = {} if dict_values is None else dict(dict_values)
        self.__orig_values__.update(kw_values)
        values = {k: v for k, v in self.__orig_values__.items() if k in fields}

        for n, t in fields.items():
            if n == "__orig_values__":
                raise ValueError("Field nane `__orig_values__` is reserved.")
            n_in_vs = n in values
            if issubclass(t, _NSDictMarker):
                if n_in_vs:
                    value = values[n]
                    if isinstance(value, _NSDictMarker):
                        v = value
                    else:
                        # noinspection PyArgumentList
                        v = t(value)
                else:
                    v = t()
            elif n_in_vs:
                v = values[n]
            else:
                v = None
            setattr(self, n, v)

    new.__init__ = _init

    def _repr(self: _NSDictMarker) -> str:
        return f"{name}({', '.join(f'{n}={repr(getattr(self, n))}' for n in fields)})"

    new.__repr__ = _repr

    def _todict(self: _NSDictMarker) -> dict[str, Any]:
        for n in fields:
            v = getattr(self, n)
            if isinstance(v, _NSDictMarker):
                self.__orig_values__[n] = v.todict()
            elif v is not None:
                self.__orig_values__[n] = v
        return self.__orig_values__

    new.todict = _todict

    return new


def nsget[T](value: T | None, default: T) -> T:
    """Return ``default`` if ``value`` is ``None`` else ``value``.

    See https://github.com/hlovatt/nonesafe/ for more details.
    """
    return default if value is None else value


def nssub[
    T
](subscriptable: Sequence[T] | Mapping[Any, T] | None, index: Any) -> T | None:
    """Return ``None`` if ``subscriptable`` is ``None`` else ``subscriptable[index]``.

    See https://github.com/hlovatt/nonesafe/ for more details.
    """
    return None if subscriptable is None else subscriptable[index]


def nscall[
    T
](callable_: Callable[..., T] | None, *args: Any, **kwargs: Any) -> T | None:
    """Return ``None`` if ``callable_`` is ``None`` else ``callable_(*args, **kwargs)``.

    See https://github.com/hlovatt/nonesafe/ for more details.
    """
    return None if callable_ is None else callable_(*args, **kwargs)


if __name__ == "__main__":
    from pathlib import Path

    readme = "README.rst"
    if Path(readme).is_file():
        from doctest import testfile

        print(f"`doctest` {readme}")
        testfile(readme)
