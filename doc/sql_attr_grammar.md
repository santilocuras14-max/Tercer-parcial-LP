# 1. Función que genera una gramática de atributos para un lenguaje tipo SQL (CRUD)

El objetivo es modelar una **función** que, dado un esquema de base de datos, construya una
**gramática de atributos** para un mini lenguaje de consultas SQL con operaciones CRUD:

- `SELECT`
- `INSERT`
- `UPDATE`
- `DELETE`

La idea es separar:

- **Gramática sintáctica** (producciones)
- **Atributos** (sintéticos y heredados)
- **Reglas semánticas** asociadas a cada producción

---

## 1.1. Gramática sintáctica base

Usamos una gramática simplificada (tipo BNF) para ilustrar:

```bnf
<Program>      ::= <StmtList>

<StmtList>     ::= <Stmt> ";" <StmtList>
                 | <Stmt>

<Stmt>         ::= <SelectStmt>
                 | <InsertStmt>
                 | <UpdateStmt>
                 | <DeleteStmt>

<SelectStmt>   ::= "SELECT" <SelectList> "FROM" <TableRef> <WhereOpt>

<SelectList>   ::= "*"
                 | <ColList>

<ColList>      ::= <ColRef> ("," <ColRef>)*

<TableRef>     ::= ID

<WhereOpt>     ::= "WHERE" <BoolExpr>
                 | ε

<BoolExpr>     ::= <BoolExpr> "AND" <BoolExpr>
                 | <BoolExpr> "OR"  <BoolExpr>
                 | "(" <BoolExpr> ")"
                 | <ColRef> <RelOp> <Literal>

<RelOp>        ::= "=" | "<>" | "<" | ">" | "<=" | ">="

<InsertStmt>   ::= "INSERT" "INTO" <TableRef> "(" <ColList> ")" "VALUES" "(" <ExprList> ")"

<ExprList>     ::= <Expr> ("," <Expr>)*

<Expr>         ::= <Literal>
                 | <ColRef>

<UpdateStmt>   ::= "UPDATE" <TableRef> "SET" <AssignList> <WhereOpt>

<AssignList>   ::= <Assign> ("," <Assign>)*

<Assign>       ::= <ColRef> "=" <Expr>

<DeleteStmt>   ::= "DELETE" "FROM" <TableRef> <WhereOpt>

<ColRef>       ::= ID

<Literal>      ::= INT
                 | STRING
```

---

## 1.2. Atributos propuestos

Para capturar la semántica y validar el uso del esquema, proponemos que
los principales no terminales contengan los siguientes atributos:

- `env` (heredado):  
  Entorno con metadatos de tablas y columnas.  
  Ejemplo: `env.tables["clientes"] = {"id": "INT", "nombre": "STRING"}`

- `ok` (sintético, booleano):  
  Indica si la subexpresión es semánticamente válida.

- `errors` (sintético, lista de strings):  
  Lista de mensajes de error semántico.

- `type` (sintético):  
  Tipo de expresión (INT, STRING, BOOL, etc.) cuando aplique.

- `sql` (sintético, string):  
  Representación canónica de la consulta (útil para reescritura, pretty-printing o generación).

Ejemplo de atributos por no terminal:

| No terminal   | Atributos                                       |
|---------------|-------------------------------------------------|
| `Program`     | `env^H`, `ok^S`, `errors^S`                     |
| `Stmt`        | `env^H`, `ok^S`, `errors^S`, `sql^S`            |
| `SelectStmt`  | `env^H`, `ok^S`, `errors^S`, `sql^S`            |
| `InsertStmt`  | `env^H`, `ok^S`, `errors^S`, `sql^S`            |
| `UpdateStmt`  | `env^H`, `ok^S`, `errors^S`, `sql^S`            |
| `DeleteStmt`  | `env^H`, `ok^S`, `errors^S`, `sql^S`            |
| `TableRef`    | `env^H`, `ok^S`, `errors^S`, `name^S`           |
| `ColRef`      | `env^H`, `ok^S`, `errors^S`, `name^S`, `type^S` |
| `BoolExpr`    | `env^H`, `ok^S`, `errors^S`, `type^S`, `sql^S`  |
| `Expr`        | `env^H`, `ok^S`, `errors^S`, `type^S`, `sql^S`  |

---

## 1.3. Reglas semánticas (ejemplos)

### 1.3.1. Resolución de tablas y columnas

Producción:

```bnf
<TableRef> ::= ID
```

Reglas:

- `TableRef.env` es heredado desde el contexto superior (por ejemplo, `SelectStmt.env`).
- Si `ID.lexeme` no está en `TableRef.env.tables`, entonces:
  - `TableRef.ok = false`
  - `TableRef.errors = ["Tabla no definida: " + ID.lexeme]`
- En caso contrario:
  - `TableRef.ok = true`
  - `TableRef.errors = []`
- `TableRef.name = ID.lexeme`

---

Producción:

```bnf
<ColRef> ::= ID
```

Reglas:

- `ColRef.env` es heredado desde la sentencia que usa la columna.
- Si existe una tabla actual `t_actual` en contexto:
  - Si `ID.lexeme` ∉ `env.tables[t_actual]`:
    - `ColRef.ok = false`
    - `ColRef.errors = ["Columna no definida: " + ID.lexeme + " en tabla " + t_actual]`
  - En caso contrario:
    - `ColRef.ok = true`
    - `ColRef.errors = []`
    - `ColRef.type = env.tables[t_actual][ID.lexeme]` (tipo de la columna)

