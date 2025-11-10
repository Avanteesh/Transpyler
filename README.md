# 🧩 Transpyler

> A tiny experimental programming language that **transpiles to Python** — built to explore parsing, AST transformation, and language design.

---

## 🚀 Overview

**Transpyler** is a mini compiler / DSL engine written entirely in Python.  
It takes source code written in a **custom syntax**, parses it into an **Abstract Syntax Tree (AST)**, and then **unparses** it back into executable Python code.

Think of it as a language that sits *on top of Python* — allowing you to experiment with language ideas, syntax rules, and compiler design, without worrying about bytecode or C-level runtimes.

---

## 🧠 How It Works

Below is a simplified flow of how Transpyler turns your custom syntax into Python:

```text
┌────────────────────────┐
│     Source Code (.tl)  │
│  (your DSL language)   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  Lexer / Tokenizer     │
│ Splits code into tokens│
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│   Parser / AST Builder │
│  Builds syntax tree     │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│   AST Translator       │
│ Converts nodes to Python│
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  Python Code Generator │
│ Writes runnable .py file│
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│    Python Interpreter  │
│ Runs your transpiled code│
└────────────────────────┘
