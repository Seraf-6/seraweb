"""Verificación de la clase del cursillo: Vectores en el plano.

`cursillo/clases/vectores.html` es la teoría de la unidad 2 de Geometría
Analítica y Cálculo (vectores en el plano), con un ejemplo resuelto por tema
y, enseguida, los ejercicios del Ejercitario 2.1 y del 2.2 de fijación que
usan ese tema, de menor a mayor, con sus opciones tal cual. Acá cada cosa se
rehace por un camino distinto del de la clase:

1. Los ejercicios numéricos, con sympy (exacto) y, donde se puede, por otro
   camino: despejar y sustituir, o recorrer.
2. Los de afirmaciones generales («si dos vectores son opuestos…»), probando
   cada afirmación sobre muchos vectores al azar con Fraction: de ahí sale
   cuáles son verdaderas, y de ahí la opción.
3. Los de figuras, con coordenadas al azar que respetan la figura: la
   respuesta tiene que salir igual con todas.
4. La opción marcada ok:true es la que salió acá, una sola; y la que lleva
   un error que es una cuenta se rehace desde ese error.
5. Los ejemplos de la teoría: cada renglón del cuaderno; el diagnóstico,
   cada ítem y cada opción incorrecta desde su error.
6. Cada ejercicio va después del tema que usa (tras:), de menor a mayor
   dentro del tema (el orden está escrito acá), y su resolución está en las
   Notas de ese tema.
7. La notación: cada fórmula con subíndices dice qué son (A = (x₁, y₁)…),
   los versores de los ejes van sin punto (ı, ȷ), el versor y los colineales
   piden un vector no nulo, y la recta de la dirección pasa por los dos
   extremos del vector. No hay rayas (—), ni dos igualdades en un renglón,
   ni el nombre de otro docente.

    python verificacion/cursillo_vectores.py
"""
import random
import re
import sys
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = RAIZ / 'cursillo' / 'clases' / 'vectores.html'
fallos = []
azar = random.Random(2026)


def mal(m):
    fallos.append(m)
    print('   FALLA:', m)


# ── vectores con Fraction: el camino «a mano» ──
def suma(*vs):
    return tuple(sum(c) for c in zip(*vs))


def por(k, v):
    return tuple(k * c for c in v)


def resta(u, v):
    return suma(u, por(-1, v))


def pe(u, v):
    return u[0] * v[0] + u[1] * v[1]


def mod2(v):
    return pe(v, v)


def paralelos(u, v):
    return u[0] * v[1] - u[1] * v[0] == 0


def al_azar(n=8):
    while True:
        v = (F(azar.randint(-n, n)), F(azar.randint(-n, n)))
        if v != (0, 0):
            return v


EJ = {}       # cod -> (tema, [(texto de la página, ok)], {k: error}, la letra)


def ejercicio(cod, tema, textos, verdades, errores=None):
    k = [i for i, v in enumerate(verdades) if v]
    if len(k) != 1:
        mal(f'{cod}: las opciones verdaderas son {k}, tiene que haber una sola')
        return
    if len(set(textos)) != len(textos):
        mal(f'{cod}: dos opciones iguales')
    EJ[cod] = (tema, [(t, i == k[0]) for i, t in enumerate(textos)], errores or {}, 'ABCDE'[k[0]])
    print(f'  {cod:7s} la {"ABCDE"[k[0]]}: {textos[k[0]]}')


def cuantas(verdades, piden):
    return sum(1 for v in verdades if v == (piden == 'verdaderas'))