La información de `t_actual` puede ser heredada desde `SelectStmt` o `UpdateStmt`.

---

### 1.3.2. Tipado de expresiones

Producción:

```bnf
<BoolExpr> ::= <ColRef> <RelOp> <Literal>
```

Reglas:

- `BoolExpr.env` es heredado.
- `ColRef.env = BoolExpr.env`
- `Literal.type` se determina por el tipo léxico (INT, STRING, etc.)
- Si `ColRef.ok` es falso → `BoolExpr.ok = false` y propaga los errores.
- Si `ColRef.type` ≠ `Literal.type`:
  - `BoolExpr.ok = false`
  - `BoolExpr.errors = ColRef.errors ∪ ["Incompatibilidad de tipos en comparación"]`
- En caso contrario:
  - `BoolExpr.ok = true`
  - `BoolExpr.errors = ColRef.errors`
  - `BoolExpr.type = BOOL`

---

### 1.3.3. Validación de `INSERT`

Producción:

```bnf
<InsertStmt> ::= "INSERT" "INTO" <TableRef> "(" <ColList> ")" "VALUES" "(" <ExprList> ")"
```

Reglas (idea general):

1. Heredar `env` a `TableRef`, `ColList` y `ExprList`.
2. Verificar:
   - `TableRef.ok` es verdadero.
   - El número de columnas de `ColList` coincide con el número de expresiones de `ExprList`.
   - Para cada posición `i`, el tipo de `ExprList[i]` es compatible con el tipo de `ColList[i]` según `env`.
3. `InsertStmt.ok` será verdadero si todas las condiciones se cumplen; en caso contrario, se acumulan errores.

---

## 1.4. Función que genera la gramática de atributos

Podemos modelar la generación de la gramática de atributos mediante una función de alto nivel
(en pseudocódigo estilo Python):

```python
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any

@dataclass
class TableSchema:
    name: str
    columns: Dict[str, str]  # nombre -> tipo (INT, STRING, etc.)

@dataclass
class Env:
    tables: Dict[str, TableSchema]

@dataclass
class AttributeRule:
    production: str                 # e.g. "ColRef -> ID"
    semantic_action: Callable[..., Any]  # función que implementa las reglas de atributos

@dataclass
class AttributeGrammar:
    nonterminals: List[str]
    terminals: List[str]
    productions: List[str]
    attribute_rules: List[AttributeRule]

def make_sql_attr_grammar(env: Env) -> AttributeGrammar:
    \"\"\"Construye una gramática de atributos para un lenguaje SQL CRUD,
    parametrizada por un esquema de BD (env).\"\"\"

    nonterminals = [
        "Program", "StmtList", "Stmt",
        "SelectStmt", "InsertStmt", "UpdateStmt", "DeleteStmt",
        "TableRef", "ColRef", "BoolExpr", "Expr", "ExprList", "ColList"
    ]

    terminals = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "INTO", "FROM",
        "WHERE", "VALUES", "AND", "OR",
        "ID", "INT", "STRING", "RELOP", "COMMA", "SEMICOLON"
    ]

    productions = [
        "Program -> StmtList",
        "StmtList -> Stmt ';' StmtList | Stmt",
        "Stmt -> SelectStmt | InsertStmt | UpdateStmt | DeleteStmt",
        "SelectStmt -> 'SELECT' SelectList 'FROM' TableRef WhereOpt",
        "InsertStmt -> 'INSERT' 'INTO' TableRef '(' ColList ')' 'VALUES' '(' ExprList ')'",
        "UpdateStmt -> 'UPDATE' TableRef 'SET' AssignList WhereOpt",
        "DeleteStmt -> 'DELETE' 'FROM' TableRef WhereOpt",
        # ...
    ]

    attribute_rules: List[AttributeRule] = []

    # Ejemplo de regla semántica para TableRef
    def table_ref_action(node):
        table_name = node.ID.lexeme
        if table_name not in env.tables:
            node.ok = False
            node.errors = [f\"Tabla no definida: {table_name}\"]
        else:
            node.ok = True
            node.errors = []
            node.name = table_name

    attribute_rules.append(
        AttributeRule(
            production="TableRef -> ID",
            semantic_action=table_ref_action
        )
    )

    # Aquí se agregarían reglas semánticas similares para ColRef, BoolExpr, InsertStmt, etc.

    return AttributeGrammar(
        nonterminals=nonterminals,
        terminals=terminals,
        productions=productions,
        attribute_rules=attribute_rules
    )
```

Esta función `make_sql_attr_grammar(env)`:

- Recibe un entorno con el **esquema de BD**.
- Construye:
  - Conjuntos de no terminales y terminales.
  - Producciones de la gramática.
  - Reglas semánticas (objetos `AttributeRule`) que vinculan una producción con una función de acción semántica.
- El resultado es una **gramática de atributos parametrizada por el esquema**, capaz de:
  - Validar tipos.
  - Verificar tablas y columnas.
  - Generar representaciones SQL (`sql`) o estructuras internas para un motor de ejecución.