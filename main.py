#!/usr/bin/env python3
from string import ascii_uppercase

while True:
    opcion = input(f'Bienvenido a la calculadora logica. \n'
                   f'Ingrese 1 para verificar si una oración es una tautología, contradicción o contingente.\n'
                   f'Ingrese 2 para verificar si un conjunto de oraciones es consistente\n'
                   f'Ingrese 3 para verificar si un argumento es válido.\n'
                   f'> ')
    print('\033[H\033[J', end='')    # Limpia toda la pantalla.
    if opcion == '1':
        print(f'Verificar si una oración es una tautología, una contradicción o una contingencia.\n'
              f'Ingrese una fórmula bien formada.\n')
        while True:
            line = input('1: ')
            if line:
                declaraciones = [line]
                break
            else:
                print('Ingrese una fórmula bien formada.\n')
        break
    elif opcion in ('2', '3'):
        if opcion == '2':
            print(f'Verificar si un conjunto de oraciones es consistente / satisfactorio.\n'
                  f'Ingrese una línea vacía para detenerse.\n')
        elif opcion == '3':
            print(f'Comprobando si un argumento es válido.\n'
                  f'Ingrese una línea vacía para detenerse.\n'
                  f'La última oración ingresada es la conclusión.\n')
        declaraciones = []
        i = 1
        while True:
            line = input(f'{i}: ')
            if line:
                declaraciones.append(line)
            elif not declaraciones:
                print('Ingrese al menos una fórmula bien formada.\n')
                continue
            else:
                break
            i += 1
        break
    print('Entrada inválida.\n')
print('\033[H\033[J', end='')    # Limpia toda la pantalla.

def parse(sentence):
    # -- : keep adding negations to negs
    # -( : wait until you see matching ) to add all negations to output
    # -A : add all negations to output immediately
    line = [(x, i) for i, x in enumerate(sentence)][::-1]
    output = []
    op_stack = []
    neg_brackets = []
    while line:
        token = line.pop()
        if token[0] in ascii_uppercase:
            output.append(token)
        elif token[0] in ('v', '^', '>', '='):
            op_stack.append(token)
        elif token[0] == '(':
            op_stack.append(token)
            neg_brackets.append([])
        elif token[0] == ')':
            while op_stack:
                op = op_stack.pop()
                if op[0] == '(':
                    output.extend(neg_brackets.pop()[::-1])
                    break
                else:
                    output.append(op)
        elif token[0] == '-':
            negs = []
            while token[0] == '-':
                negs.append(token)
                token = line.pop()
            if token[0] == '(':
                op_stack.append(token)
                neg_brackets.append(negs)
            elif token[0] in ascii_uppercase:
                output.append(token)
                output.extend(negs[::-1])
            else:
                print('Negamos algo que parece extraño')
    return output

outputs = [parse(sentence) for sentence in declaraciones]
letters = sorted(set(x for x in ''.join(declaraciones) if x in ascii_uppercase))
models = []
table = []
for i in range(2**len(letters)-1, -1, -1):
    truthrow = format(i, '0' + str(len(letters)) + 'b')
    truths = {letter: int(val) for letter, val in zip(letters, truthrow)}
    models.append(truths)
    row = []
    for sentence, output in zip(declaraciones, outputs):
        subrow = [' ' for _ in range(len(sentence))]
        stack = []
        for cur in output:
            if cur[0] == '-':
                stack.append(int(not stack.pop()))
            elif cur[0] == 'v':
                q, p = stack.pop(), stack.pop()
                stack.append(int(p or q))
            elif cur[0] == '^':
                q, p = stack.pop(), stack.pop()
                stack.append(int(p and q))
            elif cur[0] == '>':
                q, p = stack.pop(), stack.pop()
                stack.append(int((not p) or q))
            elif cur[0] == '=':
                q, p = stack.pop(), stack.pop()
                stack.append(int(p == q))
            else:
                stack.append(truths[cur[0]])
            subrow[cur[1]] = stack[-1]
        row.append(subrow)
    table.append(row)

# Columna de resultados diferente de las otras dos columnas
for i in range(2**len(letters)):
    for j in range(len(declaraciones)):
        table[i][j][outputs[j][-1][1]] = 'T' if table[i][j][outputs[j][-1][1]] else 'F'

# Enseña la tabla
header = ' | '.join([' '.join(letters)] + declaraciones)
print(header)
print(''.join('+' if x == '|' else '-' for x in header))
for model, row in zip(models, table):
    print(*model.values(), '|', ' | '.join(''.join(str(x) for x in subrow) for subrow in row))

if opcion == '1':
    if all(table[i][0][outputs[0][-1][1]] == 'T' for i in range(2**len(letters))):
        print(f'\n{declaraciones[0]} is a tautology.')
    elif all(table[i][0][outputs[0][-1][1]] == 'F' for i in range(2**len(letters))):
        print(f'\n{declaraciones[0]} es una contradicción.')
    else:
        print(f'\n{declaraciones[0]} es una contingencia.')
elif opcion == '2':
    consistent = []
    for i in range(2**len(letters)):
        if all(table[i][j][outputs[j][-1][1]] == 'T' for j in range(len(declaraciones))):
            consistent.append(i)
    print('\nEl conjunto {' + ", ".join(declaraciones) + '} es', 'consistente.' if consistent else 'inconsistente.')
    if consistent:
        print('\nEstos modelos satisfacen el conjunto:\n')
        header = ' | '.join([' '.join(letters)] + declaraciones)
        print(header)
        print(''.join('+' if x == '|' else '-' for x in header))
        for i in consistent:
            print(*models[i].values(), '|', ' | '.join(''.join(str(x) for x in subrow) for subrow in table[i]))
elif opcion == '3':
    counterexamples = []
    for i in range(2**len(letters)):
        if all(table[i][j][outputs[j][-1][1]] == 'T' for j in range(len(declaraciones)-1)) and table[i][-1][outputs[-1][-1][1]] == 'F':
            counterexamples.append(i)
    print('\nEl argumento\n')
    for sentence in declaraciones[:-1]:
        print('  ' + sentence)
    print('âˆ´', declaraciones[-1])
    print('\nes', 'invalido.' if counterexamples else 'valido.')
    if counterexamples:
        print('\nEstos modelos son contraejemplos:\n')
        header = ' | '.join([' '.join(letters)] + declaraciones)
        print(header)
        print(''.join('+' if x == '|' else '-' for x in header))
        for i in counterexamples:
            print(*models[i].values(), '|', ' | '.join(''.join(str(x) for x in subrow) for subrow in table[i]))
