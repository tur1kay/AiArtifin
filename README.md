# PyArtifIn 📦

[![PyPI version](https://badge.fury.io/py/pyartifin.svg)](https://pypi.org/project/pyartifin/)
[![License: MIT](https://shields.io)](https://opensource.org)

`PyArtifIn` is a powerful Python library and CLI tool that leverages AI to **write and automatically execute code**. Just describe your task in natural language, and the neural network does the rest — from generation to execution.

Developed for vibe-coders who want to build fast without paying for premium AI subscriptions. Powered by **Ollama Cloud / Local API**.

---

## 🚀 Key Features

* **Code & Run:** Don't just generate text. Create, write, and execute scripts in one go.
* **Dual Mode:** Use it directly in your terminal (CLI) or import it as a standard Python module.
* **Zero Cost:** Plug in your Ollama API key and generate as much code as you want.

---

## 🛠️ Installation

Install the package via `pip`:

```bash
pip install pyartifin
```

---

## 💻 CLI Usage

You can invoke `pyartifin` directly from your command line (CMD, PowerShell, or Terminal):

```bash
pyartifin "Hello! Write Hello World in C++"
```

---

## ⚙️ Configuration & Environment Variables

To use the tool globally via CLI, set your Ollama Cloud API key:

### 🪟 Windows
```cmd
set OLLAMA_API_KEY=your_api_key_ollama_cloud
```

### 🐧 Linux / 🍏 Mac
```bash
export OLLAMA_API_KEY=your_api_key_ollama_cloud
```

---

## 🐍 Python API Example

Use the library inside your own automation scripts. The `safe_run` method automatically creates the file and executes the generated code:

```python
import pyartifin as ai

# Initialize the AI client
art = ai.PyArtifIn(api_key="YOUR_API_KEY_OLLAMA_CLOUD")

# Generate, write to "myscript.py", and run it automatically
art.safe_run("myscript.py", "напиши программу для сортировки списка")
```

---

## 📄 License

This project is licensed under the **MIT License**. See the full text below:

```text
Copyright (c) 2026 tur1kay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👤 Author

Created with 💻 by **tur1kay**
