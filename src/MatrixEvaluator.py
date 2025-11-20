# src/MatrixEvaluator.py
#
# Visitante para evaluar programas del lenguaje MatrixLang:
# - Maneja una tabla de símbolos de matrices
# - Valida dimensiones en el producto de matrices
# - Ejecuta operaciones básicas (declaración, asignación, print)
#
# Nota: requiere que los archivos generados por ANTLR4 (MatrixLangLexer.py,
# MatrixLangParser.py, MatrixLangVisitor.py) estén en `src/gen`.

from typing import Dict, Tuple, List, Any
from dataclasses import dataclass, field

from gen.MatrixLangParser import MatrixLangParser
from gen.MatrixLangVisitor import MatrixLangVisitor


Matrix = List[List[int]]  # Matrices como listas de listas de enteros


@dataclass
class SymbolTable:
    matrices: Dict[str, Tuple[int, int, Matrix]] = field(default_factory=dict)

    def define(self, name: str, rows: int, cols: int, value: Matrix):
        self.matrices[name] = (rows, cols, value)

    def get(self, name: str) -> Tuple[int, int, Matrix]:
        if name not in self.matrices:
            raise RuntimeError(f"Variable no declarada: {name}")
        return self.matrices[name]


class MatrixEvaluator(MatrixLangVisitor):
    def __init__(self):
        super().__init__()
        self.symtab = SymbolTable()

    # program : stmtList EOF ;
    def visitProgram(self, ctx: MatrixLangParser.ProgramContext):
        return self.visit(ctx.stmtList())

    # stmtList : stmt ';' | stmt ';' stmtList ;
    def visitStmtList(self, ctx: MatrixLangParser.StmtListContext):
        # Ejecutar secuencialmente los statements
        if ctx.stmtList() is None:
            self.visit(ctx.stmt())
        else:
            self.visit(ctx.stmt())
            self.visit(ctx.stmtList())

    # stmt : matrixDecl | assignStmt | printStmt ;
    def visitStmt(self, ctx: MatrixLangParser.StmtContext):
        if ctx.matrixDecl():
            return self.visit(ctx.matrixDecl())
        elif ctx.assignStmt():
            return self.visit(ctx.assignStmt())
        else:
            return self.visit(ctx.printStmt())

    # matrixDecl : MATRIX ID '[' INT ',' INT ']' '=' matrixLiteral ;
    def visitMatrixDecl(self, ctx: MatrixLangParser.MatrixDeclContext):
        name = ctx.ID().getText()
        rows = int(ctx.INT(0).getText())
        cols = int(ctx.INT(1).getText())
        value, lit_rows, lit_cols = self.visit(ctx.matrixLiteral())

        if rows != lit_rows or cols != lit_cols:
            raise RuntimeError(
                f"Dimensiones declaradas ({rows}x{cols}) "
                f"no concuerdan con el literal ({lit_rows}x{lit_cols}) para {name}"
            )

        self.symtab.define(name, rows, cols, value)
        return None

    # assignStmt : ID '=' expr ;
    def visitAssignStmt(self, ctx: MatrixLangParser.AssignStmtContext):
        name = ctx.ID().getText()
        value, r, c = self.visit(ctx.expr())
        self.symtab.define(name, r, c, value)
        return None

    # printStmt : PRINT ID ;
    def visitPrintStmt(self, ctx: MatrixLangParser.PrintStmtContext):
        name = ctx.ID().getText()
        rows, cols, value = self.symtab.get(name)
        print(f"{name} ({rows}x{cols}):")
        for row in value:
            print("  ", row)
        return None

    # expr : expr '*' term     # MulExpr
    #      | term              # TermExpr
    def visitMulExpr(self, ctx: MatrixLangParser.MulExprContext):
        left_val, left_r, left_c = self.visit(ctx.expr())
        right_val, right_r, right_c = self.visit(ctx.term())
        return self.matmul(left_val, left_r, left_c, right_val, right_r, right_c)

    def visitTermExpr(self, ctx: MatrixLangParser.TermExprContext):
        return self.visit(ctx.term())

    # term : ID          # IdTerm
    #      | matrixLiteral  # LitTerm
    #      | '(' expr ')'   # ParenExpr
    def visitIdTerm(self, ctx: MatrixLangParser.IdTermContext):
        name = ctx.ID().getText()
        rows, cols, value = self.symtab.get(name)
        return value, rows, cols

    def visitLitTerm(self, ctx: MatrixLangParser.LitTermContext):
        value, r, c = self.visit(ctx.matrixLiteral())
        return value, r, c

    def visitParenExpr(self, ctx: MatrixLangParser.ParenExprContext):
        return self.visit(ctx.expr())

    # matrixLiteral : '[' rowList ']' ;
    def visitMatrixLiteral(self, ctx: MatrixLangParser.MatrixLiteralContext):
        rows, n_rows, n_cols = self.visit(ctx.rowList())
        return rows, n_rows, n_cols

    # rowList : row
    #         | row ',' rowList ;
    def visitRowList(self, ctx: MatrixLangParser.RowListContext):
        if ctx.rowList() is None:
            row_vals, cols = self.visit(ctx.row())
            return [row_vals], 1, cols
        else:
            row_vals, cols = self.visit(ctx.row())
            rest_matrix, rest_rows, rest_cols = self.visit(ctx.rowList())
            if cols != rest_cols:
                raise RuntimeError("Todas las filas deben tener el mismo número de columnas")
            return [row_vals] + rest_matrix, 1 + rest_rows, cols

    # row : '[' intList ']' ;
    def visitRow(self, ctx: MatrixLangParser.RowContext):
        ints = self.visit(ctx.intList())
        return ints, len(ints)

    # intList : INT
    #         | INT ',' intList ;
    def visitIntList(self, ctx: MatrixLangParser.IntListContext):
        if ctx.intList() is None:
            return [int(ctx.INT().getText())]
        else:
            first = int(ctx.INT().getText())
            rest = self.visit(ctx.intList())
            return [first] + rest

    # Utilidad: producto de matrices
    def matmul(
        self,
        A: Matrix, r1: int, c1: int,
        B: Matrix, r2: int, c2: int
    ) -> Tuple[Matrix, int, int]:
        if c1 != r2:
            raise RuntimeError(
                f"Incompatibilidad de dimensiones para producto: "
                f"({r1}x{c1}) * ({r2}x{c2})"
            )
        # Resultado (r1 x c2)
        result: Matrix = [[0 for _ in range(c2)] for _ in range(r1)]
        for i in range(r1):
            for j in range(c2):
                acc = 0
                for k in range(c1):
                    acc += A[i][k] * B[k][j]
                result[i][j] = acc
        return result, r1, c2