import enum

TokenType = enum.Enum("TokenType",
                "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE \
                  COMMA DOT MINUS PLUS SEMICOLON COLON SLASH STAR \
                  BANG BANG_EQUAL \
                  EQUAL EQUAL_EQUAL \
                  GREATER GREATER_EQUAL \
                  LESS LESS_EQUAL \
                  QUESTION \
                  IDENTIFIER STRING NUMBER \
                  AND CLASS ELSE FALSE FUN FOR IF NIL OR \
                  PRINT RETURN SUPER THIS TRUE VAR WHILE \
                  EOF")
