# Импорт зависимостей
import re

from kivy.utils import get_color_from_hex

# Цвета для подсветки синтаксиса
COLORS = {
    'keyword': (.6, .4, .8, 1),
    'string': (.8, .6, .2, 1),
    'comment': (.4, .8, .4, 1),
    'function': (.2, .6, .9, 1),
    'number': (.9, .5, .3, 1),
    'operator': (.7, .3, .3, 1),
    'builtin': (.4, .7, .9, 1),
    'decorator': (.9, .7, .2, 1),
    'default': (.9, .9, .9, 1)
}

# Ключевые слова Python
KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
    'except', 'finally', 'for', 'from', 'global', 'if', 'import',
    'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
    'return', 'try', 'while', 'with', 'yield'
}

# Встроенные функции
BUILTINS = {
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
    'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
    'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
    'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
    'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
    'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
    'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord',
    'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round',
    'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str',
    'sum', 'super', 'tuple', 'type', 'vars', 'zip', '__import__'
}


def highlight_python_code(code: str) -> list:
    '''
    Подсвечивает Python код и возвращает список токенов
    Каждый токен - это словарь с ключами 'text' и 'color'
    '''
    tokens = []
    i = 0
    code_len = len(code)

    while i < code_len:
        if code[i].isspace():
            start = i
            while i < code_len and code[i].isspace():
                i += 1
            tokens.append({'text': code[start:i], 'color': COLORS['default']})
            continue

        if code[i] == '#':
            start = i
            i += 1
            while i < code_len and code[i] != '\n':
                i += 1
            tokens.append({'text': code[start:i], 'color': COLORS['comment']})
            continue

        if code[i] in ('"', "'"):
            start = i
            quote_char = code[i]
            i += 1
            while i < code_len:
                if code[i] == quote_char:
                    i += 1
                    break
                elif code[i] == '\\' and i + 1 < code_len:
                    i += 2
                else:
                    i += 1
            tokens.append({'text': code[start:i], 'color': COLORS['string']})
            continue

        if code[i:i + 3] in ('"""', "'''"):
            start = i
            quote_char = code[i:i + 3]
            i += 3
            while i < code_len:
                if code[i:i + 3] == quote_char:
                    i += 3
                    break
                else:
                    i += 1
            tokens.append({'text': code[start:i], 'color': COLORS['string']})
            continue

        if code[i].isdigit():
            start = i
            while i < code_len and (code[i].isdigit() or code[i] == '.'):
                i += 1
            tokens.append({'text': code[start:i], 'color': COLORS['number']})
            continue

        if code[i].isalpha() or code[i] == '_':
            start = i
            while i < code_len and (code[i].isalnum() or code[i] == '_'):
                i += 1
            word = code[start:i]

            if word in KEYWORDS:
                color = COLORS['keyword']
            elif word in BUILTINS:
                color = COLORS['builtin']
            else:
                color = COLORS['default']
                j = i
                while j < code_len and code[j].isspace():
                    j += 1
                if j < code_len and code[j] == '(':
                    color = COLORS['function']
                elif start > 0 and code[start - 1] == '@':
                    color = COLORS['decorator']

            tokens.append({'text': word, 'color': color})
            continue

        multi_char_ops = ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '&=', '|=', '^=', '>>=',
                          '<<=', '->', '**']
        found_multi = False
        for op in multi_char_ops:
            if code[i:i + len(op)] == op:
                tokens.append({'text': op, 'color': COLORS['operator']})
                i += len(op)
                found_multi = True
                break

        if not found_multi:
            single_ops = '=+-*/%&|^~<>!@:;,.[](){}'
            if code[i] in single_ops:
                tokens.append({'text': code[i], 'color': COLORS['operator']})
                i += 1
            else:
                tokens.append({'text': code[i], 'color': COLORS['default']})
                i += 1

    return tokens
