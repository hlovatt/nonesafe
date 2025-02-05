__author__ = "Howard C Lovatt."
__copyright__ = "Howard C Lovatt, 2025 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT"
__repository__ = "https://github.com/hlovatt/nonesafe"
__version__ = "0.1.0"

from abc import ABC, abstractmethod
from collections.abc import Mapping, Iterable, Sequence, Callable
from typing import Any, Final

class _NSMarker:
    def todict(self: type) -> dict[str, Any]:
        raise NotImplemented("This is a bug in `nonesafe`!")  # Abstract class, but can't use ABC because dynamically created.

def nsdict(
        name: str,
        dict_fields: Mapping[str, type] | Iterable[tuple[str, type]] | None = None,
        **kw_fields: type
) -> type:
    new: Final = type(name, (_NSMarker, ), {})

    if not dict_fields and not kw_fields:
        raise ValueError('Both `{dict_fields=}` and `{kw_fields=}` cannot be empty.')

    fields: Final = {} if dict_fields is None else dict(dict_fields)
    fields.update(kw_fields)

    def _init(
            self: type,
            dict_values: Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None,
            **kw_values: Any
    ):
        self._orig_values_: Final = {} if dict_values is None else dict(dict_values)
        self._orig_values_.update(kw_values)
        values = {k: v for k, v in self._orig_values_.items() if k in fields}

        for n, t in fields.items():
            if n == '_orig_values_':
                raise ValueError('Field nane `_orig_values_` is reserved.')
            n_in_vs = n in values
            if issubclass(t, _NSMarker):
                if n_in_vs:
                    value = values[n]
                    if isinstance(value, _NSMarker):
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

    def _repr(self: type) -> str:
        return f'{name}({', '.join(f'{n}={repr(getattr(self, n))}' for n in fields)})'
    new.__repr__ = _repr

    def _todict(self: type) -> dict[str, Any]:
        for n in fields:
            v = getattr(self, n)
            if isinstance(v, _NSMarker):
                self._orig_values_[n] = v.todict()
            elif v is not None:
                self._orig_values_[n] = v
        return self._orig_values_
    new.todict = _todict

    return new

def nsget[T](value: T | None, default: T) -> T:
    return default if value is None else value

def nssub[T](subscriptable: Sequence[T] | Mapping[Any, T] | None, index: Any) -> T | None:
    return None if subscriptable is None else subscriptable[index]

def nscall[T](callable_: Callable[..., T] | None, *args: Any, **kwargs: Any) -> T | None:
    return None if callable_ is None else callable_(*args, **kwargs)

if __name__ == '__main__':
    from pathlib import Path
    readme = 'README.rst'
    if Path(readme).is_file():
        from doctest import testfile
        print(f'`doctest` {readme}')
        testfile(readme)
