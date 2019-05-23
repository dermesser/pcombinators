# pcombinators

Working on parser combinators for Python, in an understandable manner. I've
always been fascinated by them, so I wanted to try if I can implement them :-)

There are examples in the form of
* a JSON parser in `pcombinators/json_test.py` and
* a parser for arithmetic expressions in `pcombinators/arith_test.py`.

More simple examples:

```python

import pcombinators.combinators as c

st = c.ParseState('Hello, World!')
p = c.String('Hello') + c.Regex('([,.]) +') + c.String('World') + c.Regex('[.,?!]')

p.parse(st)
# >> (['Hello', ',', 'World', '!'], ParseState(Hello, World!<>))<Paste>

# '+' constructs AtomicSequence() parsers, which only succeed if every parser succeeds in order
# (OptimisticSequence() just goes as far as it can). Sequence parsers result in a list of the
# individual parsers' results.
#
# Skip(p) makes the result of a parser disappear; useful when you need to consume input but not use
# it after. Without Skip, an empty string would appear in the result list.
(Float() + Skip(String(" ")) + NonEmptyString()).parse(ParseState('1.22 abc'))
# >> ([1.22, 'abc'], ParseState(1.22 abc<>))

def upper(s):
    return s.upper()

# You can transform parser results with the >> (right shift) operator, and
# repeat parsers with the * (multiplication) operator. Note that Repeat() and StrictRepeat() offer
# finer control over the behavior.

# Parse two non-whitespace strings, converting them to uppercase, and a float,
# multiplying the latter by 2.
(
 (NonEmptyString() >> upper) * 2 +
 (Float() >> (lambda f: f * 2))
).parse(ParseState("hello world 2.2"))
# >> (['HELLO', 'WORLD', 4.4], ParseState(hello world 2.2<>))
```

NOTE: pcombinators is super slow right now... it could likely benefit from tightening parsers and
making fewer calls to sub-parsers. Production use isn't quite recommended :)

## Performance tips

* Cache parsers instead of reconstructing them (usually only slight impact)
* Push parsers upwards: `Skip(Whitespace()).then(A() | B() | C())` is a lot cheaper than
`Skip(Whitespace()).then(A()) | ...` because the need for backtracking is greatly reduced.
 * Or remove all whitespace before starting to parse. This is saving A LOT of time.
* Write native parsers for frequently occurring strings. See `primitives.py` for a canonical and a
 fast implementation of integer and float parsing.

