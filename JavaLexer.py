from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    line: int
    col: int

    def __str__(self) -> str:
        return f"Token<type={self.type}, lexeme={self.lexeme!r}, pos={self.line}:{self.col}>"


class LexicalError(Exception):
    pass


class JavaLexer:
    # TODO 1: Completa las palabras reservadas necesarias para el código muestra
    KEYWORDS = {"abstract", "assert", "boolean", "break", "byte", "case", "catch",
        "char", "class", "const", "continue", "default", "do", "double",
        "else", "enum", "extends", "final", "finally", "float", "for",
        "goto", "if", "implements", "import", "instanceof", "int",
        "interface", "long", "native", "new", "package", "private",
        "protected", "public", "return", "short", "static", "strictfp",
        "super", "switch", "synchronized", "this", "throw", "throws",
        "transient", "try", "void", "volatile", "while", "main",}

    # TODO 2: Completa los operadores compuestos
    # Recomendación: del más largo al más corto
    MULTI_OPS = {
        ">>>": "OP_URSHIFT",
        "==":  "OP_EQ",
        "!=":  "OP_NE",
        "<=":  "OP_LE",
        ">=":  "OP_GE",
        "&&":  "OP_AND",
        "||":  "OP_OR",
        "++":  "OP_INC",
        "--":  "OP_DEC",
        "<<":  "OP_LSHIFT",
        ">>":  "OP_RSHIFT",
    }

    # TODO 3: Completa los operadores simples
    SINGLE_OPS = {
        "+": "OP_PLUS",
        "-": "OP_MINUS",
        "*": "OP_MUL",
        "/": "OP_DIV",
        "%": "OP_MOD",
        "=": "OP_ASSIGN",
        "<": "OP_LT",
        ">": "OP_GT",
        "!": "OP_NOT",
        "&": "OP_AMP",
        "|": "OP_PIPE",
        "^": "OP_XOR",
        "~": "OP_BITNOT",
        "?": "OP_TERNARY",
    }

    DELIMS = {
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LBRACE",
        "}": "RBRACE",
        "[": "LBRACKET",
        "]": "RBRACKET",
        ";": "SEMI",
        ",": "COMMA",
        ".": "PERIOD",
        ":": "COLON",
        "@": "AT"
    }

    WHITESPACE = {" ", "\t", "\r", "\n"}

    STDLIB_NAMES = {
        "System.out.println": "KW_PRINTLN",
        "System.out.print": "KW_PRINT",
        "System.out": "KW_SYSOUT",
    }

    def __init__(self, source: str) -> None:
        self.tokens: List[Token] = []
        self.symbol_table: Dict[str, Dict[str, Any]] = {}
        self.i = 0
        self.line = 1
        self.col = 1
        self.source = source
        self.after_dot = False

    def current_char(self) -> str:
        return self.source[self.i] if self.i < len(self.source) else "\0"

    def peek(self, k: int = 1) -> str:
        j = self.i + k
        return self.source[j] if j < len(self.source) else "\0"

    def advance(self, n: int = 1) -> None:
        for _ in range(n):
            if self.i >= len(self.source):
                return
            ch = self.source[self.i]
            self.i += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def add_token(self, t_type: str, lexeme: str, t_line: int, t_col: int) -> None:
        self.tokens.append(Token(t_type, lexeme, t_line, t_col))
        self.after_dot = (t_type == "PERIOD")

    # TODO 4: Completa este método para registrar identificadores en la tabla de símbolos
    def register_symbol(self, name: str, line: int, col: int) -> None:
        """
        Estructura sugerida:
        {
            "identificador": {
                "first_line": ...,
                "first_col": ...,
                "occurrences": ...
            }
        }
        """
        pass

    def tokenize(self, verbose: bool = True) -> List[Token]:
        while self.i < len(self.source):
            ch = self.current_char()

            # 1) Espacios en blanco
            if ch in self.WHITESPACE:
                if verbose:
                    print(f"Ignorando espacio en blanco {ch!r} en {self.line}:{self.col}")
                self.advance(1)
                continue

            # 2) Comentarios
            if ch == "/" and self.peek(1) == "/":
                if verbose:
                    print(f"Ignorando comentario de línea en {self.line}:{self.col}")
                self.advance(2)
                while self.current_char() not in {"\n", "\0"}:
                    self.advance(1)
                continue

            if ch == "/" and self.peek(1) == "*":
                start_line, start_col = self.line, self.col
                if verbose:
                    print(f"Ignorando comentario de bloque iniciado en {start_line}:{start_col}")
                self.advance(2)
                while True:
                    if self.current_char() == "\0":
                        raise LexicalError(
                            f"Comentario de bloque sin cerrar (inició en {start_line}:{start_col})"
                        )
                    if self.current_char() == "*" and self.peek(1) == "/":
                        if verbose:
                            print(f"Comentario de bloque cerrado en {self.line}:{self.col}")
                        self.advance(2)
                        break
                    self.advance(1)
                continue

            # 3) Números
            if ch.isdigit():
                t_line, t_col = self.line, self.col
                start = self.i

                while self.current_char().isdigit():
                    self.advance(1)

                is_float = False

                if self.current_char() == "." and self.peek(1).isdigit():
                    is_float = True
                    self.advance(1)
                    while self.current_char().isdigit():
                        self.advance(1)

                if self.current_char() in {"E", "e"}:
                    if self.peek(1) in {"+", "-"} and self.peek(2).isdigit():
                        is_float = True
                        self.advance(2)
                        while self.current_char().isdigit():
                            self.advance(1)
                    elif self.peek(1).isdigit():
                        is_float = True
                        self.advance(1)
                        while self.current_char().isdigit():
                            self.advance(1)
                    else:
                        raise LexicalError(f"Exponente mal formado en {self.line}:{self.col}")

                lexeme = self.source[start:self.i]
                self.add_token("FLOAT_LIT" if is_float else "INT_LIT", lexeme, t_line, t_col)
                continue

            # TODO 5: Literales de cadena
            # Deben reconocer algo como: "Aprobado\n"
            # Sugerencia:
            # - detectar comilla doble
            # - consumir hasta la siguiente comilla doble
            # - permitir secuencias escapadas simples como \n o \"
            # - generar token STRING_LIT
            if ch == '"':
                t_line, t_col = self.line, self.col
                lex = ['"']
                self.advance(1)

                while True:
                    c = self.current_char()
                    if c == "\0" or c == "\n":
                        raise LexicalError(f"Cadena sin cerrar en {t_line}:{t_col}")
                    if c == '"':
                        lex.append('"')
                        self.advance(1)
                        break
                    if c == "\\":
                        # Escape básico
                        nxt = self.peek(1)
                        if nxt == "\0":
                            raise LexicalError(
                                f"Escape inválido al final del archivo en {self.line}:{self.col}"
                            )
                        lex.append("\\")
                        lex.append(nxt)
                        self.advance(2)
                        continue
                    lex.append(c)
                    self.advance(1)

                lexeme = "".join(lex)
                # value: contenido sin comillas (manteniendo escapes)
                self.add_token("STRING_LIT", lexeme, t_line, t_col)
                continue

            if ch == "'":
                t_line, t_col = self.line, self.col
                lex = ["'"]
                self.advance(1)
                c = self.current_char()
                if c == "\\":
                    lex.append("\\")
                    lex.append(self.peek(1))
                    self.advance(2)
                elif c != "\0":
                    lex.append(c)
                    self.advance(1)
                if self.current_char() != "'":
                    raise LexicalError(f"Literal de carácter mal formado en {t_line}:{t_col}")
                lex.append("'")
                self.advance(1)
                self.add_token("CHAR_LIT", "".join(lex), t_line, t_col)
                continue

            # TODO 6: Operadores compuestos
            # Recorre MULTI_OPS y revisa si el texto actual comienza con alguno
            three = ch + self.peek(1) + self.peek(2)
            if three in self.MULTI_OPS:
                t_line, t_col = self.line, self.col
                self.add_token(self.MULTI_OPS[three], three, t_line, t_col)
                self.advance(3)
                continue

            two = ch + self.peek(1)
            if two in self.MULTI_OPS:
                t_line, t_col = self.line, self.col
                self.add_token(self.MULTI_OPS[two], two, t_line, t_col)
                self.advance(2)
                continue

            # TODO 7: Operadores simples
            # Si ch pertenece a SINGLE_OPS, genera el token correspondiente
            if ch in self.SINGLE_OPS:
                t_line, t_col = self.line, self.col
                self.add_token(self.SINGLE_OPS[ch], ch, t_line, t_col)
                self.advance(1)
                continue

            # 8) Delimitadores
            if ch in self.DELIMS:
                t_line, t_col = self.line, self.col
                self.add_token(self.DELIMS[ch], ch, t_line, t_col)
                self.advance(1)
                continue

            # TODO 9: Identificadores y palabras reservadas
            # Reglas típicas:
            # - empiezan con letra o _
            # - pueden continuar con letras, dígitos o _
            # - si el lexema está en KEYWORDS, usar el token reservado
            # - en otro caso, usar ID y registrar en la tabla de símbolos
            if ch == "_" or ch.isalpha():
                t_line, t_col = self.line, self.col
                start = self.i
                while True:
                    c = self.current_char()
                    if c == "_" or c.isalpha() or c.isdigit():
                        self.advance(1)
                    else:
                        break
                lexeme = self.source[start: self.i]
                if not self.after_dot:
                    matched_stdlib = None
                    # Try longest chain first by peeking ahead over dots
                    saved_i, saved_line, saved_col = self.i, self.line, self.col
                    chain = lexeme
                    while self.current_char() == ".":
                        dot_i, dot_line, dot_col = self.i, self.line, self.col
                        self.advance(1)  # consume dot
                        part_start = self.i
                        while True:
                            c = self.current_char()
                            if c == "_" or c.isalpha() or c.isdigit():
                                self.advance(1)
                            else:
                                break
                        part = self.source[part_start: self.i]
                        if not part:
                            # rewind the dot and stop
                            self.i, self.line, self.col = dot_i, dot_line, dot_col
                            break
                        chain = chain + "." + part
                        if chain in self.STDLIB_NAMES:
                            matched_stdlib = chain
                            saved_i, saved_line, saved_col = self.i, self.line, self.col
                        # keep going to find longer match
                    if matched_stdlib:
                        # rewind to end of matched chain
                        self.i, self.line, self.col = saved_i, saved_line, saved_col
                        self.add_token(self.STDLIB_NAMES[matched_stdlib], matched_stdlib, t_line, t_col)
                    else:
                        # rewind entire chain attempt
                        self.i, self.line, self.col = saved_i, saved_line, saved_col
                        matched_stdlib = None  # fall through to normal handling below

                    if matched_stdlib:
                        continue

                if lexeme in self.KEYWORDS:
                    self.add_token(f"KW_{lexeme.upper()}", lexeme, t_line, t_col)
                    # Skip import lines entirely (rest of line after the keyword)
                    if lexeme == "import":
                        if verbose:
                            print(f"Encontrado linea Import {t_line}:{t_col}")
                        while self.current_char() not in {"\n", "\0"}:
                            self.advance(1)
                        self.add_token("LN_IMPORT", lexeme, t_line, t_col)
                    if lexeme == "package":
                        if verbose:
                            print(f"Encontrado linea package {t_line}:{t_col}")
                        while self.current_char() not in {"\n", "\0"}:
                            self.advance(1)
                        self.add_token("LN_PACKAGE", lexeme, t_line, t_col)
                elif self.after_dot:
                    self.add_token("METHOD_CALL", lexeme, t_line, t_col)
                else:
                    # Plain identifier — register in symbol_table
                    entry = self.symbol_table.get(lexeme)
                    if entry is None:
                        entry = {
                            "first_line": t_line,
                            "first_col": t_col,
                            "occurrences": [],
                        }
                        self.symbol_table[lexeme] = entry
                    entry["occurrences"].append((t_line, t_col))
                    self.add_token("ID", lexeme, t_line, t_col)
                continue

            # E) Error léxico
            raise LexicalError(f"Carácter inválido {ch!r} en {self.line}:{self.col}")

        self.tokens.append(Token("EOF", "", self.line, self.col))
        return self.tokens


if __name__ == "__main__":
    with open("In.txt", "r") as f:
        contents = f.read()

    code = contents

    lexer = JavaLexer(code)
    try:
        toks = lexer.tokenize()
        for t in toks:
            print(t)

        print("\n=== Tabla de símbolos (IDs) ===")
        for name, info in lexer.symbol_table.items():
            print(
                f"{name}: first=({info['first_line']}:{info['first_col']}), occ={info['occurrences']}"
            )
    except LexicalError as e:
        print("ERROR LÉXICO:", e)
