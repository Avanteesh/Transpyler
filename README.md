# 🧩 Transpyler

> A tiny experimental programming language that **transpiles to Python** — built to explore parsing, AST transformation, and language design.

---

## 🚀 Overview

**Transpyler** is a mini compiler / DSL engine written entirely in Python.  
It takes source code written in a **custom syntax**, parses it into an **Abstract Syntax Tree (AST)**, and then **unparses** it back into executable Python code.

Think of it as a language that sits *on top of Python* — allowing you to experiment with language ideas, syntax rules, and compiler design, without worrying about bytecode or C-level runtimes.


---

## 🧠 How It Works

Below is the architecture of how Transpyler turns your custom syntax into Python:

```text
┌────────────────────────┐
│     Source Code (.rpy)  │
│  (rpy language)   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  Lexer / Tokenizer     │
│ Splits code into tokens│
└────────────┬───────────┘
             │
             ▼
┌─────────────────────────┐
│   Parser / AST Builder  │
│  Builds syntax tree     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   AST Translator        │
│ Converts nodes to Python│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Python Code Generator  │
│ Writes runnable .py file│
└────────────┬────────────┘
             │
             ▼
┌──────────────────────────┐
│    Python Interpreter    │
│ Runs your transpiled code│
└──────────────────────────┘
```


# Tests

## test one
  sample code: 
```text
matrix <- [[1,2,3],[4,5,6],[7,8,9]];

puts("Matrix: ", matrix);
```

translated python code
```python
 matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
puts('Matrix: ', matrix) 
````


## test two

sample code:
```text
mutable struct Person do
  name;
  age;
done

struct Account do
  acc_id;
  account_owner;
done
```

translated python code:
all dependencies are added into the python's global namespace
```python
 @dataclass
class Person:
    name: Any = field(default_factory=Null)
    age: Any = field(default_factory=Null)

@dataclass(frozen=True)
class Account:
    acc_id: Any = field(default_factory=Null)
    account_owner: Any = field(default_factory=Null)
```

