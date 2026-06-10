import sys
import os
import hashlib
import subprocess
import shutil
import argparse
from io import StringIO
from typing import Optional, Dict, List, Any

# Проверка и установка зависимостей
try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("📦 Installing required package: openai")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI, AsyncOpenAI

try:
    from RestrictedPython import safe_globals
except ImportError:
    print("📦 Installing required package: RestrictedPython")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "RestrictedPython"])
    from RestrictedPython import safe_globals


class PyArtifIn:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-oss:120b-cloud",
        fallback_models: Optional[List[str]] = None,
        local_mode: bool = False
    ):
        # Определяем режим работы
        if local_mode or (base_url is None and api_key is None):
            # Локальный режим
            self.base_url = base_url or os.environ.get("OLLAMA_LOCAL_URL", "http://localhost:11434")
            self.api_key = "ollama"  # заглушка, локальная Ollama не требует ключа
        else:
            # Облачный режим
            if api_key is None:
                api_key = os.environ.get("OLLAMA_API_KEY") or os.environ.get("OPENAI_API_KEY")
                if api_key is None:
                    raise ValueError(
                        "API key not found. Pass it to PyArtifIn or set OLLAMA_API_KEY / OPENAI_API_KEY environment variable."
                    )
            self.base_url = base_url or "https://ollama.com/v1"
            self.api_key = api_key
        
        self.model = model
        self.fallback_models = fallback_models or []
        self._cache: Dict[str, str] = {}
        self._context: Dict[str, List[Dict[str, str]]] = {}
        
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.async_client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
    
    def _get_cache_key(self, prompt: str, language: str, temperature: float) -> str:
        content = f"{prompt}|{language}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate(self, prompt: str, language: str = "python", temperature: float = 0.3,
                 use_cache: bool = True, model: Optional[str] = None) -> str:
        cache_key = self._get_cache_key(prompt, language, temperature)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        system_prompt = f"""
        You are a code generator. Your task is to write only {language} code without any extra words.
        Do not write any explanations, do not use ```python ... ```, only pure code.
        The code must be working and safe.
        """
        
        models_to_try = [model or self.model] + self.fallback_models
        last_error = None
        for current_model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                code = response.choices[0].message.content.strip()
                if use_cache:
                    self._cache[cache_key] = code
                return code
            except Exception as e:
                last_error = e
                print(f"⚠️ Model {current_model} failed: {e}")
                continue
        
        raise last_error or Exception("No model available to generate code")
    
    async def agenerate(self, prompt: str, language: str = "python", temperature: float = 0.3,
                        model: Optional[str] = None) -> str:
        cache_key = self._get_cache_key(prompt, language, temperature)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        system_prompt = f"""
        You are a code generator. Your task is to write only {language} code without any extra words.
        Do not write any explanations, do not use ```python ... ```, only pure code.
        The code must be working and safe.
        """
        
        models_to_try = [model or self.model] + self.fallback_models
        last_error = None
        for current_model in models_to_try:
            try:
                response = await self.async_client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                code = response.choices[0].message.content.strip()
                self._cache[cache_key] = code
                return code
            except Exception as e:
                last_error = e
                print(f"⚠️ Model {current_model} failed: {e}")
                continue
        
        raise last_error or Exception("No model available to generate code")
    
    def run(self, prompt: str, language: str = "python", variables: Optional[Dict[str, Any]] = None,
            chat_id: Optional[str] = None, use_cache: bool = True, model: Optional[str] = None) -> str:
        code = self.generate(prompt, language, use_cache=use_cache, model=model)
        print(f"📦 Generated code:\n{code}\n{'-'*40}")
        
        if language != "python":
            return code
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        exec_globals = safe_globals.copy() if 'safe_globals' in dir() else {}
        exec_globals.update(variables or {})
        exec_globals['__builtins__'] = {
            'print': print, 'len': len, 'range': range, 'int': int, 'str': str,
            'float': float, 'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
            'set': set, 'abs': abs, 'sum': sum, 'min': min, 'max': max, 'round': round,
            'enumerate': enumerate, 'zip': zip, 'isinstance': isinstance, 'type': type,
            'ValueError': ValueError, 'TypeError': TypeError, 'KeyError': KeyError, 'IndexError': IndexError,
        }
        
        try:
            exec(code, exec_globals)
            result = sys.stdout.getvalue()
            return result if result else "✅ Code executed, but no output produced"
        except Exception as e:
            return f"❌ Execution error: {e}"
        finally:
            sys.stdout = old_stdout
    
    async def arun(self, prompt: str, language: str = "python", variables: Optional[Dict[str, Any]] = None,
                   chat_id: Optional[str] = None, model: Optional[str] = None) -> str:
        code = await self.agenerate(prompt, language, model=model)
        print(f"📦 Generated code:\n{code}\n{'-'*40}")
        
        if language != "python":
            return code
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        exec_globals = safe_globals.copy() if 'safe_globals' in dir() else {}
        exec_globals.update(variables or {})
        exec_globals['__builtins__'] = {
            'print': print, 'len': len, 'range': range, 'int': int, 'str': str,
            'float': float, 'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
            'set': set, 'abs': abs, 'sum': sum, 'min': min, 'max': max, 'round': round,
            'enumerate': enumerate, 'zip': zip, 'isinstance': isinstance, 'type': type,
        }
        
        try:
            exec(code, exec_globals)
            result = sys.stdout.getvalue()
            return result if result else "✅ Code executed, but no output produced"
        except Exception as e:
            return f"❌ Execution error: {e}"
        finally:
            sys.stdout = old_stdout
    
    def safe_run(self, filename: str, prompt: str, language: str = "python",
                 variables: Optional[Dict[str, Any]] = None, max_backups: int = 5) -> str:
        code = self.generate(prompt, language)
        
        if os.path.exists(filename):
            for i in range(max_backups - 1, 0, -1):
                old = f"{filename}.backup{i}"
                new = f"{filename}.backup{i+1}"
                if os.path.exists(old):
                    shutil.move(old, new)
            shutil.move(filename, f"{filename}.backup1")
            print(f"📁 Backup created: {filename}.backup1")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ Code saved to {filename}")
            return filename
        except Exception as e:
            return f"❌ Save error: {e}"
    
    def clear_cache(self) -> None:
        self._cache.clear()
    
    def clear_context(self, chat_id: Optional[str] = None) -> None:
        if chat_id:
            self._context.pop(chat_id, None)
        else:
            self._context.clear()