PALABRAS = {'Una': 1, 'Dos': 2, 'Tres': 3, 'Cuatro': 4, 'Cero': 0, 'Ninguna': 0,
            'una': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cero': 0}


# ═══════════════════════ La lista de ejercicios ═══════════════════════
# cada ejercicio va después del tema que usa, de menor a mayor dentro del tema
# (1 qué es un vector, 2 módulo y tipos, 3 operaciones, 4 producto escalar,
# 5 ángulo y proyección), tras la última teoría del tema
POR_TEMA = {2: ('versor', ['E22-6']),
            3: ('resta-escalar', ['E21-1', 'E21-2', 'E21-3', 'E21-4', 'E21-12']),
            4: ('cuadrado', ['E21-16', 'E21-10', 'E21-9']),
            5: ('proyeccion', ['E21-15', 'E22-7', 'E21-8', 'E21-17', 'E21-11', 'E21-19'])}
ORDEN = [c for n in sorted(POR_TEMA) for c in POR_TEMA[n][1]]
DESAFIO = 'E21-20'
TEMA = {c: n for n in POR_TEMA for c in POR_TEMA[n][1]} | {DESAFIO: 5}


def ejercicios():
    print('La lista de ejercicios')
    # E21-1: x = 3(b − 2a) + 6a − 2b con a = (−1, 3) y b = (4, 8)
    a, b = (F(-1), F(3)), (F(4), F(8))
    x = suma(por(3, resta(b, por(2, a))), por(6, a), por(-2, b))
    A, B = sp.Matrix([-1, 3]), sp.Matrix([4, 8])
    if list(3 * (B - 2 * A) + 6 * A - 2 * B) != list(x) or x != b:     # simplificado, x es b
        mal('E21-1: x no es b')
    ejercicio('E21-1', 3, ['8', '12', '10', '7', '24'], [int(t) == sum(x) for t in ['8', '12', '10', '7', '24']])

    # E21-16: la figura, u = (4, 5) y v = (3, −4)
    u, v = (4, 5), (3, -4)
    ver = [por(-1, v) == (-3, -4), pe(u, v) == -8, por(F(1, 2), u) == (2, 5), resta(u, v) == (1, 9)]
    textos = ['tres', 'dos', 'una', 'cuatro', 'cero']
    ejercicio('E21-16', 1, textos, [PALABRAS[t] == cuantas(ver, 'verdaderas') for t in textos])

    # E22-6: ‖a‖ = 15, la dirección y el sentido de b = (3, −4)
    b = sp.Matrix([3, -4])
    a = 15 * b / b.norm()
    k = sp.symbols('k', positive=True)                  # otro camino: a = k b, con ‖k b‖ = 15
    kk = sp.solve(sp.Eq((k * b).norm(), 15), k)
    if kk != [3] or list(a) != [9, -12]:
        mal('E22-6: a no es (9, −12)')
    textos = ['3', '12', '−3', '5', '−5']
    num = lambda t: int(t.replace('−', '-'))
    ejercicio('E22-6', 2, textos, [num(t) == sum(a) for t in textos],
              {0: 3, 3: 5})            # 3: se le fue el signo; 5: dio el módulo de b

    # E21-2: (2, −4) = k(−2, 1) + m(3, −2)
    k, m = sp.symbols('k m')
    s = sp.solve([sp.Eq(-2 * k + 3 * m, 2), sp.Eq(k - 2 * m, -4)], [k, m])
    if suma(por(s[k], (-2, 1)), por(s[m], (3, -2))) != (2, -4):
        mal('E21-2: k y m no dan w')
    textos = ['6', '8', '10', '2', '14']
    ejercicio('E21-2', 3, textos, [int(t) == s[k] + s[m] for t in textos],
              {0: s[m], 1: s[k], 3: s[k] - s[m]})

    # E21-3: el cuadrado. A sube, B va a la derecha, C baja, D vuelve; E va del
    # vértice de abajo al centro y F del centro al vértice de arriba
    for _ in range(200):
        x0, y0, l = F(azar.randint(-9, 9)), F(azar.randint(-9, 9)), F(azar.randint(1, 9))
        P = [(x0, y0), (x0, y0 + l), (x0 + l, y0 + l), (x0 + l, y0)]
        O = (x0 + l / 2, y0 + l / 2)
        V = {'A': resta(P[1], P[0]), 'B': resta(P[2], P[1]), 'C': resta(P[3], P[2]),
             'D': resta(P[0], P[3]), 'E': resta(O, P[0]), 'F': resta(P[1], O)}
        r = suma(*V.values())
        ops = [V['D'], por(2, V['A']), por(3, V['A']), por(2, V['D']), V['A']]
        if [o == r for o in ops] != [False, False, False, False, True]:
            mal('E21-3: la resultante no es A')
            break
    ejercicio('E21-3', 3, ['D', '2A', '3A', '2D', 'A'], [False, False, False, False, True])

    # E21-4: el pentágono P0…P4 (P0 abajo a la izquierda, en el sentido del reloj)
    ok = None
    for _ in range(200):
        P = [(F(azar.randint(-20, 20)), F(azar.randint(-20, 20))) for _ in range(5)]
        V = {'A': resta(P[1], P[0]), 'B': resta(P[2], P[1]), 'C': resta(P[3], P[2]),
             'D': resta(P[3], P[4]), 'E': resta(P[4], P[0]), 'F': resta(P[0], P[3]), 'G': resta(P[2], P[0])}
        Z = (0, 0)
        ver = [suma(V['A'], V['B'], por(-1, V['F']), V['C']) == Z, suma(V['A'], V['G'], V['B']) == Z,
               suma(V['E'], V['F']) == V['D'], suma(V['G'], V['C']) == suma(V['D'], V['E']),
               suma(V['C'], V['G']) == V['F']]
        ok = ver if ok is None else ok
        if ver != ok:
            mal('E21-4: lo que vale depende de la forma del pentágono')
            break
    ejercicio('E21-4', 3, ['A + B − F + C = 0', 'A + G + B = 0', 'E + F = D', 'G + C = D + E', 'C + G = F'], ok)

    # E21-12: p = (3, 2), q = (2, −3), r = (4, 6)
    p, q, r = (3, 2), (2, -3), (4, 6)
    I = paralelos(resta(p, q), resta(q, r))
    II = not paralelos(suma(p, q, r), por(3, q))
    pq = suma(p, q)
    III = paralelos(pq, (-10, 2)) and pe(pq, (-10, 2)) < 0
    ver = {'I': I, 'II': II, 'III': III}
    quiero = {k for k, x in ver.items() if x}
    textos = ['solo I', 'solo II', 'solo III', 'solo I y II', 'solo II y III']
    ejercicio('E21-12', 2, textos, [set(re.findall(r'\bI+\b', t)) == quiero for t in textos])

    # E21-10: u = (1, a), v = (−a, 1), a entero positivo
    falsas = set()
    for a in range(1, 60):
        u, v = (1, a), (-a, 1)
        ver = [pe(u, v) == a, pe(u, v) == 0, mod2(u) == mod2(v), paralelos(u, v)]   # cos 0 ⇔ u · v = 0
        falsas.add(cuantas(ver, 'falsas'))
    if falsas != {2}:
        mal(f'E21-10: la cantidad de falsas depende de a: {falsas}')
    textos = ['Una', 'Dos', 'Tres', 'Todas', 'Ninguna']
    cant = {'Todas': 4}
    ejercicio('E21-10', 4, textos, [cant.get(t, PALABRAS.get(t)) == 2 for t in textos])

    # E21-15: la falsa. Cada afirmación, sobre vectores al azar
    vale = {k: True for k in 'ABCDE'}
    for _ in range(3000):
        u, v = al_azar(), al_azar()
        k = F(azar.randint(-6, 6)) or F(1)
        w = por(k, u)                                   # colineal con u
        if k > 0 and pe(u, w) ** 2 != mod2(u) * mod2(w):           # ángulo 0°: cos = 1
            vale['A'] = False
        if k < 0 and not paralelos(u, w):                           # ángulo 180°: colineales
            vale['B'] = False
        # mismo versor: u / ‖u‖ = v / ‖v‖ ⇔ u y v con la misma dirección y sentido
        if paralelos(u, v) and pe(u, v) > 0 and u != v:
            vale['D'] = False
        pr = por(F(pe(u, v), mod2(v)), v)                         # la proyección es k · v
        if not paralelos(pr, v):
            vale['E'] = False
    if not paralelos((1, 2), (-2, -4)) or pe((1, 2), (-2, -4)) >= 0:   # colineales y opuestos: C
        vale['C'] = False
    textos = ['Dos vectores no nulos que forman un ángulo de 0° son colineales.',
              'Dos vectores no nulos que forman un ángulo de 180° son colineales.',
              'Dos vectores colineales pueden tener sentidos opuestos.',
              'Si dos vectores no nulos tienen el mismo versor, dichos vectores son iguales.',
              'Dados los vectores u ≠ 0 y v ≠ 0, el vector proy_v u es el producto de un escalar por el vector v.']
    ejercicio('E21-15', 2, textos, [not vale[k] for k in 'ABCDE'])

    # E22-7: cuántas falsas
    I = II = III = IV = True
    for _ in range(3000):
        u = al_azar()
        if pe(u, por(-1, u)) == 0:                     # opuestos: u · v = 0
            pass
        else:
            I = False
        v = al_azar()
        if pe(u, v) < 0:                               # negativo: obtuso o llano, cos en [−1, 0)
            c2 = F(pe(u, v) ** 2, mod2(u) * mod2(v))
            if not (pe(u, v) < 0 and c2 <= 1):
                II = False
        w = al_azar()
        if pe(suma(u, w), resta(u, w)) == 0 and mod2(u) != mod2(w):
            IV = False
        if pe(suma(u, w), resta(u, w)) != mod2(u) - mod2(w):         # la identidad de fondo
            IV = False
    # III: un vector unitario es el versor de sí mismo (que no es nulo)
    for e in [(1, 0), (0, -1), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]:
        if mod2(e) != 1 or por(F(1), e) != e:
            III = False
    falsas = cuantas([I, II, III, IV], 'falsas')
    textos = ['Una', 'Cuatro', 'Cero', 'Dos', 'Tres']
    ejercicio('E22-7', 4, textos, [PALABRAS[t] == falsas for t in textos])

    # E21-8: ‖u‖ = 4, ‖v‖ = 6, ‖u + v‖ = 7: el coseno
    uv = sp.Rational(49 - 16 - 36, 2)
    c = uv / (4 * 6)
    # otro camino: u = (4, 0) y v = 6(cos, sen); ‖u + v‖ tiene que dar 7
    s = sp.sqrt(1 - c ** 2)
    if sp.simplify((4 + 6 * c) ** 2 + (6 * s) ** 2 - 49) != 0:
        mal('E21-8: con el coseno hallado, ‖u + v‖ no es 7')
    lee = {'−3': -3, '1/16': sp.Rational(1, 16), '−1/16': sp.Rational(-1, 16), '2/3': sp.Rational(2, 3), '−2/3': sp.Rational(-2, 3)}
    textos = list(lee)
    ejercicio('E21-8', 5, textos, [lee[t] == c for t in textos], {0: 2 * uv, 1: -c})

    # E21-9: ‖u + v‖ = 4 y ‖u − v‖ = 3: u · v
    uv = sp.Rational(16 - 9, 4)
    lee = {'7/3': sp.Rational(7, 3), '4/3': sp.Rational(4, 3), '7/2': sp.Rational(7, 2),
           '7/4': sp.Rational(7, 4), '3/4': sp.Rational(3, 4)}
    # otro camino: u + v = (4, 0) y u − v = 3(cos t, sen t): u · v = (‖u+v‖² − ‖u−v‖²) : 4 para cualquier t
    for t in range(0, 360, 15):
        ct, st = sp.cos(sp.rad(t)), sp.sin(sp.rad(t))
        U = (sp.Rational(1, 2) * (4 + 3 * ct), sp.Rational(1, 2) * 3 * st)
        Vv = (sp.Rational(1, 2) * (4 - 3 * ct), -sp.Rational(1, 2) * 3 * st)
        if sp.simplify(U[0] * Vv[0] + U[1] * Vv[1] - uv) != 0:
            mal('E21-9: u · v depende de u y v')
            break
    textos = list(lee)
    ejercicio('E21-9', 4, textos, [lee[t] == uv for t in textos], {2: sp.Rational(7, 2), 1: sp.Rational(4, 3)})

    # E21-17: cos α = 5/8, u · v = 15, ‖u‖ = x, ‖v‖ = x + 2
    x = sp.symbols('x')
    sol = [r for r in sp.solve(sp.Eq(x * (x + 2) * sp.Rational(5, 8), 15), x) if r > 0]
    if sol != [4]:
        mal(f'E21-17: x puede ser {sol}')
    total = sol[0] + sol[0] + 2
    neg = [r for r in sp.solve(sp.Eq(x * (x + 2) * sp.Rational(5, 8), 15), x) if r < 0][0]
    textos = ['4', '6', '−6', '−10', '10']
    ejercicio('E21-17', 5, textos, [num(t) == total for t in textos],
              {0: sol[0], 1: sol[0] + 2, 3: neg + neg + 2})

    # E21-11: el ángulo entre −2u y 3v, con u = (3, 0) y v = (1, −√2); su suplemento
    U, Vv = -2 * sp.Matrix([3, 0]), 3 * sp.Matrix([1, -sp.sqrt(2)])
    cos = sp.nsimplify(U.dot(Vv) / (U.norm() * Vv.norm()))
    if sp.simplify(cos + 1 / sp.sqrt(3)) != 0:
        mal('E21-11: el coseno no es −1/√3')
    ang = sp.acos(cos) * 180 / sp.pi

    def gms(x):
        s = int(sp.N(x * 3600, 40).round())
        return f'{s // 3600}° {s % 3600 // 60}′ {s % 60}″'
    sup = gms(180 - ang)
    textos = ['55° 30′ 45″', '124° 29′ 15″', '54° 44′ 8″', '35° 15′ 52″', '125° 15′ 52″']
    ejercicio('E21-11', 5, textos, [t == sup for t in textos], {4: gms(ang), 3: gms(ang - 90)})

    # E21-19: la proyección del versor de u = (x, x), x > 0, sobre el eje X
    for xx in range(1, 30):
        u = sp.Matrix([xx, xx])
        e = u / u.norm()
        i = sp.Matrix([1, 0])
        pr = (e.dot(i) / i.dot(i)) * i
        if list(pr) != [sp.sqrt(2) / 2, 0]:
            mal('E21-19: la proyección depende de x')
            break
    r2 = sp.sqrt(2) / 2
    lee = {'(1, 0)': (1, 0), '(√2/2, √2/2)': (r2, r2), '(−1, 0)': (-1, 0), '(√2/2, 0)': (r2, 0), '(−√2/2, 0)': (-r2, 0)}
    textos = list(lee)
    ejercicio('E21-19', 5, textos, [lee[t] == (r2, 0) for t in textos], {1: (r2, r2)})

    # E21-20 (el desafío): el ángulo de u y v es el doble del de u y su
    # proyección sobre v; u ≠ v y ‖u‖ = ‖v‖ = 4. Se recorre el ángulo de a
    # milésimas de grado: la proyección apunta como v si u · v > 0 (el ángulo
    # con u es θ) y al revés si u · v < 0 (es 180° − θ)
    sols = []
    for k in range(1, 180000):
        th = F(k, 1000)
        con_pr = th if th < 90 else (180 - th if th > 90 else None)
        if con_pr is not None and th == 2 * con_pr:
            sols.append(th)
    if sols != [120]:
        mal(f'E21-20: el ángulo puede ser {sols}')
    uv = 16 * sp.cos(sp.rad(120))
    textos = ['−2', '2', '4', '8', '−8']
    ejercicio('E21-20', 5, textos, [num(t) == uv for t in textos], {3: -uv})
    return {'th20': 120, 'uv20': uv}


# ═══════════════════════ La teoría y sus ejemplos ═══════════════════════
def teoria():
    print('La teoría y los ejemplos')
    ok = True
    ok &= resta((3, 5), (-1, 2)) == (4, 3)                       # componentes de AB
    ok &= mod2((3, 4)) == 25                                      # módulo 5
    ok &= por(F(1, 10), (6, 8)) == (F(3, 5), F(4, 5))             # versor de (6, 8)
    ok &= suma((2, 1), (1, 3)) == (3, 4)                          # la suma
    ok &= por(3, (2, -1)) == (6, -3) and por(-1, (2, -1)) == (-2, 1)
    ok &= pe((3, 2), (4, -1)) == 10 and pe((3, 4), (3, 4)) == 25
    ok &= pe((2, 3), (-3, 2)) == 0
    ok &= F(6, 3 * 4) == F(1, 2)                                  # cos 60°
    ok &= por(F(pe((2, 3), (4, 0)), mod2((4, 0))), (4, 0)) == (2, 0)   # proyección
    if not ok:
        mal('un número de la teoría no da')

    # ejemplo del tema 1: AB = DC
    A, B, C = (2, -1), (5, 3), (4, 6)
    AB = resta(B, A)
    D = resta(C, AB)                                              # D = C − AB
    if AB != (3, 4) or D != (1, 2) or resta(C, D) != AB:
        mal('el ejemplo del tema 1 no da')
    # ejemplo del tema 2: ‖(5, m + 2)‖ = 13, m > 0
    m = sp.symbols('m')
    ms = sp.solve(sp.Eq(25 + (m + 2) ** 2, 169), m)
    if sorted(ms) != [-14, 10]:
        mal(f'el ejemplo del tema 2 da {ms}')
    # ejemplo del tema 3: (5, 3) = k(1, 2) + m(3, −1)
    k = sp.symbols('k')
    s = sp.solve([sp.Eq(k + 3 * m, 5), sp.Eq(2 * k - m, 3)], [k, m])
    if (s[k], s[m]) != (2, 1) or suma(por(2, (1, 2)), por(1, (3, -1))) != (5, 3):
        mal('el ejemplo del tema 3 no da')
    # ejemplo del tema 4: ‖u‖ = 5, ‖v‖ = 3, ‖u + v‖ = 7
    if F(49 - 25 - 9, 2) != F(15, 2):
        mal('el ejemplo del tema 4 no da')
    # ejemplo del tema 5: el ángulo de (1, 2) y (3, 1)
    c = sp.Rational(pe((1, 2), (3, 1))) / sp.sqrt(mod2((1, 2)) * mod2((3, 1)))
    if sp.acos(c) != sp.pi / 4:
        mal('el ejemplo del tema 5 no da 45°')


# ═══════════════════════ El diagnóstico ═══════════════════════
def diagnostico():
    print('El diagnóstico')
    D = {}

    def item(cod, tema, ops):
        textos = [t for t, _ in ops]
        if len(set(textos)) != 5 or sum(ok for _, ok in ops) != 1:
            mal(f'{cod}: tiene que tener 5 opciones distintas y una sola correcta')
        D[cod] = (tema, ops)
        k = [ok for _, ok in ops].index(True)
        print(f'  {cod}  la {"ABCDE"[k]}: {textos[k]}')

    vt = lambda v: '(' + ', '.join(str(c).replace('-', '−') for c in v) + ')'

    # tema 1: las componentes de AB
    def componentes(cod, A, B, orden):
        ops = {'ok': resta(B, A), 'al-reves': resta(A, B), 'sumo': suma(A, B),
               'signo-y': (B[0] - A[0], B[1] - abs(A[1]) if A[1] < 0 else B[1] + A[1]),
               'signo-x': (B[0] - abs(A[0]), B[1] - A[1]), 'cambio': resta(B, A)[::-1]}
        item(cod, 1, [(vt(ops[e]), e == 'ok') for e in orden])

    componentes('I1', (2, -1), (5, 3), ['al-reves', 'ok', 'sumo', 'signo-y', 'cambio'])
    componentes('F1', (-1, 4), (3, 1), ['sumo', 'al-reves', 'signo-x', 'cambio', 'ok'])

    # tema 2: el módulo
    def modulo(cod, v, orden):
        x, y = v
        r = lambda n: str(sp.sqrt(n)).replace('sqrt(', '√').replace(')', '').replace('*', '')
        ops = {'ok': r(x * x + y * y), 'sumo': str(x + y).replace('-', '−'), 'abs': str(abs(x) + abs(y)),
               'sin-raiz': str(x * x + y * y), 'resto': r(abs(x * x - y * y))}
        item(cod, 2, [(ops[e], e == 'ok') for e in orden])

    modulo('I2', (-6, 8), ['sumo', 'abs', 'sin-raiz', 'ok', 'resto'])
    modulo('F2', (5, -12), ['abs', 'sin-raiz', 'resto', 'ok', 'sumo'])

    # tema 3: 2u − v
    def combina(cod, u, v, orden):
        ops = {'ok': resta(por(2, u), v), 'sumo': suma(por(2, u), v), 'sin-2': resta(u, v),
               'signo-y': (2 * u[0] - v[0], 2 * u[1] + v[1]) if v[1] > 0 else (2 * u[0] - v[0], 2 * u[1] - abs(v[1])),
               'al-reves': resta(v, por(2, u))}
        item(cod, 3, [(vt(ops[e]), e == 'ok') for e in orden])

    combina('I3', (2, -1), (-3, 4), ['sin-2', 'sumo', 'ok', 'signo-y', 'al-reves'])
    combina('F3', (-1, 3), (4, -2), ['al-reves', 'ok', 'sumo', 'sin-2', 'signo-y'])

    # tema 4: m para que sean perpendiculares
    def perp(cod, u, v, orden):
        m = sp.symbols('m')
        V = [m if c == 'm' else c for c in v]
        ops = {'ok': sp.solve(sp.Eq(u[0] * V[0] + u[1] * V[1], 0), m)[0],
               'paralelo': sp.solve(sp.Eq(u[0] * V[1] - u[1] * V[0], 0), m)[0],
               'sumo': sp.solve(sp.Eq(u[0] + V[0] + u[1] + V[1], 0), m)[0]}
        ops['signo'] = -ops['ok']
        ops['al-reves'] = 1 / ops['ok']
        txt = lambda q: (('−' if q < 0 else '') + (str(abs(q)) if q.q == 1 else f'{abs(q.p)}/{q.q}'))
        item(cod, 4, [(txt(ops[e]), e == 'ok') for e in orden])

    perp('I4', (3, -2), (4, 'm'), ['ok', 'signo', 'paralelo', 'sumo', 'al-reves'])
    perp('F4', (2, 5), ('m', -4), ['paralelo', 'al-reves', 'signo', 'sumo', 'ok'])

    # tema 5: ‖u + v‖ con el ángulo de 60°
    def largo(cod, a, b, orden):
        uv = sp.Rational(a * b, 2)                      # a · b · cos 60°
        r = lambda n: str(sp.sqrt(n)).replace('sqrt(', '√').replace(')', '')
        ops = {'ok': r(a * a + b * b + 2 * uv), 'sumo': str(a + b), 'perp': r(a * a + b * b),
               'resto': r(a * a + b * b - 2 * uv), 'sin-raiz': str(a * a + b * b + 2 * uv)}
        item(cod, 5, [(ops[e], e == 'ok') for e in orden])

    largo('I5', 3, 4, ['sumo', 'perp', 'resto', 'sin-raiz', 'ok'])
    largo('F5', 2, 5, ['ok', 'sumo', 'resto', 'sin-raiz', 'perp'])
    return D


# ═══════════════════════ La página ═══════════════════════
def lee_opciones(bloque):
    """las opciones de un ejercicio, tal como están escritas en la página:
    (texto, ok, error); el texto en limpio (sin M(), Q() ni V())"""
    lista = re.findall(r"\{\s*t:(?:'([^']*)'|`([^`]*)`)(?:,\s*(?:(ok:true)|error:'([^']*)'))?\s*\}", bloque)
    return [(limpia(a or b), bool(ok), err) for a, b, ok, err in lista]


def limpia(s):
    s = re.sub(r"\$\{Q\('?([^',)]*)'?,\s*'?([^',)]*)'?\)\}", r'\1/\2', s)
    s = re.sub(r"\$\{(?:M|V|VV|W)\('([^']*)'\)\}", r'\1', s)
    s = s.replace('~', '')
    s = re.sub(r"\$\{(?:CERO|NULO)\}", '0', s)
    return s


def controla_sombra(html):
    """De dónde sale el coseno: v acostado, u con un ángulo θ. Las cuentas de
    la diapositiva se rehacen con sympy, y el dibujo tiene que poder hacerse
    con los números de SOMBRA (θ agudo y la sombra cayendo sobre v)."""
    a, b, t = sp.symbols('a b t', positive=True)
    u, v = (a * sp.cos(t), a * sp.sin(t)), (b, 0)
    pe_sombra = u[0] * v[0] + u[1] * v[1]
    if sp.simplify(pe_sombra - a * b * sp.cos(t)) != 0 or sp.simplify(sp.sqrt(u[0]**2 + u[1]**2) - a) != 0:
        mal('la sombra: u · v no da ‖u‖ ‖v‖ cos θ, o u no mide ‖u‖')
    # otro camino: con vectores al azar, el coseno de la fórmula es el del ángulo medido con atan2
    for _ in range(50):
        p, q = al_azar(), al_azar()
        ang = sp.atan2(p[1], p[0]) - sp.atan2(q[1], q[0])
        c = sp.Rational(pe(p, q)) / sp.sqrt(mod2(p) * mod2(q))
        if abs(sp.N(sp.cos(ang) - c, 30)) > sp.Float('1e-25'):
            mal(f'el coseno de la fórmula no es el del ángulo entre {p} y {q}')
            break
    for frag in ("R('~u = (‖~u‖ cos θ, ‖~u‖ sen θ)')", "R('~v = (‖~v‖, 0)')",
                 "R('~u · ~v = ‖~u‖ cos θ · ‖~v‖ + ‖~u‖ sen θ · 0')", "R(' = ‖~u‖ ‖~v‖ cos θ')"):
        if frag not in html:
            mal(f'la sombra no trae {frag}')
    # el teorema del coseno y la proyección, por otro camino: vectores al azar
    for _ in range(50):
        p, q = al_azar(), al_azar()
        ang = sp.atan2(p[1], p[0]) - sp.atan2(q[1], q[0])
        mu, mv = sp.sqrt(mod2(p)), sp.sqrt(mod2(q))
        resta2 = mod2(resta(p, q))
        if abs(sp.N(resta2 - (mod2(p) + mod2(q) - 2 * mu * mv * sp.cos(ang)), 30)) > 1e-20 \
                or resta2 != mod2(p) + mod2(q) - 2 * pe(p, q):
            mal(f'el teorema del coseno y el cuadrado de la resta no coinciden con {p} y {q}')
            break
        largo = mu * sp.cos(ang)                                  # la sombra, con signo
        proy = [largo * c / mv for c in q]                        # por el versor de v
        if any(abs(sp.N(a1 - F(pe(p, q), mod2(q)) * c, 30)) > 1e-20 for a1, c in zip(proy, q)):
            mal(f'la sombra por el versor no es la proyección con {p} y {q}')
            break
    for frag, que in [("¿Por qué se puede acostar v sobre el eje x?", 'el observador: acostar v'),
                      ("¿Qué pasa con la sombra si el ángulo es recto?", 'el observador: el ángulo recto'),
                      ('El supuesto escondido.', 'las Notas: el supuesto de girar'),
                      ("R('‖~u − ~v‖^2 = ‖~u‖^2 + ‖~v‖^2 − 2 ‖~u‖ ‖~v‖ cos θ')", 'las Notas: el teorema del coseno'),
                      ("R('‖~u − ~v‖^2 = ‖~u‖^2 + ‖~v‖^2 − 2 ~u · ~v')", 'las Notas: el cuadrado de la resta'),
                      ('Es la fórmula que salió de la sombra', 'el ángulo no se apoya en la sombra'),
                      ('Es la sombra de la diapositiva del coseno, convertida en vector', 'la proyección no reusa la sombra'),
                      ('Tema 5, con la sombra y seis ejercicios, 75', 'el reparto no suma los cinco minutos del tema 5')]:
        if frag not in html:
            mal(que)
    if re.search(r'\bsin\s*θ', html):
        mal('el seno se escribe sen, no sin')
    if not -1 < html.find("{ id:'sombra'") < html.find("{ id:'angulo'"):
        mal('la diapositiva de la sombra tiene que ir antes de la del ángulo')
    m = re.search(r'const SOMBRA = \{ u:([\d.]+), v:([\d.]+), grados:(\d+) \}', html)
    if not m:
        mal('no encuentro SOMBRA, los números del dibujo')
        return
    lu, lv, g = F(m.group(1)), F(m.group(2)), int(m.group(3))
    pie = lu * sp.cos(sp.rad(g))                     # el pie de la perpendicular
    if not 0 < g < 90 or not 0 < sp.N(pie) < lv:
        mal('en el dibujo de la sombra, θ no es agudo o la sombra no cae sobre v')


def controla_notacion(html):
    """Lo que se corrigió el 27/11: subíndices, ı y ȷ, condiciones, el dibujo."""
    # cada renglón con subíndices dice qué son
    for renglon in html.splitlines():
        for k in '₁₂':
            if re.search(r'[xy]' + k, renglon) and f'(x{k}, y{k})' not in renglon:
                mal(f'usa x{k} o y{k} y no dice qué son: {renglon.strip()[:80]}')
    # los versores de los ejes, sin punto
    if re.search(r"~[ij]\b", html):
        mal('quedó un ~i o un ~j con punto: van ~ı y ~ȷ')
    letras = html.split('Pizarra.letras =')[1][:120]
    if html.count('~ı') < 4 or 'ıȷ' not in letras:
        mal('faltan ı y ȷ, o Pizarra.letras no las pone en cursiva')
    if '4~ı + 3~ȷ' not in html:
        mal('las componentes no conectan AB con 4ı + 3ȷ')
    # las condiciones y las aclaraciones
    for frag, que in [("de un vector ${W('~v')} no nulo", 'el versor pide v no nulo'),
                      ("${W('~u = k · ~v')}, con ${W('~v')} no nulo", 'los colineales piden v no nulo'),
                      ('fuera 0, la proyección sería el vector nulo', 'el desafío no descarta u · v = 0'),
                      ('por eso el punto y el vector se escriben igual', 'la revela de las componentes'),
                      ('vector posición', 'las Notas no aclaran fijo, libre y posición'),
                      ('En el material, el que sale del origen', 'la igualdad no dice que fijo y libre son del material')]:
        if frag not in html:
            mal(que)
    if 'recto([0, 1]' in html:
        mal('quedó el código muerto en la proyección')
    controla_sombra(html)
    # la recta de la dirección pasa por (1, 1) y (6, 3), los extremos del vector
    m = re.search(r"guias:\[\[\[0, ([\d.]+)\], \[7, ([\d.]+)\], 2\]\]", html)
    if not m:
        mal('no encuentro la recta de la dirección')
    else:
        y0, y7 = F(m.group(1)), F(m.group(2))
        recta = lambda x: y0 + (y7 - y0) * x / 7
        if recta(1) != 1 or recta(6) != 3:
            mal('la recta de la dirección no pasa por (1, 1) y (6, 3)')


def controla_pagina(D, datos):
    print('La página')
    if not PAGINA.exists():
        mal(f'no existe {PAGINA}')
        return
    html = PAGINA.read_text(encoding='utf-8')

    # los ejercicios, con sus opciones, en el orden de la lista
    en_pagina, pos = {}, {}
    for cod, cuerpo in re.findall(r"\{\s*cod:'(E2[12]-\d+)'(.*?)opciones:\[", html, flags=re.S):
        ini = html.find(f"cod:'{cod}'")
        fin = html.find(']', html.find('opciones:[', ini))
        en_pagina[cod] = lee_opciones(html[html.find('opciones:[', ini):fin + 1])
        pos[cod] = ini
    orden = sorted(en_pagina, key=pos.get)
    if orden != ORDEN:
        mal(f'los ejercicios no van en el orden de cada tema: {orden}')
    if len(ORDEN) != 15 or len(set(ORDEN)) != 15:
        mal(f'tienen que ser 15 ejercicios distintos: {len(ORDEN)}')
    if "n:6," in html or 'temasLibro:5' not in html:
        mal('quedó el tema 6 de los ejercicios, o temasLibro no es 5')
    # cada uno, dentro de su tema, después de su teoría, y su resolución en las Notas del tema
    inicios = {n: html.find("n:%d, corto:" % n) for n in range(1, 6)}
    finales = {n: (inicios[n + 1] if n < 5 else html.find('const DESAFIO')) for n in inicios}
    for n, (tras, cods) in POR_TEMA.items():
        a, b = inicios[n], finales[n]
        for c in cods:
            i = html.find(f"cod:'{c}'")
            if not a < i < b:
                mal(f'{c}: no está en el tema {n}')
            if not html[i:i + 60].startswith(f"cod:'{c}', tras:'{tras}'"):
                mal(f'{c}: tiene que ir tras «{tras}», la última teoría del tema {n}')
            lib, num = c[1:3], c.split('-')[1]
            nombre = f"<b>Ejercitario 2.{lib[1]}{' de fijación' if lib == '22' else ''}, ejercicio {num}</b>"
            j = html.find(nombre, html.find('notas:`', a))
            if not a < j < b:
                mal(f'{c}: su resolución no está en las Notas del tema {n}')
    for cod in ORDEN:
        if cod not in EJ:
            mal(f'{cod}: no está resuelto en el verificador')
            continue
        tema, ops, errores, letra = EJ[cod]
        if cod not in en_pagina:
            mal(f'{cod}: no está en la página')
            continue
        pag = en_pagina[cod]
        coincide = lambda a, b: a == b or (len(b) > 40 and a.startswith(b[:40]))
        if len(pag) != len(ops) or not all(coincide(t, e) and ok == eok for (t, ok, _), (e, eok) in zip(pag, ops)):
            mal(f'{cod}: la página dice {[(t, ok) for t, ok, _ in pag]}, tiene que ser {ops}')
        for k in errores:
            if k < len(pag) and not pag[k][2]:
                mal(f'{cod}, opción {"ABCDE"[k]}: sale de un error y la página no lo anota')
        lib, n = cod[1:3], cod.split('-')[1]
        nombre = f"Ejercitario 2.{lib[1]}{' de fijación' if lib == '22' else ''}, ejercicio {n}"
        m = re.search(r'<b>%s</b>(.*?)</p>' % re.escape(nombre), html, flags=re.S)
        if not m or not re.search(r'\b[Ll]a %s\b' % letra, m.group(1)):
            mal(f'{cod}: su resolución en las Notas no dice «la {letra}»')
    for cod in en_pagina:
        if cod not in ORDEN:
            mal(f'{cod}: está en la página y no en la lista del verificador')
    # cada uno dice de dónde sale
    for cod in ORDEN:
        lib, n = cod[1:3], cod.split('-')[1]
        nombre = f"Ejercitario 2.{lib[1]}{' de fijación' if lib == '22' else ''}, ejercicio {n}"
        if nombre not in html:
            mal(f'{cod}: la página no dice de dónde sale («{nombre}»)')

    controla_notacion(html)

    # el desafío
    for frag in ("16 · cos 120°", "' = −8'", "θ = 120°"):
        if frag not in html:
            mal(f'el desafío no trae «{frag}»')

    # los datos de cada enunciado, como en el material
    FUENTE = {
        'E21-1': ['(−1, 3)', '(4, 8)', 'la suma de las componentes'],
        'E21-16': ['(−3, −4)', '−8', '(2, 5)', '(1, 9)', 'opciones verdaderas'],
        'E22-6': ['igual a 15', '(3, −4)'],
        'E21-2': ['(−2, 1)', '(3, −2)', 'no colineales'],
        'E21-3': ['El vector resultante'],
        'E21-4': ['la verdadera es'],
        'E21-12': ['(3, 2)', '(2, −3)', '(4, 6)', '(−10, 2)'],
        'E21-10': ['enteros positivos', 'paralelos'],
        'E21-15': ['la falsa es'],
        'E22-7': ['obtuso o llano', 'no nulo'],
        'E21-8': ['= 4', '= 6', '= 7', 'El coseno'],
        'E21-9': ['= 4', '= 3', 'El producto escalar'],
        'E21-17': ['15', 'x + 2', 'la suma de los módulos'],
        'E21-11': ['(3, 0)', 'suplemento'],
        'E21-19': ['x > 0', 'eje X'],
        'E21-20': ['es el doble', '= 4'],
    }
    for cod, frags in FUENTE.items():
        ini = html.find(f"cod:'{cod}'") if cod != DESAFIO else html.find('const DESAFIO')
        enun = html[ini:html.find('opciones:[' if cod != DESAFIO else 'pasos:[', ini)]
        for f in frags:
            if limpia(f) not in limpia(enun):
                mal(f'{cod}: el enunciado no trae «{f}»')

    # los ejemplos de la teoría: lo que se escribe en la página
    for frag in ["D = (1, 2)", "x + y = 3", "m = 10", "k = 2", "m = 1", "Q('15', '2')", "θ = 45°",
                 "(4, 3)", "(6, −3)", "(−2, 1)", "(2, 0)"]:
        if frag not in html:
            mal(f'la teoría no trae «{frag}»')

    # el diagnóstico
    pag = {}
    for cod, tema, cuerpo in re.findall(r"\{\s*cod:'([IF]\d)',\s*tema:'(\d)',(.*?)opciones:\[(?:.*?)\]\s*\}", html, flags=re.S):
        ini = html.find(f"cod:'{cod}'")
        fin = html.find(']', html.find('opciones:[', ini))
        pag[cod] = (int(tema), lee_opciones(html[html.find('opciones:[', ini):fin + 1]))
    for cod, (tema, ops) in D.items():
        if cod not in pag:
            mal(f'{cod}: no está en la página')
            continue
        t, lista = pag[cod]
        if t != tema:
            mal(f'{cod}: es del tema {tema}, la página dice {t}')
        if [(a, ok) for a, ok, _ in lista] != ops:
            mal(f'{cod}: las opciones de la página no son las calculadas: {[(a, ok) for a, ok, _ in lista]} / {ops}')
        for a, ok, err in lista:
            if not ok and not err:
                mal(f'{cod}: la opción «{a}» no anota de qué error sale')
    if set(pag) != set(D):
        mal(f'el diagnóstico de la página tiene {sorted(pag)}')
    for pre in 'IF':
        letras = [[ok for _, ok in D[f'{pre}{k}'][1]].index(True) for k in range(1, 6)]
        if len(set(letras)) < 4:
            mal(f'el diagnóstico {pre}: la correcta cae casi siempre en la misma letra')

    # lo de siempre
    teorias = re.findall(r"\{\s*id:'([^']+)',\s*cajon:", html)
    if len(re.findall(r"\bpregunta:[`']", html)) < len(teorias):
        mal('hay una teoría sin pregunta')
    transcripto = {t for _, ops, _, _ in EJ.values() for t, _ in ops}
    # lo transcripto del material (enunciados y opciones) va tal cual
    zonas = [(html.find(f"cod:'{c}'"), html.find(']', html.find('opciones:[', html.find(f"cod:'{c}'")))) for c in ORDEN]
    zonas.append((html.find('const DESAFIO'), html.find('pasos:[', html.find('const DESAFIO'))))
    afuera = lambda i: not any(a <= i < b for a, b in zonas)
    cadenas = [m.group(1) for m in re.finditer(r"'([^'\n]*)'", html) if afuera(m.start())]
    cadenas += [re.sub(r'\$\{[^{}]*\}', '', m.group(1)) for m in re.finditer(r'`([^`]*)`', html) if afuera(m.start())]
    for s in cadenas:
        if limpia(s) not in transcripto and len(re.findall(r'\s=\s', s)) > 1:
            mal(f'dos igualdades en un renglón: {s[:90]}')
    if '—' in html:
        mal('la página tiene rayas (—)')
    if re.search(r'P[ée]rez|Duarte|Rol[oó]n|Caballero|Camila', html, flags=re.I):
        mal('la página nombra a otro docente')
    print(f'  {len(en_pagina)} ejercicios en la lista, {len(teorias)} teorías, {len(pag)} ítems de diagnóstico')


datos = ejercicios()
teoria()
D = diagnostico()
controla_pagina(D, datos)
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
