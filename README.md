[![PyPI version](https://badge.fury.io/py/pyartifin.svg)](https://pypi.org/project/pyartifin/)
# PyArtifIn

PyArtifIn is a Python library that writes and executes code using AI. Just describe your task in Russian (or our languages), and the neural network does everything for you.

## CLI

pyartifin "Hello! Write Hello World in C++"

## Installation

pip install pyartifin
# Environment variables
set OLLAMA_API_KEY=you_api_key_ollama_cloud # for Windows
export OLLAMA_API_KEY=you_api_key_ollama_cloud # for linux Debian-based, RedHat-based, Arch-based (and mac)

## Example

import pyartifin as ai
art = ai.PyArtifIn(api_key="API_KEY_OLLAMA_CLOUD")
art.safe_run("myscript.py", "напиши программу для сортировки списка")

## License

MIT License

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

## Author

tur1kay
