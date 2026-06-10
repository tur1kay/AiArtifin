import sys
import argparse
from pyartifin import PyArtifIn

def main():
    parser = argparse.ArgumentParser(
        description="PyArtifIn - AI-powered code generator and executor",
        epilog="Примеры:\n"
               "  python -m pyartifin 'напиши hello world'\n"
               "  python -m pyartifin 'создай калькулятор' --save calc.py\n"
               "  python -m pyartifin 'вывести числа от 1 до 10' --lang cpp"
    )
    
    parser.add_argument(
        "prompt",
        help="Описание задачи на естественном языке"
    )
    
    parser.add_argument(
        "--lang", "-l",
        default="python",
        help="Язык программирования (по умолчанию: python)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gpt-oss:120b-cloud",
        help="Модель для генерации"
    )
    
    parser.add_argument(
        "--save", "-s",
        metavar="FILENAME",
        help="Сохранить код в файл (создаст резервную копию)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API-ключ (или установи переменную OLLAMA_API_KEY)"
    )
    
    parser.add_argument(
        "--base-url",
        default="https://ollama.com/v1",
        help="Base URL для API (по умолчанию: https://ollama.com/v1)"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.3,
        help="Температура (креативность) 0.1-0.5 (по умолчанию: 0.3)"
    )
    
    args = parser.parse_args()
    
    # Создаём экземпляр
    art = PyArtifIn(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model
    )
    
    if args.save:
        # Сохраняем в файл с бэкапом
        result = art.safe_run(
            filename=args.save,
            prompt=args.prompt,
            language=args.lang
        )
        print(f"✅ Код сохранён в {result}")
    else:
        # Генерируем и выполняем
        result = art.run(
            prompt=args.prompt,
            language=args.lang,
            use_cache=True
        )
        print(result)

if __name__ == "__main__":
    main()

