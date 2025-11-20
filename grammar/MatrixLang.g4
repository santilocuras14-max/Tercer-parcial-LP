grammar MatrixLang;

// --------- Reglas de Parser ---------

program
    : stmtList EOF
    ;

stmtList
    : stmt ';'
    | stmt ';' stmtList
    ;

stmt
    : matrixDecl
    | assignStmt
    | printStmt
    ;

matrixDecl
    : MATRIX ID LBRACK INT COMMA INT RBRACK ASSIGN matrixLiteral
    ;

assignStmt
    : ID ASSIGN expr
    ;

printStmt
    : PRINT ID
    ;

expr
    : expr MUL term           # MulExpr
    | term                    # TermExpr
    ;

term
    : ID                      # IdTerm
    | matrixLiteral           # LitTerm
    | LPAREN expr RPAREN      # ParenExpr
    ;

matrixLiteral
    : LBRACK rowList RBRACK
    ;

rowList
    : row
    | row COMMA rowList
    ;

row
    : LBRACK intList RBRACK
    ;

intList
    : INT
    | INT COMMA intList
    ;

// --------- Reglas Léxicas ---------

MATRIX  : 'matrix';
PRINT   : 'print';

ASSIGN  : '=';
MUL     : '*';
LBRACK  : '[';
RBRACK  : ']';
COMMA   : ',';
SEMI    : ';';
LPAREN  : '(';
RPAREN  : ')';

ID      : [a-zA-Z_][a-zA-Z_0-9]*;
INT     : [0-9]+;

// Ignorar espacios y saltos de línea
WS      : [ \t\r\n]+ -> skip;

// Comentarios estilo //
LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;