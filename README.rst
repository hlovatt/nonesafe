=========
None safe
=========

-------------------------------------------------------------------------------------
``nonesafe``: safe to read, write, and read/modify/write ``dicts`` from external data
-------------------------------------------------------------------------------------

Licenses
========
Code
    `MIT <https://opensource.org/license/MIT>`_
Rest
    `Creative Commons by Attribution
    <https://creativecommons.org/licenses/by/4.0/>`_

Installation
============
Simply copy
`nonesafe.py
<https://github.com/hlovatt/nonesafe/nonesafe.py>`_
(note
`LICENCE <https://github.com/hlovatt/nonesafe/LICENSE>`_),
run some examples by executing ``nonesafe.py``

Home: `Github <https://github.com/hlovatt/nonesafe>`_

Motivation
==========
When parsing a dictionary from an external source,
e.g. a JSON request,
dictionary keys might be missing or
there may be unknown dictionary keys or values might be ``None``.

For example suppose you know (or only care about)
keys ``a`` and ``b`` at the top level and that
``a`` is also a dictionary that has a ``c``.

>>> d_ok = {'a': {'c': 1}, 'b': 0}

This would be easy to use directly as a dictionary:

>>> d_ok['a']
{'c': 1}
>>> d_ok['a']['c']
1
>>> d_ok['b']
0

But if instead ``d_ok`` from the external source you got:

>>> d_not_ok = {'a': {'c': 1}, 'not_b': 0}

Then the code above using a dictionary would fail.
You could write safe accessor functions:

>>> from typing import Any
>>> def get_a(d: dict[str, Any] | None) -> Any | None:
...     return None if d is None else d.get('a', None)
>>> def get_b(d: dict[str, Any] | None) -> Any | None:
...     return None if d is None else d.get('b', None)
>>> def get_a_c(d: dict[str, Any] | None) -> Any | None:
...     a = get_a(d)
...     return None if a is None else a.get('c', None)

But "there must be a better way"
(apologies to Raymond Hettinger):

>>> from nonesafe import *
>>> A = nsdict('A', c=int)
>>> Safe = nsdict('Safe', a=A, b=int)

``nsdict`` creates a new class who's constructor
accepts a dict (or similar)
and then copies the values from the dict into the new class.
Missing values in the dict are replaced with ``None``.
If an embedded dict is missing,
it is replaced with a new class whose fields (leafs)
are ``None``.
In the example there are two classes created ``A``
and ``Safe``,
two classes because there is a nested dictionary in the data.

>>> s = Safe(d_not_ok)
>>> s.a
A(c=1)
>>> s.a.c
1
>>> s.b

The missing value ``b`` is replaced by ``None``
(in the ``doctest`` above ``None`` is treated as not
returning a value)
and the extra value ``not_b`` is ignored.
The usage ``s.expr`` indicates safe
(will not raise an access exception but might 
return ``None`` instead).

There is also three utility functions.

``nsget(value, default)``
takes a ``value`` that might be ``None`` and if it is
returns ``default``.
EG:

>>> nsget(s.b, -1)
-1

``nssub(subscriptable, index)``
takes a ``lst`` that might be ``None`` and if it is
returns ``None``, else returns ``subscriptable`` subscripted
by ``index``.
EG:

>>> nssub([0], 0)
0
>>> nssub(None, 0)

The intended use of ``nssub`` is lists that might be ``None``,
``nsdict`` is generally better for ``dict``s.

``nscall(callable, *args, **kwargs)``
takes a ``callable`` that might be ``None`` and if it is
returns ``None``, else returns ``callable`` called with
``args`` and ``kwargs``.
EG:

>>> nscall(lambda x, y: (x, y), 0, y=1)
(0, 1)
>>> nscall(None)

The above has only discussed reading external data.
Hand coding safe writing is cumbersome.

>>> def set_a(d: dict[str, Any] | None, value: Any) -> dict[str, Any]:
...     if d is None:
...         d = {}
...     d['a'] = value
...     return d
>>> def set_b(d: dict[str, Any] | None, value: Any) -> dict[str, Any]:
...     if d is None:
...         d = {}
...     d['b'] = value
...     return d
>>> def set_a_c(d: dict[str, Any] | None, value: Any) -> dict[str, Any]:
...     if d is None:
...         d = {}
...     a = d.get('a', {})
...     a['c'] = value
...     return d

Writing is much easier using ``nonesafe`` than the above, EG:

