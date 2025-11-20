# Lenguaje SQL-CRUD y Lenguaje de Producto Punto de Matrices (ANTLR4 / Python)

Este repositorio contiene la solución a los numerales:

1. Función que modela una **gramática de atributos** para un mini lenguaje de consultas tipo SQL (operaciones CRUD).
2. Diseño de una **gramática** para un lenguaje de programación capaz de resolver el **producto punto (multiplicación de matrices)** entre dos matrices de dimensiones compatibles.
3. Implementación en **ANTLR4** de la gramática del punto 2, con **lenguaje objetivo Python**.

## Estructura del repo

- `doc/sql_attr_grammar.md`  
  Modelo de función y especificación de **gramática de atributos** para un lenguaje tipo SQL CRUD.

- `doc/matrix_language_design.md`  
  Diseño de la gramática (BNF) para el lenguaje de producto punto de matrices.

- `grammar/MatrixLang.g4`  
  Gramática ANTLR4 del lenguaje de matrices (punto 2), objetivo Python.

- `src/MatrixEvaluator.py`  
  Visitante en Python que evalúa expresiones de matrices y realiza la multiplicación, validando dimensiones.

- `src/main.py`  
  Punto de entrada de ejemplo que usa el parser generado por ANTLR4 para interpretar un archivo de programa.

## Cómo usarlo

1. Instalar ANTLR4 y el runtime de Python:

   ```bash
   pip install antlr4-python3-runtime
   ```

2. Generar el parser (desde la carpeta `grammar/`):

   ```bash
   antlr4 -Dlanguage=Python3 MatrixLang.g4 -visitor -o ../src/gen
   ```

3. Ejecutar un programa de ejemplo:

   ```bash
   python src/main.py ejemplo.mtx
   ```

Crea tu propio repositorio en GitHub y sube el contenido de este proyecto.