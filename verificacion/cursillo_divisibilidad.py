"""Verificación de la clase del cursillo: Divisibilidad.

Los ejercicios de `cursillo/clases/divisibilidad.html` son los del ejercitario
del cursillo, transcriptos tal cual con sus opciones. Acá cada uno se
resuelve de nuevo, con enteros (nada de float), por un camino distinto del
de la clase:

1. Los de afirmaciones: cada afirmación se prueba por fuerza bruta sobre
   muchos números (divisores contados uno por uno, no con la fórmula), y de
   ahí sale qué opción es la correcta. No se escribe a mano cuál es.
2. Los numéricos: por fuerza bruta (se recorren los exponentes, los números,
   los pedazos posibles) y, donde se puede, por la fórmula de la clase. Los
   dos tienen que dar lo mismo, y la solución tiene que ser única.
3. Las opciones de la página son las del material, en ese orden; la que
   está marcada ok:true es la que salió de 1 o 2; y la que lleva un error
   que es una cuenta se recalcula desde ese error.
4. El enunciado de la página trae los datos del material.
5. Cada ejercicio con tras: va después de una teoría que existe en la página.
6. Los ejemplos de la teoría (317, 720, 12 y 18…) y el desafío (el
   ejercicio 39, resuelto en la pizarra).
7. Ningún renglón propio encadena dos igualdades, no hay rayas (—) y no
   aparece el nombre de otro docente.

    python verificacion/cursillo_divisibilidad.py
"""
import re
import sys
from fractions import Fraction as F
from itertools import product, combinations
from math import gcd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = RAIZ / 'cursillo' / 'clases' / 'divisibilidad.html'
fallos = []


def mal(m):
    fallos.append(m)
    print('   FALLA:', m)


EJ = {}                       # cod -> (tema, [(texto, ok)], {k: valor del error})


# ── a mano, sin fórmulas: los divisores uno por uno ──
def divisores(n):
    return [k for k in range(1, n + 1) if n % k == 0]


def es_primo(n):
    return n > 1 and all(n % k for k in range(2, n))


def primos_de(n):
    return [p for p in divisores(n) if es_primo(p)]


def mcd(*xs):
    """el mayor que divide a todos, buscado de arriba hacia abajo"""
    for k in range(min(xs), 0, -1):
        if all(x % k == 0 for x in xs):
            return k


def mcm(*xs):
    """el menor múltiplo común, buscado de abajo hacia arriba"""
    k = max(xs)
    while any(k % x for x in xs):
        k += max(xs)
    return k


def factoriza(n):
    f, p = {}, 2
    while n > 1:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        p += 1
    return f


def miles(n):
    return f'{n:,}'.replace(',', '.')


def unica(cod, verdades):
    k = [i for i, v in enumerate(verdades) if v]
    if len(k) != 1:
        mal(f'{cod}: las opciones verdaderas son {k}, tiene que haber una sola')
        return None
    return k[0]


def ejercicio(cod, tema, textos, correcta, errores=None):
    if correcta is None:
        return
    if len(set(textos)) != len(textos):
        mal(f'{cod}: dos opciones iguales')
    EJ[cod] = (tema, [(t, i == correcta) for i, t in enumerate(textos)], errores or {})
    print(f'  {cod:4s} la {"ABCDE"[correcta]}: {textos[correcta]}')


def conjunto(cod, textos, verdad, piden):
    """Opciones como 'I, II y IV' o 'Solo II' o 'Todas': la correcta es la
    que nombra justo las afirmaciones que piden (las verdaderas o las falsas)."""
    quiero = {k for k, v in verdad.items() if v == (piden == 'verdaderas')}
    def lee(t):
        if t == 'Todas':
            return set(verdad)
        return set(re.findall(r'\b[IVX]+\b', t))
    return unica(cod, [lee(t) == quiero for t in textos])


NUM = range(1, 121)


# ═══════════════════════ Tema 1 · múltiplos y divisores ═══════════════════════
def tema1():
    print('Tema 1 · múltiplos y divisores')
    # E1: m, n, k divisibles por t
    trios = [(m, n, k, t) for t in range(1, 13) for m, n, k in product(range(t, 60, t), repeat=3)]
    I = all((m + n + k) % t == 0 for m, n, k, t in trios)
    II = all(max(range(t, 1000, t)) == t for t in range(1, 13))          # el mayor múltiplo de t es t
    III = all(m <= n or (m - n) % t == 0 for m, n, k, t in trios)
    IV = all(len(divisores(t)) > 1000 for t in range(1, 13))             # infinitos: más que cualquier cota
    ver = {'I': I, 'II': II, 'III': III, 'IV': IV}
    textos = ['I y III', 'Solo IV', 'II y IV', 'Solo II', 'Todas']
    ejercicio('E1', '1', textos, conjunto('E1', textos, ver, 'falsas'))

    # E13: un número que divide al dividendo y al divisor divide al resto
    casos = [(D, d, k) for D in range(1, 150) for d in range(1, 40) for k in range(1, 15)
             if D % k == 0 and d % k == 0]
    divide = all((D % d) % k == 0 for D, d, k in casos)
    alguno_no = any((D % d) % k != 0 for D, d, k in casos)
    textos = ['No es divisor del resto.', 'También es divisor del resto.', 'El resto es igual a uno.',
              'El resto es siempre negativo.', 'No está definido.']
    ejercicio('E13', '1', textos, unica('E13', [alguno_no, divide,
                                               all(D % d == 1 for D, d, k in casos),
                                               all(D % d < 0 for D, d, k in casos), False]))

    # teoría: 84 entre 7 y entre 8
    assert 84 % 7 == 0 and 84 // 7 == 12 and divmod(84, 8) == (10, 4)
    # teoría: 3 divide a 12 y a 18, y a su suma y su diferencia
    assert (12 + 18) % 3 == 0 and (18 - 12) % 3 == 0


