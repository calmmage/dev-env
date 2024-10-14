#!/bin/zsh runp
if __name__ == "__main__":
    import deepl
    import calmlib
    import langchain
    from pydantic_settings import BaseSettings
    from loguru import logger
    import typer
    import pydantic

    print("This is the main script")
    print("deepl version:", deepl.__version__)
    print("calmlib version:", calmlib.__version__)
    # print("langchain version:", langchain.__version__)
    print("pydantic version:", pydantic.__version__)

    print("typer version:", typer.__version__)
