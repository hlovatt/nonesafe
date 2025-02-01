__author__ = "Howard C Lovatt."
__copyright__ = "Howard C Lovatt, 2025 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT"
__repository__ = "https://github.com/hlovatt/nonesafe"
__version__ = "0.0.0"

from collections.abc import Mapping, Iterable
from typing import Any, Final

#TODO Check field value is of correct type or `None` (auto-convert if possible). Presently ugly error!
#TODO Add `todict`: should 'extras' not parsed be added back in? Should `None` be omitted? Yes & Yes.
#TODO Allow `declare` to be used as a class decorator.
#TODO Decorated classes can provide defaults other than `None`.

class _NSMarker:
    ...

def declare(
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
        values: Final = {} if dict_values is None else dict(dict_values)
        values.update(kw_values)
        for n in list(values):  # Copy keys into a list; you can't delete from `values` whilst traversing `values`.
            if n not in fields:
                del values[n]

        for n, t in fields.items():
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
            object.__setattr__(self, n, v)
    new.__init__ = _init

    def _repr(self: type) -> str:
        return f'{name}({', '.join(f'{n}={repr(getattr(self, n))}' for n in fields)})'
    new.__repr__ = _repr

    return new

def onnone[T](value: T | None, otherwise: T) -> T:
    return otherwise if value is None else value

if __name__ == '__main__':
    from pathlib import Path
    readme = 'README.rst'
    if Path(readme).is_file():
        from doctest import testfile
        print(f'`doctest` {readme}')
        testfile(readme)

    print('Example of `nonesafe` usage')
    C: Final = declare('C', d=int)
    A: Final = declare('A', c=C)
    print(vars(A))
    print(f'{A({'c': {'d': 0}})=}')
    print(f'{A([('c', [('c', 0)])])=}')
    print(f'{A(c=C(d=0))=}')
    print(f'{A()=}')
    a_ok = A(c=C(d=0))
    print(f'{a_ok=}')
    print(f'{a_ok.c=}')
    print(f'{a_ok.c.d=}')
    a_none = A()
    print(f'{a_none=}')
    print(f'{a_none.c=}')
    print(f'{a_none.c.d=}')
    Safe: Final = declare('Safe', a=A, b=int)
    print(f'{Safe({'a': {'c': {'d': 0}}, 'b': 1})=}')
    print(f'{Safe([('a', [('c', [('d', 0)])]), ('b', 1)])=}')
    print(f'{Safe(a=A(c=C(d=0)), b=1)=}')
    print(f'{Safe()=}')
    print(f'{Safe(not_a=A(c=C(d=0)), not_b=1)=}')
    print(f'{Safe(not_a=A(c=C(d=0)), b=1)=}')
    s_ok = Safe(a=A(c=C(d=0)), b=1)
    print(f'{s_ok=}')
    print(f'{s_ok.a=}')
    print(f'{s_ok.a.c=}')
    print(f'{s_ok.a.c.d=}')
    print(f'{s_ok.b=}')
    print(f'{onnone(None, -1)=}')
