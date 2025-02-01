===========
 None safe
===========

-----------------------------------------------------
License: https://creativecommons.org/licenses/by/4.0/
-----------------------------------------------------

`nonesafe` makes it safe to parse dictionaries.

When parsing a dictionary from an external source,
a JSON request,
dictionary keys might be missing or
there may be unknown dictionary keys.

For example suppose you know (or only care about)
keys ``a`` and `b` at the top level and that
``a`` is also a dictionary that has a ``c``.

>>> d_ok = {'a': {'c': 1}, 'b': 0}

This would be easy to use directly as a dictionary:

>>> d_ok['a']
{'c': 1}
>>> d_ok['a']['c']
1
>>> d_ok['b']
0

But if instead from the external source you got:

>>> d_not_ok = {'a': {'c': 1}, 'not_b': 0}

Then the code above using a dictionary would fail.
Instead, use:

>>> import nonesafe as ns
>>> A = ns.declare('A', c=int)
>>> Safe = ns.declare('Safe', a=A, b=int)
>>> s = Safe(d_not_ok)
>>> s.a
A(c=1)
>>> s.a.c
1
>>> s.b

The missing value ``b`` is replaced by ``None``
(in the doctest above ``None`` is treated as not returning
a value)
and the extra value ``not_b`` is ignored.
The usage ``s.expr`` indicates safe
(will not raise an access exception but might 
return ``None`` instead).

There is also a utility function ``onnone(value, otherwise)``,
that takes a ``value`` that might be ``None`` and if it is
returns ``otherwise``.
EG:

>>> ns.onnone(s.b, -1)
-1

The function ``declare`` is very flexible,
the following are all the same as each other:

>>> Ex0 = ns.declare('Ex0', {'a': int, 'b': int})
>>> Ex1 = ns.declare('Ex1', [('a', int), ('b', int)])
>>> Ex2 = ns.declare('Ex2', a=int, b=int)
>>> Ex3 = ns.declare('Ex3', {'a': int}, b=int)
>>> Ex4 = ns.declare('Ex4', [('a', int)], b=int)

Constructing an instance of a ``nonsafe`` class is also
very flexible, 
the following are all the same as each other:

>>> ex0 = Ex0({'a': 0, 'b': 1})
>>> ex1 = Ex0([('a', 0), ('b', 1)])
>>> ex2 = Ex0(a=0, b=1)
>>> ex3 = Ex0({'a': 0}, b=1)
>>> ex4 = Ex0([('a', 0)], b=1)

and these are also the same as each other:

>>> ex5 = Ex0({})
>>> ex6 = Ex0([])
>>> ex7 = Ex0(None)
>>> ex8 = Ex0()

Installation
============
Simply copy
`nonesafe.py <https://github.com/hlovatt/nonesafe/nonesafe.py>`_
(note
`LICENCE <https://github.com/hlovatt/nonesafe/LICENSE>`_),
run some examples by executing ``nonesafe.py``

Alternatives
============
Very similar can be achieved with packages like
`pydantic <https://docs.pydantic.dev/latest/>`_,
but they are much too heavyweight for casual use
and there inclusion has previously been rejected
in favour of dataclasses
(`PEP 557 <https://peps.python.org/pep-0557/>`_).

