# src/main.py
#
# Ejemplo de uso del parser y visitante para ejecutar un programa MatrixLang.
#
# Uso:
#   python src/main.py ejemplo.mtx
#
# Requiere:
#   - Instalar antlr4-python3-runtime
#   - Generar los archivos en src/gen con:
#       antlr4 -Dlanguage=Python3 grammar/MatrixLang.g4 -visitor -o src/gen

import sys
from antlr4 import FileStream, CommonTokenStream

from gen.MatrixLangLexer import MatrixLangLexer
from gen.MatrixLangParser import MatrixLangParser
from MatrixEvaluator import MatrixEvaluator


def run_file(path: str):
    input_stream = FileStream(path, encoding="utf-8")
    lexer = MatrixLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = MatrixLangParser(stream)

    tree = parser.program()
    evaluator = MatrixEvaluator()
    evaluator.visit(tree)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <archivo.mtx>")
        sys.exit(1)
    run_file(sys.argv[1])