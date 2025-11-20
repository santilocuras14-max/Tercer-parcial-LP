# 2. Gramática para un lenguaje de producto punto entre matrices

El objetivo es diseñar una **gramática** para un lenguaje que permita:

- Declarar matrices con dimensiones explícitas.
- Inicializarlas con literales.
- Realizar el **producto punto (multiplicación de matrices)** entre matrices de dimensiones compatibles.
- Asignar el resultado a variables y opcionalmente imprimirlo.

## 2.1. Ideas de diseño del lenguaje

Ejemplos de programas válidos:

```text
matrix A[2,3] = [[1,2,3],[4,5,6]];
matrix B[3,2] = [[7,8],[9,10],[11,12]];
C = A * B;
print C;
```

Reglas de compatibilidad:

- Si `A` es de dimensión `(m x n)` y `B` de dimensión `(p x q)`, el producto `A * B` es válido si `n = p`.
- El resultado será de dimensión `(m x q)`.

La **validación de dimensiones** la hacemos con atributos / acciones semánticas, no en la gramática pura libre de contexto.

---

## 2.2. Gramática (BNF)

```bnf
<Program>       ::= <StmtList> EOF

<StmtList>      ::= <Stmt> ";"
                  | <Stmt> ";" <StmtList>

<Stmt>          ::= <MatrixDecl>
                  | <AssignStmt>
                  | <PrintStmt>

<MatrixDecl>    ::= "matrix" ID "[" INT "," INT "]" "=" <MatrixLiteral>

<AssignStmt>    ::= ID "=" <Expr>

<PrintStmt>     ::= "print" ID

<Expr>          ::= <Term>
                  | <Expr> "*" <Term>

<Term>          ::= ID
                  | <MatrixLiteral>
                  | "(" <Expr> ")"

<MatrixLiteral> ::= "[" <RowList> "]"

<RowList>       ::= <Row>
                  | <Row> "," <RowList>

<Row>           ::= "[" <IntList> "]"

<IntList>       ::= INT
                  | INT "," <IntList>
```

### Tokens principales

- Palabras reservadas:
  - `matrix`
  - `print`
- Símbolos:
  - `=`, `*`, `[`, `]`, `,`, `;`, `(`, `)`
- Identificadores:
  - `ID`
- Números enteros:
  - `INT`

---

## 2.3. Atributos para validación de dimensiones

Para comprobar que `A * B` es válido y para saber la dimensión del resultado, proponemos
los siguientes atributos:

- Para `Expr` y `Term`:
  - `rows` (sintético): número de filas de la matriz resultante.
  - `cols` (sintético): número de columnas de la matriz resultante.
  - `ok` (sintético, booleano): indica si la expresión es semánticamente válida.

- Para declaraciones de matrices:
  - `MatrixDecl.name` (sintético): nombre del identificador.
  - Almacenamos en una tabla de símbolos: `symtab[name] = (rows, cols, value)`.

### Reglas semánticas (idea)

Producción:

```bnf
<Expr> ::= <Expr> "*" <Term>
```

Reglas:

- Si `Expr1` tiene atributos `(rows1, cols1)` y `Term` `(rows2, cols2)`,
- El producto es válido si `cols1 = rows2`.
- En ese caso:
  - `Expr.rows = rows1`
  - `Expr.cols = cols2`
  - `Expr.ok = Expr1.ok ∧ Term.ok ∧ (cols1 = rows2)`
- Si no se cumple:
  - `Expr.ok = false`
  - Se reporta error de incompatibilidad de dimensiones.

Producción:

```bnf
<Term> ::= ID
```

Reglas:

- Buscamos `ID` en la tabla de símbolos:
  - Si no existe: error de variable no declarada.
  - Si existe: `Term.rows, Term.cols` se toman de la tabla de símbolos.

Producción:

```bnf
<MatrixDecl> ::= "matrix" ID "[" INT "," INT "]" "=" <MatrixLiteral>
```

Reglas:

- Se guardan las dimensiones declaradas:
  - `rows = INT1.value`
  - `cols = INT2.value`
- (Opcional) Se valida que el literal concuerde con esas dimensiones.
- Se inserta en la tabla de símbolos: `symtab[ID.lexeme] = (rows, cols, matrix_value)`.

---

## 2.4. Relación con la gramática ANTLR

La gramática BNF anterior se traduce casi directamente a una gramática ANTLR4 (`MatrixLang.g4`)
que:

- Define las mismas reglas sintácticas (`program`, `stmt`, `expr`, `term`, etc.).
- Usa un **visitor** en Python para implementar:
  - Tabla de símbolos.
  - Validación de dimensiones.
  - Cálculo del producto matriz-matriz.