>>> out = Safe()

Just an instance of the required safe version of the dict
is needed.
In use:

>>> out.a.c = 0
>>> out.todict()
{'a': {'c': 0}}

Note how the embedded dict is auto-created and the ``b`` field
which is ``None`` is omitted to reduce payload size
when writing externally.

Reading/modifying/writing external data is
cumbersome to hand code
(more so than reading and writing alone)
and therefore the hand code is not shown.
With ``nonesafe`` it is easy.
Consider a particularly tricky example, suppose we read:

>>> tricky = {'b': None, 'unknown': 'u'}

Then added in ``a.c``:

>>> st = Safe(tricky)
>>> st.a.c = 0

Finally write it out again:

>>> st.todict()
{'b': None, 'unknown': 'u', 'a': {'c': 0}}

There is a lot going on this example:

1. ``a.c`` has been added at the end,
   note it is not in input ``tricky`` hence at end.
2. ``b`` despite being ``None`` is in output,
   because it was in ``tricky``.
   If a field is in the input it is retained;
   even if ``None``, which would normally be trimmed.
3. ``unknown`` is retained, even though ``Safe`` doesn't
   know about this field.
   It is retained because it is in the input.

Details
=======
The function ``nsdict`` makes a shallow copy of it's arguments.
The shallow copy is first made ``dict_fields`` argument and
then updated with the ``kw_fields`` arguments.
Therefore:

>>> Ex = nsdict('Ex', {'a': int}, a=A)

Matches:

>>> Ex({'a': {'c': 0}})
Ex(a=A(c=0))

The function ``nsdict`` is very flexible
(following `Postel
<https://en.wikipedia.org/wiki/Robustness_principle>`_),
the following are all the same as each other:

>>> Ex0 = nsdict('Ex0', {'a': int, 'b': int})
>>> Ex1 = nsdict('Ex1', [('a', int), ('b', int)])
>>> Ex2 = nsdict('Ex2', a=int, b=int)
>>> Ex3 = nsdict('Ex3', {'a': int}, b=int)
>>> Ex4 = nsdict('Ex4', [('a', int)], b=int)

There is a reserved field name ``__orig_values__`` that is
used by ``todict`` to restore values from the original ``dict``.

Like creating a class with``nsdict``; when an instance of
the created class is instantiated,
it too makes a shallow copy of its arguments.
First ``dict_values`` and then ``kw_values``, therefore:

>>> Ex({'a': 0}, a=A(c=0))
Ex(a=A(c=0))

Constructing an instance of a ``nonsafe`` class is also
very flexible (again following `Postel
<https://en.wikipedia.org/wiki/Robustness_principle>`_),
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

Alternatives
============
In general there are a lot of discussions and suggestions in
this space, e.g.:

* `PEP 505 <https://peps.python.org/pep-0505/>`_
* `Revisiting PEP 505
  <https://discuss.python.org/t/revisiting-pep-505/74568>`_
* `PEP 505 is stuck in a circle
  <https://discuss.python.org/t/pep-505-is-stuck-in-a-circle/75423>`_
* `Linked Booleans Logics (rethinking PEP 505)
  <https://discuss.python.org/t/linked-booleans-logics-rethinking-pep-505/78477>`_
* `PEP 505: status?
  <https://discuss.python.org/t/pep-505-status/4612>`_
* `Introducing a Safe Navigation Operator in Python
  <https://discuss.python.org/t/introducing-a-safe-navigation-operator-in-python/35480/2>`_
* `Safe navigation operators by way of expression result queries
  <https://discuss.python.org/t/safe-navigation-operators-by-way-of-expression-result-queries/68066>`_
* `Expressions to handle raising and catching exceptions,
  plus coalescion
  <https://discuss.python.org/t/expressions-to-handle-raising-and-catching-exceptions-plus-coalescion/46048/2>`_
* `None-safe traversal of dictionaries, e.g. from JSON
  <https://discuss.python.org/t/none-safe-traversal-of-dictionaries-e-g-from-json/79045>`_
* `PEP 769: Add a ‘default’ keyword argument to ‘attrgetter’
  and ‘itemgetter’
  <https://discuss.python.org/t/pep-769-add-a-default-keyword-argument-to-attrgetter-and-itemgetter/76419/3>`_
* `New syntax for safe attribute and safe subscript access
  <https://discuss.python.org/t/new-syntax-for-safe-attribute-and-safe-subscript-access/38643/2>`_