# ═══════════════════════ Tema 2 · criterios ═══════════════════════
def suma_cifras(n):
    return sum(int(c) for c in str(n))


def alterna(n):
    """la suma de las cifras de lugar impar menos la de lugar par, desde la derecha"""
    c = [int(x) for x in str(n)][::-1]
    return sum(c[0::2]) - sum(c[1::2])


def tema2():
    print('Tema 2 · criterios de divisibilidad')
    # los criterios de la tabla, contra la división, sobre muchos números
    for n in range(1, 30000):
        u = n % 10
        ok = [(n % 2 == 0) == (u % 2 == 0), (n % 3 == 0) == (suma_cifras(n) % 3 == 0),
              (n % 4 == 0) == ((n % 100) % 4 == 0), (n % 5 == 0) == (u in (0, 5)),
              (n % 9 == 0) == (suma_cifras(n) % 9 == 0), (n % 10 == 0) == (u == 0),
              (n % 11 == 0) == (alterna(n) % 11 == 0), (n % 6 == 0) == (n % 2 == 0 and n % 3 == 0)]
        if not all(ok):
            mal(f'un criterio falla con {n}')
            break
    # el del 7: separar la última cifra, duplicarla y restarla
    def siete(n):
        while n >= 70:
            n = abs(n // 10 - 2 * (n % 10))
        return n % 7 == 0
    if not all(siete(n) == (n % 7 == 0) for n in range(1, 30000)):
        mal('el criterio del 7 falla')
    assert suma_cifras(2340) == 9 and alterna(17820) == 0 and 245 // 10 - 2 * 5 == 14

    # E17: entre 120 y 140, divisible por 9
    textos = ['127', '144', '135', '129', '162']
    todos = [n for n in range(121, 140) if n % 9 == 0]
    print(f'       (entre 120 y 140 hay dos múltiplos de 9: {todos}; en las opciones está uno solo)')
    ejercicio('E17', '2', textos, unica('E17', [int(t) in todos for t in textos]),
              {1: 144, 4: 162})

    # E16: divisibles por 2, 3, 4, 5, 6, 9 y 11 a la vez
    nums = {'I': 17820, 'II': 11880, 'III': 17560}
    ver = {k: all(v % d == 0 for d in (2, 3, 4, 5, 6, 9, 11)) for k, v in nums.items()}
    if mcm(2, 3, 4, 5, 6, 9, 11) != 1980:
        mal('E16: el MCM de los divisores no es 1980')
    textos = ['Solo I', 'Solo II', 'Solo III', 'I y II', 'II y III']
    ejercicio('E16', '2', textos, conjunto('E16', textos, ver, 'verdaderas'))


# ═══════════════════════ Tema 3 · primos y compuestos ═══════════════════════
def tema3():
    print('Tema 3 · primos y compuestos')
    PR = [p for p in range(2, 200) if es_primo(p)]
    # E4
    I = all(len(divisores(p)) == 1 for p in PR)
    II = all(es_primo(n) and n % 2 for n in (3, 15, 21, 29))
    III = all(len([m for m in range(1, 10000) if m % n == 0]) < 50 for n in range(1, 20))
    IV = all(n % 4 == 0 for n in range(2, 200, 2))
    ver = {'I': I, 'II': II, 'III': III, 'IV': IV}
    textos = ['I y II', 'II y IV', 'III y IV', 'I y IV', 'Todas']
    ejercicio('E4', '3', textos, conjunto('E4', textos, ver, 'falsas'))

    # E6
    ver = {
        'I': all(min(m for m in range(1, 500) if m % n == 0) == 1 for n in range(1, 30)),
        'II': all(A % B or (A % B == 0 and B in divisores(A)) for A in NUM for B in NUM),
        'III': all(n % d == 0 for n in NUM for d in divisores(n)),
        'IV': all(n == 2 or not es_primo(n) for n in range(2, 300, 2)),
        'V': all(es_primo(n) for n in range(3, 300, 2)),
        'VI': [n for n in range(1, 300) if n % 2 == 0 and es_primo(n)] == [2],
    }
    textos = ['I, III, V y VI', 'II, III, V y VI', 'I, IV, V y VI', 'III, IV, V y VI', 'II, III, IV y VI']
    ejercicio('E6', '3', textos, conjunto('E6', textos, ver, 'verdaderas'))

    # E7
    def criterio2(n):              # «termina en cero o cifra impar»
        return n % 10 == 0 or n % 2 == 1
    ver = {
        'I': all((n % 10 == 0) == (n % 10 == 0) for n in range(1, 5000)),
        'II': all(criterio2(n) == (n % 2 == 0) for n in range(1, 5000)),
        'III': all((n % 3 == 0) == (suma_cifras(n) % 3 == 0) for n in range(1, 5000)),
        'IV': all(gcd(a, b) == 1 for a, b in combinations((5, 7, 18), 2)),
    }
    textos = ['I, II y III', 'II, III y IV', 'III y IV', 'I, III y IV', 'Solo II']
    ejercicio('E7', '3', textos, conjunto('E7', textos, ver, 'falsas'))

    # teoría: 317 es primo y basta probar hasta 17
    if not es_primo(317) or not (17 ** 2 <= 317 < 18 ** 2):
        mal('teoría: 317 y su raíz')
    if [p for p in PR if p * p <= 317] != [2, 3, 5, 7, 11, 13, 17]:
        mal('teoría: los primos a probar para 317')
    # 8 y 15 primos entre sí; 6, 10, 15 entre sí pero no dos a dos
    assert mcd(8, 15) == 1 and mcd(6, 10, 15) == 1 and mcd(6, 10) == 2
    assert len(divisores(9)) == 3 and len(divisores(1)) == 1


# ═══════════════════════ Tema 4 · factores primos y divisores ═══════════════════════
def tema4():
    print('Tema 4 · factores primos y divisores')
    # la fórmula de la cantidad, la suma y el producto, contra contar uno por uno
    for n in range(2, 3000):
        f = factoriza(n)
        cant = 1
        suma = 1
        for p, a in f.items():
            cant *= a + 1
            suma *= sum(p ** k for k in range(a + 1))
        ds = divisores(n)
        prod = 1
        for d in ds:
            prod *= d
        if cant != len(ds) or suma != sum(ds) or prod ** 2 != n ** cant:
            mal(f'las fórmulas fallan con {n}')
            break
    assert factoriza(720) == {2: 4, 3: 2, 5: 1} and len(divisores(720)) == 30
    assert sum(divisores(12)) == 28 == (1 + 2 + 4) * (1 + 3)

    # E3: 7^m · 5^n · 3^p · 2^q = 8100
    sol = [(m, n, p, q) for m, n, p, q in product(range(8), repeat=4)
           if 7 ** m * 5 ** n * 3 ** p * 2 ** q == 8100]
    if len(sol) != 1:
        mal(f'E3: {sol}')
    m, n, p, q = sol[0]
    v = m * n + p * q
    ejercicio('E3', '4', ['0', '8', '−8', '4', 'NDA'], unica('E3', [v == 0, v == 8, v == -8, v == 4, False]))

    # E5: 2^a · 3^b · 5^c · 7^d = 540, ab − cd
    sol = [s for s in product(range(10), repeat=4) if 2 ** s[0] * 3 ** s[1] * 5 ** s[2] * 7 ** s[3] == 540]
    a, b, c, d = sol[0]
    v = a * b - c * d
    if len(sol) != 1:
        mal(f'E5: {sol}')
    ejercicio('E5', '4', ['6', '5', '4', '3', 'NDA'], unica('E5', [v == 6, v == 5, v == 4, v == 3, False]),
              {1: a * b - c})

    # E2: 2340
    N = 2340
    ps = primos_de(N)
    simples = [1] + ps
    ver = {
        'I': len(ps) == 5,                                 # distintos: 4
        'II': len(divisores(N)) == 36,
        'III': sum(simples) == 20 or sum(ps) == 20,        # con la unidad 24, sin ella 23
        'IV': 10 in ps,
    }
    nfalsas = sum(not v for v in ver.values())
    textos = ['Una', 'Dos', 'Tres', 'Todas', 'Ninguna']
    cuenta = {'Una': 1, 'Dos': 2, 'Tres': 3, 'Todas': 4, 'Ninguna': 0}
    ejercicio('E2', '4', textos, unica('E2', [cuenta[t] == nfalsas for t in textos]))

    # E8: N = 15 · 18^n tiene 144 divisores (contados uno por uno con la factorización de N)
    sol = []
    for n in range(1, 10):
        f = factoriza(15 * 18 ** n)
        k = 1
        for e in f.values():
            k *= e + 1
        if k == 144:
            sol.append(n)
    # y contando uno por uno el de n = 5 por otro lado: 4(n + 1)² = 144
    if sol != [5] or 4 * (5 + 1) ** 2 != 144:
        mal(f'E8: {sol}')
    ejercicio('E8', '4', ['3', '4', '5', '6', 'NDA'], unica('E8', [3 in sol, 4 in sol, 5 in sol, 6 in sol, not sol]))

    # E24: P = 3^m + 3^(m+3) tiene 33 divisores que no son primos
    sol = []
    for m in range(1, 12):
        P = 3 ** m + 3 ** (m + 3)
        f = factoriza(P)
        tot = 1
        for e in f.values():
            tot *= e + 1
        if tot - len(f) == 33:
            sol.append(m)
    if len(sol) != 1:
        mal(f'E24: {sol}')
    m = sol[0]
    mmm = int(str(m) * 3)
    v = len(primos_de(mmm))
    P = 3 ** m + 3 ** (m + 3)
    totP = len(divisores(P))
    ejercicio('E24', '4', ['5', '36', '3', '7', '6'], unica('E24', [v == 5, v == 36, v == 3, v == 7, v == 6]),
              {0: m, 1: totP})

    # E33: suma de divisores 624, producto 3^12 · 5^6 · 7^6, 12 divisores
    obj = 3 ** 12 * 5 ** 6 * 7 ** 6
    sol = []
    for n in range(1, 2000):
        ds = divisores(n)
        if len(ds) != 12 or sum(ds) != 624:
            continue
        pr = 1
        for d in ds:
            pr *= d
        if pr == obj:
            sol.append(n)
    if len(sol) != 1:
        mal(f'E33: {sol}')
    n = sol[0]
    v = sum(d for d in divisores(n) if d % 7)
    ejercicio('E33', '4', ['13', '6', '45', '78', '12'], unica('E33', [v == 13, v == 6, v == 45, v == 78, v == 12]),
              {0: 1 + 3 + 9, 1: 1 + 5, 2: n // 7, 4: 12})
    return n


# ═══════════════════════ Tema 5 · MCD y MCM ═══════════════════════
def tema5():
    print('Tema 5 · MCD y MCM')
    # las propiedades de la teoría, por fuerza bruta
    for A in range(1, 80):
        for B in range(1, 80):
            g, l = mcd(A, B), mcm(A, B)
            if A * B != g * l or mcd(A // g, B // g) != 1 or mcd(l // A, l // B) != 1:
                mal(f'propiedad MCD y MCM con {A}, {B}')
            if A % B and mcd(A, B) != mcd(B, A % B):
                mal(f'el principio del resto con {A}, {B}')
    assert mcd(12, 18) == 6 and mcm(12, 18) == 36 and 6 * 36 == 12 * 18 == 216
    assert min(n for n in range(3, 100) if n % 3 == 2 and n % 4 == 2) == 14

    # E10: cintas de 36 y 48
    pedazo = max(k for k in range(1, 49) if 36 % k == 0 and 48 % k == 0)
    textos = ['12 m', '6 m', '24 m', '2 m', 'NDA']
    ejercicio('E10', '5', textos, unica('E10', [2 * int(t.split()[0]) == pedazo if t != 'NDA' else False
                                                 for t in textos]), {0: pedazo})

    # E19: bolillas
    cols = (5400, 2400, 1560)
    mejor = None
    for k in range(1, 1561):                 # cuántas por bolillero: tiene que dividir a las tres
        if all(c % k == 0 for c in cols):
            n = sum(c // k for c in cols)
            if mejor is None or n < mejor[0]:
                mejor = (n, k)
    n, k = mejor
    ejercicio('E19', '5', ['120', '349', '280.800', '180', '78'],
              unica('E19', [n == 120, n == 349, n == 280800, n == 180, n == 78]),
              {0: k, 2: mcm(*cols)})

    # E21
    A, B = 117975, 2574
    comunes = [p for p in primos_de(B) if A % p == 0]
    p = max(comunes)
    q = (A // p, B // p)
    textos = ['9.075 y 19', '9.075 y 198', '9.075', '198', 'NDA']
    ejercicio('E21', '5', textos, unica('E21', [q == (9075, 19), q == (9075, 198), False, False, False]))

    # E14: jabón
    cajas = (1600, 2000, 3392)
    k = max(b for b in range(1, 1601) if all(c % b == 0 for c in cajas))
    bloques = [c // k for c in cajas]
    v = mcm(*bloques)
    ejercicio('E14', '5', ['2.650', '265', '256', '26.500', 'NDA'],
              unica('E14', [v == 2650, v == 265, v == 256, v == 26500, False]))

    # E9: 2^a · 5^b · 9^d = 8100; mcm(a, 3b, 4d) : mcd(5b, 7d)
    sol = [s for s in product(range(8), repeat=3) if 2 ** s[0] * 5 ** s[1] * 9 ** s[2] == 8100]
    a, b, d = sol[0]
    v = F(mcm(a, 3 * b, 4 * d), mcd(5 * b, 7 * d))
    cada = [v == 2 * 6, v == 6 * 2, v == 3 * 4, v == 10 + 2]
    if len(sol) != 1 or not all(cada):
        mal(f'E9: {sol}, {v}')
    # A, B, C y D dicen lo mismo y son verdaderas: la correcta es «todas las anteriores»
    textos = ['El doble de 6', 'El séxtuplo de 2', 'Triple de 4', 'Suma de 10 y 2', 'TLA']
    ejercicio('E9', '5', textos, 4 if all(cada) else None)

    # E26: primos entre sí, MCM 330, diferencia 7
    pares = [(x, y) for x in range(1, 331) for y in range(x + 1, 331)
             if mcd(x, y) == 1 and mcm(x, y) == 330 and y - x == 7]
    if len(pares) != 1:
        mal(f'E26: {pares}')
    x, y = pares[0]
    v = mcd(y + 18, x + 40)
    ejercicio('E26', '5', ['12', '15', '10', '5', '20'], unica('E26', [v == 12, v == 15, v == 10, v == 5, v == 20]))

    # E28: B y C
    R = range(1, 80)
    ver = {
        'I': all(B == C or set(primos_de(B)) != set(primos_de(C)) for B in R for C in R),
        'II': all(B % C or all(B % d == 0 for d in divisores(C)) for B in R for C in R),
        'III': all(mcd(B, C) != 1 or mcm(B, C) == B * C for B in R for C in R),
        'IV': all(B >= C or len(divisores(B)) < len(divisores(C)) for B in R for C in R),
    }
    nver = sum(ver.values())
    textos = ['Una', 'Dos', 'Tres', 'Cuatro', 'Cero']
    cuenta = {'Una': 1, 'Dos': 2, 'Tres': 3, 'Cuatro': 4, 'Cero': 0}
    ejercicio('E28', '5', textos, unica('E28', [cuenta[t] == nver for t in textos]))

    # E11: la falsa
    R = range(1, 40)
    A_ = all(not (mcd(x, y) == 1) or (es_primo(x) and es_primo(y)) for x in R for y in R)
    B_ = all(mcm(x, y, z) == x * y * z for x, y, z in product(R, repeat=3)
             if mcd(x, y) == mcd(y, z) == mcd(x, z) == 1)
    C_ = [n for n in range(1, 300) if n % 2 == 0 and es_primo(n)] == [2]
    D_ = all(len(divisores(n)) >= 3 for n in range(4, 300) if not es_primo(n))
    E_ = all(mcd(x, y, z) == 1 for x, y, z in product(R, repeat=3)
             if mcd(x, y) == mcd(y, z) == mcd(x, z) == 1)
    textos = ['Para que dos números sean primos entre sí, necesariamente deben ser primos absolutos.',
              'Si dos o más números son primos dos a dos, el m.c.m. es su producto.',
              'El número 2 es el único número par primo.',
              'Todo número compuesto tiene por lo menos tres divisores.',
              'Si dos o más números son primos dos a dos, necesariamente son primos entre sí.']
    ejercicio('E11', '5', textos, unica('E11', [not A_, not B_, not C_, not D_, not E_]))

    # E20: el menor que dividido por 5, 6, 7 o 15 da resto 3
    n = min(n for n in range(4, 10000) if all(n % k == 3 for k in (5, 6, 7, 15)))
    v = sum(int(c) for c in str(n))
    if n != mcm(5, 6, 7, 15) + 3:
        mal('E20: no es el MCM más 3')
    ejercicio('E20', '5', ['231', '213', '21', '6', '1'], unica('E20', [v == 231, v == 213, v == 21, v == 6, v == 1]),
              {1: n})

    # E22: el menor que dividido por 17, 38 y 115 da resto 11
    n = next(n for n in range(12, 200000) if all(n % k == 11 for k in (17, 38, 115)))
    if n != mcm(17, 38, 115) + 11:
        mal('E22: no es el MCM más 11')
    ejercicio('E22', '5', ['7.430', '74.301', '743', '74.300', 'NDA'],
              unica('E22', [n == 7430, n == 74301, n == 743, n == 74300, False]))

    # E30: tornillos
    sol = [n for n in range(701, 800) if n % 15 == 10 and n % 20 == 15 and n % 24 == 19]
    if sol != [mcm(15, 20, 24) * 6 - 5]:
        mal(f'E30: {sol}')
    n = sol[0]
    ejercicio('E30', '5', ['705', '715', '825', '785', '935'],
              unica('E30', [n == 705, n == 715, n == 825, n == 785, n == 935]))
    return mcm(15, 20, 24)


def desafio():
    """E39: rayas cada 1,2 m, pasos de 75 cm, 3 m/s; la raya por 34.ª vez."""
    # a fuerza de pasos: se cuentan los pasos que caen en una raya
    vez, paso = 1, 0                          # al empezar ya pisa una (la vez 1)
    while vez < 34:
        paso += 1
        if (paso * 75) % 120 == 0:
            vez += 1
    cm = paso * 75
    t = F(cm, 300)                            # 3 m/s son 300 cm por segundo
    if cm != 33 * mcm(120, 75) or t != 66:
        mal(f'E39: {cm} cm, {t} s')
    textos = ['85 segundos', '66 segundos', '100 segundos', '60 segundos', '70 segundos']
    if [x for x in textos if x == f'{t} segundos'] != ['66 segundos']:
        mal('E39: la respuesta no está entre las opciones')
    return int(t), mcm(120, 75), paso


# los datos de cada ejercicio, como están en el material
FUENTE = {
    'E1': ['divisibles por', 'El mayor múltiplo de', 'tiene infinitos divisores'],
    'E2': ['2.340', 'cinco factores primos', 'tres decenas y seis unidades', 'dos decenas', 'El número diez'],
    'E3': ['8.100'],
    'E4': ['3, 15, 21, 29', 'divisible por 4'],
    'E5': ['540'],
    'E6': ['excepto el 2', 'Todos los números impares son primos'],
    'E7': ['cero o cifra impar', '5, 7, 18'],
    'E8': ['144 divisores'],
    'E9': ['8.100'],
    'E10': ['36 m y 48 m', 'el doble de'],
    'E14': ['1.600 kg, 2.000 kg y 3.392 kg'],
    'E16': ['17.820', '11.880', '17.560', '2; 3; 4; 5; 6; 9 y 11'],
    'E17': ['menor que 140 y mayor que 120', 'divisible por 9'],
    'E19': ['5.400 bolillas rojas, 2.400 azules, 1.560 blancas'],
    'E20': ['5; 6; 7 o 15', 'por resto 3', 'suma de las cifras'],
    'E21': ['117.975 y 2.574', 'mayor divisor primo común'],
    'E22': ['17, 38 y 115', 'resto 11'],
    'E24': ['33 divisores positivos que no son números primos'],
    'E26': ['es 330', 'diferencia 7', 'se le aumenta 18', 'al menor 40'],
    'E28': ['los mismos divisores primos', 'la cantidad de divisores de'],
    'E30': ['mayor que 700 pero menor que 800', 'sobran 10', 'sobran 15', 'sobran 19'],
    'E33': ['son 624', '12 divisores positivos', 'no son múltiplos de 7'],
}
# lo que se transcribe tal cual aunque tenga dos «=»: una afirmación del material
TAL_CUAL = ['III) Si MCD(B, C) = 1, entonces MCM(B, C) = B × C.']


def controla_pagina(n33, mcm30, t39, mcm39, pasos39):
    print('La página')
    if not PAGINA.exists():
        mal(f'no existe {PAGINA}')
        return
    html = PAGINA.read_text(encoding='utf-8')

    en_pagina = {}
    for cod, cuerpo, ops in re.findall(r"\{\s*cod:'(E\d+)'(.*?)opciones:\[(.*?)\]\s*\}", html, flags=re.S):
        lista = re.findall(r"\{\s*t:'([^']*)'(?:,\s*(?:(ok:true)|error:'([^']*)'))?\s*\}", ops)
        tras = re.search(r"tras:'([^']+)'", cuerpo)
        en_pagina[cod] = ([(t, bool(ok), err) for t, ok, err in lista], tras.group(1) if tras else None)
    teorias = set(re.findall(r"\{\s*id:'([^']+)',\s*cajon:", html))
    for cod, (tema, ops, errores) in EJ.items():
        if cod not in en_pagina:
            mal(f'{cod}: no está en la página')
            continue
        pag, tras = en_pagina[cod]
        if [(t, ok) for t, ok, _ in pag] != ops:
            for k, (a, b) in enumerate(zip(ops, [(t, ok) for t, ok, _ in pag] + [None] * 5)):
                if a != b:
                    mal(f'{cod}, opción {"ABCDE"[k]}: la página dice {b}, tiene que ser {a}')
        for k, valor in errores.items():
            if k < len(pag) and not pag[k][2]:
                mal(f'{cod}, opción {"ABCDE"[k]}: sale de un error, y la página no lo anota')
            num = re.sub(r'[^\d]', '', ops[k][0])
            if num != str(valor):
                mal(f'{cod}, opción {"ABCDE"[k]}: el error anotado da {valor}, no {ops[k][0]}')
        if not tras:
            mal(f'{cod}: no dice después de qué teoría va (tras:)')
        elif tras not in teorias:
            mal(f'{cod}: va tras «{tras}», que no es una teoría de la página')
    for cod in en_pagina:
        if cod not in EJ:
            mal(f'{cod}: está en la página y no en el verificador')

    for cod, datos in FUENTE.items():
        m = re.search(r"\{\s*cod:'%s'.*?enun:`([^`]*)`" % cod, html, flags=re.S)
        if not m:
            mal(f'{cod}: no encuentro su enunciado')
            continue
        for d in datos:
            if d not in m.group(1):
                mal(f'{cod}: el enunciado no trae «{d}», como el material')

    n_teo = len(teorias)
    n_preg = len(re.findall(r"\bpregunta:[`']", html))
    if n_preg < n_teo:
        mal(f'hay {n_teo} teorías y solo {n_preg} preguntas')

    # las notas y la teoría dicen los números que salieron acá
    for frag in (f'{n33}', '317', f'{mcm30}'):
        if frag not in html:
            mal(f'la página no trae {frag}')

    # el desafío
    if f"final:'hay que caminar {t39} segundos'" not in html:
        mal(f'el desafío no termina en {t39} segundos')
    for frag in (f"' = {mcm39}'", f"' = {t39}'", "'d = 33 · 6 m'"):
        if frag not in html:
            mal(f'el desafío no trae {frag}')

    transcripto = {t for _, ops, _ in EJ.values() for t, _ in ops}
    cadenas = re.findall(r"'([^'\n]*)'", html)
    cadenas += [re.sub(r'\$\{[^{}]*\}', '', s) for s in re.findall(r'`([^`]*)`', html)]
    for s in cadenas:
        if s in transcripto or s in TAL_CUAL:
            continue
        if len(re.findall(r'\s=\s', s)) > 1:
            mal(f'dos igualdades en un renglón: {s[:90]}')
    if '—' in html:
        mal('la página tiene rayas (—)')
    if re.search(r'Duarte|Rol[oó]n|Caballero|Camila', html, flags=re.I):
        mal('la página nombra a otro docente')
    print(f'  {len(EJ)} ejercicios, {sum(len(o) for _, o, _ in EJ.values())} opciones controladas; {n_teo} teorías')


def diagnostico():
    """El diagnóstico inicial (I1 a I5) y el final (F1 a F5): la prueba de
    antes y después. Son propios, uno por tema, y van de a pares: I1 y F1
    miden lo mismo con otros números. Cada respuesta se busca recorriendo
    (sin las fórmulas de la clase) y cada opción incorrecta se rehace desde
    el error que la produce. Se devuelve, por código:
    (tema, datos del enunciado, [(texto, ok)])."""
    print('El diagnóstico inicial y el final')
    D = {}

    def item(cod, tema, datos, opciones):
        textos = [t for t, _ in opciones]
        if len(set(textos)) != 5 or sum(ok for _, ok in opciones) != 1:
            mal(f'{cod}: tiene que tener 5 opciones distintas y una sola correcta')
        D[cod] = (tema, datos, opciones)
        k = [ok for _, ok in opciones].index(True)
        print(f'  {cod}  la {"ABCDE"[k]}: {textos[k]}')

    # tema 1: cuántos múltiplos de d hay entre a y b
    def multiplos(cod, d, a, b, orden):
        bien = len([n for n in range(a + 1, b) if n % d == 0])
        if bien != b // d - a // d:                     # el otro camino: los de hasta b menos los de hasta a
            mal(f'{cod}: contando y restando cocientes no da lo mismo')
        ops = {'ok': bien, 'distancia': (b - a) // d, 'hasta-b': b // d, 'resta': b - a, 'hasta-a': a // d}
        item(cod, '1', [str(d), str(a), str(b)], [(str(ops[e]), e == 'ok') for e in orden])

    multiplos('I1', 6, 45, 128, ['distancia', 'ok', 'hasta-b', 'resta', 'hasta-a'])
    multiplos('F1', 8, 45, 170, ['distancia', 'hasta-b', 'resta', 'ok', 'hasta-a'])

    # tema 2: la cifra del □ para que sea divisible por 3 y por 4
    def cifra(cod, izq, der, orden):
        num = lambda c: int(f'{izq}{c}{der}')
        bien = [c for c in range(10) if num(c) % 3 == 0 and num(c) % 4 == 0]
        if len(bien) != 1:
            mal(f'{cod}: {len(bien)} cifras posibles')
            return
        ops = []
        for c, que in orden:
            n = num(c)
            # el otro camino: los criterios (suma de cifras; las dos últimas cifras)
            c3, c4 = sum(int(x) for x in str(n)) % 3 == 0, int(str(n)[-2:]) % 4 == 0
            if (c3, c4) != (n % 3 == 0, n % 4 == 0):
                mal(f'{cod}: los criterios no coinciden con dividir')
            if que == 'ok' and not (c3 and c4) or que == '3' and (c3, c4) != (True, False) or que == '4' and (c3, c4) != (False, True):
                mal(f'{cod}: la cifra {c} no cumple lo que dice su error ({que})')
            ops.append((str(c), que == 'ok'))
        item(cod, '2', [f'{izq}□{der}'], ops)

    cifra('I2', 7, 4, [(1, '3'), (0, '4'), (7, '3'), (4, 'ok'), (8, '4')])
    cifra('F2', 8, 2, [(5, 'ok'), (2, '3'), (3, '4'), (8, '3'), (7, '4')])

    # tema 3: cuántos primos hay entre a y b
    def primos(cod, a, b, orden):
        rango = range(a + 1, b)
        impares = [n for n in rango if n % 2]
        ops = {'ok': len([n for n in rango if es_primo(n)]),
               'impares': len(impares),
               'solo-3': len([n for n in impares if n % 3]),
               'sin-7': len([n for n in impares if n % 3 and n % 5]),
               'terminan': len([n for n in rango if n % 10 in (1, 3, 7, 9)])}
        # el otro camino: la criba, tachando múltiplos de 2, 3, 5 y 7 (alcanza hasta 120)
        criba = [n for n in rango if all(n % p or n == p for p in (2, 3, 5, 7))]
        if b > 121 or len(criba) != ops['ok']:
            mal(f'{cod}: la criba y la definición no dan lo mismo')
        item(cod, '3', [str(a), str(b)], [(str(ops[e]), e == 'ok') for e in orden])

    primos('I3', 20, 50, ['ok', 'impares', 'solo-3', 'sin-7', 'terminan'])
    primos('F3', 60, 100, ['impares', 'solo-3', 'ok', 'terminan', 'sin-7'])

    # tema 4: cuántos divisores tiene n
    def cuantos(cod, n, orden):
        f = factoriza(n)
        prod = suma = 1
        for e in f.values():
            prod *= e + 1
        bien = len(divisores(n))
        if bien != prod:
            mal(f'{cod}: contando uno por uno y con la fórmula no da lo mismo')
        pe = 1
        for e in f.values():
            pe *= e
        ops = {'ok': bien, 'producto-exp': pe, 'suma-exp': sum(f.values()),
               'suma-mas-uno': sum(e + 1 for e in f.values()), 'sin-extremos': bien - 2}
        item(cod, '4', [str(n)], [(str(ops[e]), e == 'ok') for e in orden])

    cuantos('I4', 72, ['producto-exp', 'suma-exp', 'suma-mas-uno', 'sin-extremos', 'ok'])
    cuantos('F4', 180, ['producto-exp', 'ok', 'suma-exp', 'sin-extremos', 'suma-mas-uno'])

    # tema 5: dos colectivos que salen juntos; a qué hora vuelven a salir juntos
    def colectivos(cod, h, p, q, orden):
        hora = lambda m: f'{h + m // 60}:{m % 60:02d}'
        # recorriendo los minutos: el primero en que salen los dos
        t = next(m for m in range(1, p * q + 1) if m % p == 0 and m % q == 0)
        if t != mcm(p, q):
            mal(f'{cod}: recorriendo y con el MCM no da lo mismo')
        ops = {'ok': t, 'mcd': mcd(p, q), 'producto': p * q, 'suma': p + q, 'mayor': max(p, q)}
        item(cod, '5', [str(p), str(q), f'{h}:00'], [(hora(ops[e]), e == 'ok') for e in orden])

    colectivos('I5', 6, 12, 18, ['mcd', 'mayor', 'ok', 'producto', 'suma'])
    colectivos('F5', 7, 15, 20, ['mcd', 'suma', 'producto', 'mayor', 'ok'])
    return D


def controla_diagnostico(D):
    html = PAGINA.read_text(encoding='utf-8')
    if not re.search(r'data-diapos="[^"]*\.diagnostico-diapo', html):
        mal('data-diapos no trae .diagnostico-diapo')
    if 'id="diagnostico-lugar"' not in html:
        mal('la página no tiene #diagnostico-lugar')
    ini = html.find('const DIAGNOSTICO')
    fin = html.find('final:{', ini)
    if ini < 0 or fin < 0:
        mal('falta el DIAGNOSTICO con su final')
        return
    pag = {}
    for cod, tema, enun, ops in re.findall(
            r"\{\s*cod:'([IF]\d)',\s*tema:'(\d)',\s*enun:'([^']*)',\s*opciones:\[(.*?)\]\s*\}", html, flags=re.S):
        lista = re.findall(r"\{\s*t:'([^']*)',\s*(?:(ok:true)|error:'([^']*)')\s*\}", ops)
        pag[cod] = (tema, enun, lista, html.find(f"cod:'{cod}'"))
    for cod, (tema, datos, ops) in D.items():
        if cod not in pag:
            mal(f'{cod}: no está en la página')
            continue
        t, enun, lista, pos = pag[cod]
        if t != tema:
            mal(f'{cod}: es del tema {tema}, la página dice {t}')
        if [(a, bool(ok)) for a, ok, _ in lista] != ops:
            mal(f'{cod}: las opciones de la página no son las calculadas: {[(a, bool(ok)) for a, ok, _ in lista]}')
        for a, ok, err in lista:
            if not ok and not err:
                mal(f'{cod}: la opción «{a}» no anota de qué error sale')
        for d in datos:
            if d not in enun:
                mal(f'{cod}: el enunciado no trae «{d}»')
        if (cod[0] == 'I') != (pos < fin):
            mal(f'{cod}: está en el diagnóstico equivocado')
    for cod in pag:
        if cod not in D:
            mal(f'{cod}: está en la página y no en el verificador')
    for k in range(1, 6):
        if D[f'I{k}'][0] != D[f'F{k}'][0]:
            mal(f'I{k} y F{k} no miden el mismo tema')
    for pre in 'IF':
        letras = [[ok for _, ok in D[f'{pre}{k}'][2]].index(True) for k in range(1, 6)]
        if len(set(letras)) < 4:
            mal(f'el diagnóstico {pre}: la correcta cae casi siempre en la misma letra')
    print(f'  {len(pag)} ítems en la página, 5 y 5, de a pares')


tema1()
tema2()
tema3()
n33 = tema4()
mcm30 = tema5()
t39, mcm39, pasos39 = desafio()
print(f'  E39  hay que caminar {t39} segundos (MCM {mcm39} cm, {pasos39} pasos)')
controla_pagina(n33, mcm30, t39, mcm39, pasos39)
controla_diagnostico(diagnostico())
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