# ========== CLI ==========

def parse_args():
    parser = argparse.ArgumentParser(
        description="PyArtifIn - AI-powered code generator and executor",
        epilog="Examples:\n"
               "  pyartifin-cloud 'напиши hello world'    # cloud mode\n"
               "  pyartifin-local 'напиши hello world'    # local mode"
    )
    parser.add_argument("prompt", help="Task description in natural language")
    parser.add_argument("--lang", "-l", default="python", help="Programming language")
    parser.add_argument("--model", "-m", default="gpt-oss:120b-cloud", help="Model to use")
    parser.add_argument("--save", "-s", metavar="FILENAME", help="Save code to file (with backups)")
    parser.add_argument("--api-key", help="API key (or set OLLAMA_API_KEY)")
    parser.add_argument("--base-url", help="Base URL for API")
    parser.add_argument("--temperature", "-t", type=float, default=0.3, help="Temperature 0.1-0.5")
    return parser.parse_args()


def main_cloud():
    args = parse_args()
    art = PyArtifIn(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model
    )
    _run_cli(art, args)


def main_local():
    args = parse_args()
    art = PyArtifIn(local_mode=True, model=args.model)
    _run_cli(art, args)


def _run_cli(art: PyArtifIn, args):
    if args.save:
        result = art.safe_run(args.save, args.prompt, language=args.lang)
        print(result)
    else:
        result = art.run(args.prompt, language=args.lang, use_cache=True)
        print(result)


if __name__ == "__main__":
    # Определяем режим по имени команды
    script_name = os.path.basename(sys.argv[0])
    if "local" in script_name:
        main_local()
    else:
        main_cloud()
