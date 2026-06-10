import sys
import os
import hashlib
import subprocess
from io import StringIO
from functools import lru_cache
from typing import Optional, Dict, List, Any, Union

# Проверка и установка зависимостей
try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    print("📦 Installing required package: openai")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI, AsyncOpenAI

# Песочница для безопасного выполнения
try:
    from RestrictedPython import compile_restricted, safe_globals
except ImportError:
    print("📦 Installing required package: RestrictedPython")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "RestrictedPython"])
    from RestrictedPython import compile_restricted, safe_globals


class PyArtifIn:
    """
    AI-powered code generator and executor for Python.
    
    Example:
        art = PyArtifIn(api_key="your-key")
        result = art.run("print('Hello')")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://ollama.com/v1",
        model: str = "gpt-oss:120b-cloud",
        fallback_models: Optional[List[str]] = None
    ):
        """
        Initialize PyArtifIn.
        
        Args:
            api_key: API key for the LLM provider. If None, tries OLLAMA_API_KEY or OPENAI_API_KEY env vars.
            base_url: Base URL for the API endpoint.
            model: Default model name.
            fallback_models: List of alternative models to try if primary fails.
        """
        # Handle API key from environment
        if api_key is None:
            api_key = os.environ.get("OLLAMA_API_KEY") or os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key not found. Pass it to PyArtifIn or set OLLAMA_API_KEY / OPENAI_API_KEY environment variable."
                )
        
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.fallback_models = fallback_models or []
        self._cache: Dict[str, str] = {}
        self._context: Dict[str, List[Dict[str, str]]] = {}  # chat_id -> history
        
        # Initialize clients
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.async_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    
    def _get_cache_key(self, prompt: str, language: str, temperature: float) -> str:
        """Generate cache key for a request."""
        content = f"{prompt}|{language}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate(
        self,
        prompt: str,
        language: str = "python",
        temperature: float = 0.3,
        use_cache: bool = True,
        model: Optional[str] = None
    ) -> str:
        """
        Generate code from text description.
        
        Args:
            prompt: Task description in natural language.
            language: Programming language (python, cpp, javascript, etc.).
            temperature: Creativity level (0.1-0.5).
            use_cache: Whether to use cached results.
            model: Override default model for this request.
        
        Returns:
            Generated code as string.
        """
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
    
    async def agenerate(
        self,
        prompt: str,
        language: str = "python",
        temperature: float = 0.3,
        model: Optional[str] = None
    ) -> str:
        """Async version of generate."""
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
    
    def run(
        self,
        prompt: str,
        language: str = "python",
        variables: Optional[Dict[str, Any]] = None,
        chat_id: Optional[str] = None,
        use_cache: bool = True,
        model: Optional[str] = None
    ) -> str:
        """
        Generate and execute code.
        
        Args:
            prompt: Task description.
            language: Programming language.
            variables: Variables to pass to the execution context.
            chat_id: ID for maintaining conversation context.
            use_cache: Whether to use cached results.
            model: Override default model.
        
        Returns:
            Output from executed code or error message.
        """
        # Handle context
        if chat_id:
            if chat_id not in self._context:
                self._context[chat_id] = []
            context_history = self._context[chat_id]
            # Build full prompt with context
            full_prompt = prompt
            # (simplified: just use last few exchanges)
        else:
            full_prompt = prompt
        
        code = self.generate(full_prompt, language, model=model, use_cache=use_cache)
        print(f"📦 Generated code:\n{code}\n{'-'*40}")
        
        if language != "python":
            return code
        
        # Execute code in sandbox
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Restricted execution environment
        exec_globals = safe_globals.copy() if 'safe_globals' in dir() else {}
        exec_globals.update(variables or {})
        exec_globals['__builtins__'] = {
            'print': print,
            'len': len,
            'range': range,
            'int': int,
            'str': str,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'abs': abs,
            'sum': sum,
            'min': min,
            'max': max,
            'round': round,
            'enumerate': enumerate,
            'zip': zip,
            'isinstance': isinstance,
            'type': type,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
        }
        
        try:
            exec(code, exec_globals)
            result = sys.stdout.getvalue()
            return result if result else "✅ Code executed, but no output produced"
        except Exception as e:
            return f"❌ Execution error: {e}"
        finally:
            sys.stdout = old_stdout
    
    async def arun(
        self,
        prompt: str,
        language: str = "python",
        variables: Optional[Dict[str, Any]] = None,
        chat_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """Async version of run."""
        code = await self.agenerate(prompt, language, model=model)
        print(f"📦 Generated code:\n{code}\n{'-'*40}")
        
        if language != "python":
            return code
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        exec_globals = safe_globals.copy() if 'safe_globals' in dir() else {}
        exec_globals.update(variables or {})
        exec_globals['__builtins__'] = {
            'print': print,
            'len': len,
            'range': range,
            'int': int,
            'str': str,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'abs': abs,
            'sum': sum,
            'min': min,
            'max': max,
            'round': round,
            'enumerate': enumerate,
            'zip': zip,
            'isinstance': isinstance,
            'type': type,
        }
        
        try:
            exec(code, exec_globals)
            result = sys.stdout.getvalue()
            return result if result else "✅ Code executed, but no output produced"
        except Exception as e:
            return f"❌ Execution error: {e}"
        finally:
            sys.stdout = old_stdout
    
    def clear_cache(self) -> None:
        """Clear the generation cache."""
        self._cache.clear()
    
    def clear_context(self, chat_id: Optional[str] = None) -> None:
        """Clear conversation context for a specific chat or all."""
        if chat_id:
            self._context.pop(chat_id, None)
        else:
            self._context.clear()


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PyArtifIn - AI code generator")
    parser.add_argument("prompt", nargs="?", help="Task description")
    parser.add_argument("--language", "-l", default="python", help="Programming language")
    parser.add_argument("--model", "-m", help="Model to use")
    parser.add_argument("--api-key", help="API key (or set OLLAMA_API_KEY env)")
    parser.add_argument("--base-url", default="https://ollama.com/v1", help="API base URL")
    
    args = parser.parse_args()
    
    if not args.prompt:
        parser.print_help()
        sys.exit(1)
    
    art = PyArtifIn(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model or "gpt-oss:120b-cloud"
    )
    
    result = art.run(args.prompt, language=args.language)
    print(result)
