# pyartifin.py
import os
from openai import OpenAI
from typing import Optional

class PyArtifIn:
    def __init__(self, 
                 api_key: str = "", 
                 base_url: str = "https://ollama.com/v1", 
                 model: str = "gpt-oss:120b-cloud"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model
    
    def generate(self, 
                 prompt: str, 
                 language: str = "python",
                 temperature: float = 0.3) -> str:
        system_prompt = f"""
        You are a code generator. Your task is to write only {language} code without any extra words.
        Do not write any explanations, do not use ```python ... ```, only pure code.
        The code must be working and safe.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"# Generation error: {e}"
    
    def run(self, 
            prompt: str, 
            language: str = "python",
            variables: dict = None) -> any:
        code = self.generate(prompt, language)
        print(f"📦 Generated code:\n{code}\n{'-'*40}")
        
        if language != "python":
            return code
        
        exec_globals = variables or {}
        try:
            exec(code, exec_globals)
            return exec_globals.get('result', '✅ Code executed, but result variable not found')
        except Exception as e:
            return f"❌ Execution error: {e}"