* `Questions about '?.' syntax
  <https://discuss.python.org/t/questions-about-syntax/29993/4>`_
* `Using the question mark (?) for inline conditions
  <https://discuss.python.org/t/using-the-question-mark-for-inline-conditions/60155/5>`_
* `Add optional chaining of attributes
  <https://discuss.python.org/t/add-optional-chaining-of-attributes/27089/2>`_

Which demonstrates ``nonesafe``'s value,
but shows there is no consensus.
Therefore, having an officially sanctioned approach,
in ``stdlib``, has value.

``nonsafe`` can be used to read, write, and read/modify/write
external data. For reading only there are alternatives.

Reading
--------
Very similar reading behaviour can be achieved with
packages like
`Pydantic <https://docs.pydantic.dev/latest/>`_,
but they are much too heavyweight for casual use
and their inclusion has previously been rejected
in favour of dataclasses
(`PEP 557 <https://peps.python.org/pep-0557/>`_).

There are many other similar approaches to pydantic:

* `Automatic generation of marshmallow schemas from dataclasses
  <https://github.com/lovasoa/marshmallow_dataclass>`_
* `Simple, elegant,
  wizarding tools for interacting with Python’s dataclasses
  <https://github.com/lovasoa/marshmallow_dataclass>`_
* `Easily serialize Data Classes to and from JSON
  <https://github.com/lovasoa/marshmallow_dataclass>`_
* `Simple creation of data classes from dictionaries
  <https://github.com/lovasoa/marshmallow_dataclass>`_
* `Pandas <https://pandas.pydata.org/>`_

There are also specification languages that parse strings
that specify the data, e.g.:

* `glom <https://github.com/mahmoud/glom>`_
* `JSON Schema
  <https://github.com/python-jsonschema/jsonschema?tab=readme-ov-file>`_

These 'schemas' are generally difficult to use when the data
from the external source changes and you have to specify all
the data and not just the parts you are interested in.

There is also a rejected
`PEP 505 <https://peps.python.org/pep-0505/>`_
and a proposal to revive it
`Revisiting PEP 505
<https://discuss.python.org/t/revisiting-pep-505/74568>`_
that failed to reach a consensus.
505 proposed introducing new ``None`` aware operators
``??`` (same as ``nsget``), ``?.``, and ``?[]``
(last two equivalent to ``nsdict``'s behaviour for ``dict``).
This module is considerably easier to add
than three operators
(current proof on concept circa 100 lines)
and is arguably superior, because it is declarative.
Note operators also need to be added to IDE's,
type-checkers, etc. and need to be taught.
For newbies and none computer-science people they
will be unfamiliar.
There is an advantage with the 505 built in operators,
they delay the evaluation of their right-hand argument.
It is not possible to do this in Python except inside
the compiler (as it does for ``and`` and ``or``).

Writing
-------
`PEP 505 <https://peps.python.org/pep-0505/>`_ has some
capability to write, but cannot write nested data easily.
Each level has to be manually written.

Read/Modify/Write
-----------------
There is nothing available that supports this use case directly,
but you could hand code using other packages or dicts directly.

Summary
-------
There is great interest in this area, but no standard.
There are 3rd party alternatives for reading,
that are large and complicated and some already rejected
because of their size and complication.
There are no good 3rd party or PEP alternatives
available for writing and read/modify/writing.

Personal note
^^^^^^^^^^^^^
My motivation for writing ``nonesafe`` came from a previous
company where we supplied a wrapper around a JSON API
to customers (that was built using dataclasses)
and also from processing data from an internal Asana
database (this code used Pandas).
In both cases the ``nonesafe`` library would have been superior
(but I hadn’t thought of it!).

Possibilities for the future
============================
In no particular order:

1. Check field value is of correct type or ``None``
   (auto-convert if possible).
   JSON data can be painful where ``"0"`` or ``0`` can be
   any of ``bool``, ``float``, or ``int``.
2. ``field`` specifier that allows a custom type converter,
   checkers for things like ranges,
   marking a field as required, and defaults other than ``None``.
3. Allow ``nsdict`` to be used as a class decorator.
   Copy ``docstring`` from decorated classes.
   Add something like ``__post_init__`` to check interrelated
   field values.
4. Add ``a.b.set(‘c’, default)`` - Note ``c`` has to be a
   leaf and is given separately as a  field name as a ``str``,
   used instead of ``a.b.c = nsget(a.b.c, default)``.
5. Use ``__slots__``.
