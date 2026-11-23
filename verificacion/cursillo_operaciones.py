"""Verificación de la clase del cursillo: Operaciones fundamentales.

Los ejercicios de `cursillo/clases/operaciones.html` son los del ejercitario
del cursillo, transcriptos tal cual con sus opciones. Acá cada uno se
resuelve de nuevo, con enteros y Fraction (nada de float):

1. Los de afirmaciones (leyes, propiedades, «la falsa es»): cada afirmación
   se prueba por fuerza bruta sobre muchos números, y de ahí sale qué
   opción es la correcta. No se escribe a mano cuál es.
2. Los numéricos: por fuerza bruta (se recorren los dividendos, divisores,
   minuendos posibles hasta encontrar los que cumplen el enunciado) y por
   otro camino, despejando. Los dos tienen que dar lo mismo, y la solución
   tiene que ser única.
3. Las opciones de la página son las del material, en ese orden; la que
   está marcada ok:true es la que salió de 1 o 2; y la que lleva un error
   anotado, si el error es una cuenta, se recalcula desde ese error.
4. El enunciado de la página trae los datos del material.
5. Cada ejercicio con tras: va después de una teoría que existe en la página.
6. El desafío (el ejercicio 39 resuelto en la pizarra): la respuesta, por
   fuerza bruta, escrita tal cual en la página.
7. Ningún renglón propio encadena dos igualdades, y no hay rayas (—).

    python verificacion/cursillo_operaciones.py
"""
import re
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = RAIZ / 'cursillo' / 'clases' / 'operaciones.html'
fallos = []


def mal(m):
    fallos.append(m)
    print('   FALLA:', m)


NAT = range(0, 13)                                   # naturales chicos, con el 0
POS = [F(k, 4) for k in range(1, 25)]                # racionales positivos: 1/4 … 6
EJ = {}                                              # cod -> (tema, [(texto, ok)], {k: valor del error})


def siempre(pred, muestras):
    return all(pred(*m) for m in muestras)


def unica(cod, verdades):
    """verdades: una lista de bool, una por opción. Devuelve la única verdadera."""
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


def miles(n):
    """3216 -> '3.216', como se escribe en la clase."""
    return f'{n:,}'.replace(',', '.')


def cifras(n):
    return [int(c) for c in str(n)]


# ── división entera: por defecto y por exceso ──
def defecto(D, d):
    return D // d, D % d


def exceso(D, d):
    c, r = defecto(D, d)
    return c + 1, d - r                # solo tiene sentido si la división es inexacta


def adicion():
    print('Tema 1 · adición')
    # E1: las propiedades de la adición
    I = siempre(lambda m, n, p: (m + n) + p == m + (n + p), product(NAT, NAT, NAT))
    II = siempre(lambda m, n: m + n == n + m, product(NAT, NAT))
    III = siempre(lambda n: n + 0 == 0 + n == 0, [(n,) for n in NAT])
    IV = siempre(lambda m, n, p: m + p != n + p or m == n, product(NAT, NAT, NAT))
    V = siempre(lambda m, n, p: m != n or m + p == n + p, product(NAT, NAT, NAT))
    ver = {'I': I, 'II': II, 'III': III, 'IV': IV, 'V': V}
    ops = [['I', 'II', 'IV'], ['I', 'III', 'IV', 'V'], ['I', 'II', 'III', 'V'],
           ['I', 'II', 'IV', 'V'], ['II', 'III', 'IV', 'V']]
    ejercicio('E1', '1', ['I, II y IV', 'I, III, IV y V', 'I, II, III y V', 'I, II, IV y V', 'II, III, IV y V'],
              unica('E1', [set(o) == {k for k, v in ver.items() if v} for o in ops]))

    # E6: un sumando aumenta k y otro disminuye k
    mu = [(a, b, k) for a, b, k in product(range(1, 15), range(1, 15), range(1, 6)) if b >= k]
    nueva = lambda a, b, k: (a + k) + (b - k)
    ejercicio('E6', '1', ['queda dividida por el mismo número.', 'aumenta el mismo número.',
                          'disminuye el mismo número.', 'queda multiplicada por el mismo número.', 'no varía.'],
              unica('E6', [siempre(lambda a, b, k: F(nueva(a, b, k)) == F(a + b, k), mu),
                           siempre(lambda a, b, k: nueva(a, b, k) == a + b + k, mu),
                           siempre(lambda a, b, k: nueva(a, b, k) == a + b - k, mu),
                           siempre(lambda a, b, k: nueva(a, b, k) == (a + b) * k, mu),
                           siempre(lambda a, b, k: nueva(a, b, k) == a + b, mu)]))

    # E7: la falsa
    A = siempre(lambda a, b, k: (a + k) + b == a + b + k and (a - k) + b == a + b - k, mu)
    B = siempre(lambda a, b, k: nueva(a, b, k) != a + b, mu)
    C = siempre(lambda a, b, c, d: not (a < b and c == d) or a + c < b + d, product(NAT, NAT, NAT, NAT))
    D = siempre(lambda a, b, x: x > a or a + b == (x + (a - x)) + b, product(NAT, NAT, NAT))
    E = siempre(lambda a, b, c: a + b + c == (a + b) + c, product(NAT, NAT, NAT))
    ejercicio('E7', '1', [
        'Si un sumando aumenta o disminuye un número cualquiera, la suma aumenta o disminuye el mismo número.',
        'Si un sumando aumenta un número cualquiera y otro sumando disminuye el mismo número, la suma varía.',
        'Sumando miembro a miembro desigualdades del mismo sentido con igualdades resulta una desigualdad del mismo sentido que las dadas.',
        'La suma de varios números no se altera descomponiendo uno o varios sumandos en dos o más sumandos.',
        'La suma de varios números no varía sustituyendo varios sumandos por su suma.'],
        unica('E7', [not v for v in (A, B, C, D, E)]))


def sustraccion():
    print('Tema 2 · sustracción')
    mu = [(M, S) for M, S in product(range(0, 40), repeat=2) if S <= M]
    # E10: M + S + D
    ejercicio('E10', '2', ['cero', 'uno', 'el doble de la diferencia', 'el doble del minuendo', 'el doble del sustraendo'],
              unica('E10', [siempre(lambda M, S, f=f: M + S + (M - S) == f(M, S), mu) for f in (
                  lambda M, S: 0, lambda M, S: 1, lambda M, S: 2 * (M - S), lambda M, S: 2 * M, lambda M, S: 2 * S)]))

    # E8: +14 al minuendo, +24 al sustraendo
    cambio = {(M + 14) - (S + 24) - (M - S) for M, S in mu}
    if len(cambio) != 1:
        mal('E8: la diferencia no varía siempre lo mismo')
    v = cambio.pop()
    ejercicio('E8', '2', ['Aumenta en 14', 'Disminuye en 24', 'Aumenta en 10', 'Disminuye en 10', 'No varía'],
              unica('E8', [v == 14, v == -24, v == 10, v == -10, v == 0]))

    # E4: (M − D) − S
    res = lambda M, S: (M - (M - S)) - S
    verdades = [siempre(lambda M, S, f=f: res(M, S) == f(M, S), mu) for f in (
        lambda M, S: M, lambda M, S: S, lambda M, S: 1, lambda M, S: 2 * M)]
    ejercicio('E4', '2', ['M', 'S', '1', '2M', 'NDA'], unica('E4', verdades + [not any(verdades)]))

    # E11: M + S + D = 142 y M + S es la unidad del tercer orden (la centena)
    tercer = 10 ** (3 - 1)                                  # unidades, decenas, centenas
    sol = [M - S for M, S in product(range(200), repeat=2) if S <= M and M + S + (M - S) == 142 and M + S == tercer]
    despejo = 142 - tercer                                  # S + D es M: M + S + D es 2M; D es 142 − (M + S)
    if sol != [despejo]:
        mal(f'E11: fuerza bruta {sol}, despejando {despejo}')
    ops = [55, 17, 45, 42, 83]
    ejercicio('E11', '2', [str(x) for x in ops], unica('E11', [x == despejo for x in ops]))

    # E13: M + S + D = 50 S y D = 960
    sol = [(M, S) for S in range(1, 2000) for M in [S + 960] if M + S + (M - S) == 50 * S]
    if len(sol) != 1:
        mal(f'E13: soluciones {sol}')
    M, S = sol[0]
    if (2 * M != 50 * S) or (M != 25 * S) or (24 * S != 960):   # el otro camino: 2M = 50S, M = 25S, 24S = 960
        mal('E13: despejando no da')
    ops = [1000, 1, 40, 4, 1040]
    ejercicio('E13', '2', [str(x) for x in ops], unica('E13', [x == sum(cifras(M)) for x in ops]),
              {0: M, 2: S, 3: sum(cifras(S)), 4: M + S})


def multiplicacion():
    print('Tema 3 · multiplicación')
    # E15: a · b = p, con a positivo; ¿cuál no se verifica?
    mu = list(product(POS, POS + [F(0)]))
    verif = [siempre(lambda a, b: b != 1 or a * b == a, mu),
             siempre(lambda a, b: not b > 1 or a * b > a, mu),
             siempre(lambda a, b: not b < 1 or a * b == 0, mu),
             siempre(lambda a, b: b != 0 or a * b == 0, mu),
             siempre(lambda a, b: b != a or a * b == a ** 2, mu)]
    ejercicio('E15', '3', ['Si b = 1, entonces p = a.', 'Si b > 1, entonces p > a.', 'Si b < 1, entonces p = 0.',
                           'Si b = 0, entonces p = 0.', 'Si b = a, entonces p = a².'],
              unica('E15', [not v for v in verif]))

    # E16: ¿en qué operaciones se cumple la conmutativa?
    mu = list(product(POS, POS))
    conm = {'suma': siempre(lambda a, b: a + b == b + a, mu), 'resta': siempre(lambda a, b: a - b == b - a, mu),
            'multiplicación': siempre(lambda a, b: a * b == b * a, mu), 'división': siempre(lambda a, b: a / b == b / a, mu)}
    conm['adición'] = conm['suma']
    pares = [('suma', 'resta'), ('suma', 'multiplicación'), ('multiplicación', 'división'),
             ('resta', 'división'), ('adición', 'división')]
    ejercicio('E16', '3', [f'{a} y {b}' for a, b in pares], unica('E16', [conm[a] and conm[b] for a, b in pares]))

    # E27: (a − 4) · b = p − 640 y a · (b + 4) = p + 120
    sol = [(a, b) for a in range(5, 400) for b in range(1, 400)
           if (a - 4) * b == a * b - 640 and a * (b + 4) == a * b + 120]
    a, b = 120 // 4, 640 // 4                               # despejando: 4b = 640, 4a = 120
    if sol != [(a, b)]:
        mal(f'E27: fuerza bruta {sol}, despejando {(a, b)}')
    ops = [30, 160, 480, 4800, 300]
    ejercicio('E27', '3', [str(x) for x in ops], unica('E27', [x == a * b for x in ops]), {0: a, 1: b})


def division():
    print('Tema 4 · división')
    mu = [(D, d) for D in range(0, 120) for d in range(1, 25)]
    exacta = lambda D, d: D % d == 0
    # E18: la división es exacta cuando… (la condición tiene que equivaler a ser exacta)
    conds = [lambda D, d: any(d * k == D for k in range(0, D + 1)),      # el dividendo es múltiplo del divisor
             lambda D, d: d == 1, lambda D, d: (D // d) % 2 == 0, lambda D, d: D % d == 1, lambda D, d: d % 2 == 1]
    ejercicio('E18', '4', ['el dividendo es múltiplo del divisor.', 'el divisor es 1.', 'el cociente es par.',
                           'el resto es igual a la unidad.', 'el divisor es impar.'],
              unica('E18', [siempre(lambda D, d, f=f: f(D, d) == exacta(D, d), mu) for f in conds]))

    # E24: x : 23 exacta, y el cociente es la mitad del cuádruplo del divisor
    d = 2 * 10 + 3
    sol = [x for x in range(1, 5000) if x % d == 0 and 2 * (x // d) == 4 * d]
    if sol != [d * (4 * d // 2)]:
        mal(f'E24: {sol}')
    x = sol[0]
    textos = ['1,500', '1,800', '1,058', '2,116', '1,580']   # el material escribe los miles con coma
    valor = lambda t: int(t.replace(',', ''))
    ejercicio('E24', '4', textos, unica('E24', [valor(t) == x for t in textos]), {3: d * 4 * d})

    # E31: cociente 19, resto 26, y D + d + c + r = 1011
    sol = [(19 * d + 26, d) for d in range(27, 2000) if (19 * d + 26) + d + 19 + 26 == 1011]
    d = (1011 - 19 - 26 - 26) // 20                         # despejando: 20d + 71 = 1011
    if sol != [(19 * d + 26, d)] or defecto(19 * d + 26, d) != (19, 26):
        mal(f'E31: {sol}')
    ops = [825, 872, 919, 966, 1013]
    ejercicio('E31', '4', [str(o) for o in ops], unica('E31', [o == sol[0][0] for o in ops]))

    # E33: c 17, r 9; al dividendo + 49, c 21 y r 6
    sol = [(D, d) for d in range(2, 500) for D in [17 * d + 9]
           if defecto(D, d) == (17, 9) and defecto(D + 49, d) == (21, 6)]
    d = (49 + 9 - 6) // (21 - 17)                           # despejando: 17d + 9 + 49 = 21d + 6
    if sol != [(17 * d + 9, d)]:
        mal(f'E33: {sol}')
    ops = [238, 240, 244, 241, 243]
    ejercicio('E33', '4', [str(o) for o in ops], unica('E33', [o == sum(sol[0]) for o in ops]))

    # E22: ¿cuántas falsas? (en divisiones inexactas)
    ine = [(D, d) for D, d in mu if D % d and d > 1]
    af = [siempre(lambda D, d: d < defecto(D, d)[1], ine),
          siempre(lambda D, d: defecto(D, d)[1] + exceso(D, d)[1] == defecto(D, d)[0], ine),
          siempre(lambda D, d: all(defecto(D, d)[1] % k == 0 for k in range(1, d + 1) if D % k == 0 and d % k == 0), ine),
          siempre(lambda D, d: defecto(D, d)[0] != 1 or D == d, ine)]
    falsas = af.count(False)
    ejercicio('E22', '4', ['Una', 'Dos', 'Tres', 'Todas', 'Ninguna'],
              unica('E22', [falsas == 1, falsas == 2, falsas == 3, falsas == 4, falsas == 0]))

    # E25: por defecto suman 41, por exceso 39, los cocientes suman 7
    sol = []
    for d in range(2, 60):
        for D in range(d + 1, 60):
            if D % d == 0:
                continue
            c, r = defecto(D, d)
            c2, r2 = exceso(D, d)
            if D + d + c + r == 41 and D + d + c2 + r2 == 39 and c + c2 == 7:
                sol.append(d)
    # despejando: c = 3, c′ = 4; r′ es r − 3 y r + r′ es d, así que d = 2r − 3; 3d + r + d + 3 + r = 41
    r = next(r for r in range(1, 30) if 4 * (2 * r - 3) + 2 * r + 3 == 41)
    if sol != [2 * r - 3]:
        mal(f'E25: fuerza bruta {sol}, despejando {2 * r - 3}')
    ops = [26, 5, 7, 2, 4]
    ejercicio('E25', '4', [str(o) for o in ops], unica('E25', [o == sol[0] for o in ops]))

    # E23: al resto le faltan 13 para el máximo; D − 131 da cociente 6 menos y resto máximo
    sol = sorted({d for d in range(15, 400) for q in range(6, 60)
                  for D in [d * q + (d - 1 - 13)] if defecto(D - 131, d) == (q - 6, d - 1)})
    d = (145 - 1) // 6                                       # despejando: d − 14 − 131 = −6d + d − 1
    if sol != [d]:
        mal(f'E23: fuerza bruta {sol}, despejando {d}')
    ops = [8, 6, 12, 13, 16]
    p = 1
    for k in cifras(d):
        p *= k
    ejercicio('E23', '4', [str(o) for o in ops], unica('E23', [o == sum(cifras(d)) for o in ops]), {0: p})

    # E34: divisor 23, resto 4: lo más que se puede sumar para que el cociente aumente 3
    d, r = 23, 4
    mas = set()
    for q in range(0, 40):
        D = d * q + r
        mas.add(max(k for k in range(0, 200) if (D + k) // d == q + 3))
    if mas != {3 * d + (d - 1) - r}:
        mal(f'E34: {mas}')
    k = mas.pop()
    ops = [65, 42, 66, 88, 87]
    ejercicio('E34', '4', [str(o) for o in ops], unica('E34', [o == k for o in ops]),
              {0: 3 * d - r, 3: 3 * d + d - r})


def combinadas():
    print('Tema 5 · operaciones combinadas')
    # E30, de adentro hacia afuera
    a = 65 - 56
    b = -24 - 73
    c = 44 - b - 36
    v = 7 - (-a - c - 30) + 103
    if v != eval('7 - (-(65 - 56) - (44 - (-24 - 73) - 36) - 30) + 103'):
        mal('E30: por pasos no da lo mismo que de una')
    primo = v > 1 and all(v % k for k in range(2, int(v ** .5) + 1))
    ejercicio('E30', '5', ['Un número par', 'Una cifra no significativa', 'El módulo de la multiplicación',
                           'Un número negativo', 'Un número primo'],
              unica('E30', [v % 2 == 0, v == 0, v == 1, v < 0, primo]))
    return v


def desafio():
    """E39: dividido entre 150, r = 3c′ y r′ = 4c."""
    sol = []
    for D in range(151, 30000):
        c, r = defecto(D, 150)
        if r == 0:
            continue
        c2, r2 = exceso(D, 150)
        if r == 3 * c2 and r2 == 4 * c:
            sol.append(D)
    c = (150 - 3) // 7                                       # despejando: 3(c + 1) + 4c = 150
    if sol != [150 * c + 3 * (c + 1)]:
        mal(f'E39: fuerza bruta {sol}, despejando {150 * c + 3 * (c + 1)}')
    return sol[0], c


# los datos de cada ejercicio, como están en el material
FUENTE = {
    'E1': ['(m + n) + p = m + (n + p)', 'n + 0 = 0 + n = 0', 'Si m + p = n + p, entonces m = n'],
    'E4': ['Si del minuendo (M) se resta la diferencia (D)', 'se disminuye el sustraendo'],
    'E8': ['se suma 14 al minuendo y 24 al sustraendo'],
    'E11': ['es 142', 'unidad del tercer orden'],
    'E13': ['50 veces el sustraendo', 'la diferencia es 960', 'suma de las cifras del minuendo'],
    'E15': ['a · b = p', 'no se verifica'],
    'E24': ['dos decenas y tres unidades', 'la mitad del'],
    'E25': ['se obtiene 41', 'la suma es 39', 'la suma de los cocientes es 7'],
    'E23': ['le falta 13 unidades', 'restarle 131 unidades', 'disminuye en 6'],
    'E27': ['disminuye en 4 unidades', 'disminuye en 640', 'aumenta 4 unidades', 'aumenta en 120'],
    'E31': ['es 19 y el resto, 26', 'es 1011'],
    'E33': ['son 17 y 9', 'aumenta 49 unidades', 'sería 21 y el resto 6'],
    'E34': ['el divisor es 23 y el resto 4', 'el cociente aumente en 3'],
    'E30': ['7 − [−(65 − 56) − [44 − (−24 − 73) − 36] − 30] + 103'],
}
# lo que se transcribe tal cual aunque tenga dos «=»: es una afirmación falsa del material
TAL_CUAL = ['n + 0 = 0 + n = 0', 'Si m + p = n + p, entonces m = n', 'Si m = n, entonces m + p = n + p']


def controla_pagina(v30, d39, c39):
    print('La página')
    if not PAGINA.exists():
        mal(f'no existe {PAGINA}')
        return
    html = PAGINA.read_text(encoding='utf-8')

    # los ejercicios: opciones, la correcta, los errores que son cuentas
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
            if ops[k][0].replace(',', '').replace('.', '') != str(valor):
                mal(f'{cod}, opción {"ABCDE"[k]}: el error anotado da {valor}, no {ops[k][0]}')
        if tras and tras not in teorias:
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

    # cada teoría tiene su pregunta
    n_teo = len(teorias)
    n_preg = len(re.findall(r"\bpregunta:[`']", html))
    if n_preg < n_teo:
        mal(f'hay {n_teo} teorías y solo {n_preg} preguntas')

    # el desafío
    if f'final:\'el número es {miles(d39)}\'' not in html:
        mal(f'el desafío no termina en {miles(d39)}')
    for frag in (f"'c = {c39}'", f"'r′ = 4 · {c39}'", f"' = {miles(d39)}'"):
        if frag not in html:
            mal(f'el desafío no trae {frag}')
    if f'{v30}' not in html:
        mal(f'las notas no dicen cuánto da el ejercicio 30 ({v30})')

    # renglones propios: ninguno con dos igualdades (las opciones del material van tal cual)
    transcripto = {t for _, ops, _ in EJ.values() for t, _ in ops}
    cadenas = re.findall(r"'([^'\n]*)'", html)
    cadenas += [re.sub(r'\$\{[^{}]*\}', '', s) for s in re.findall(r'`([^`]*)`', html)]
    for s in cadenas:
        if s in transcripto:
            continue
        limpio = s
        for t in TAL_CUAL:
            limpio = limpio.replace(t, '')
        if len(re.findall(r'\s=\s', limpio)) > 1:
            mal(f'dos igualdades en un renglón: {s[:90]}')
    if '—' in html:
        mal('la página tiene rayas (—)')
    if re.search(r'Caballero|Camila', html):
        mal('la página nombra a otra docente')
    print(f'  {len(EJ)} ejercicios, {sum(len(o) for _, o, _ in EJ.values())} opciones controladas; {n_teo} teorías')


adicion()
sustraccion()
multiplicacion()
division()
v30 = combinadas()
d39, c39 = desafio()
print(f'  E39  el número es {miles(d39)} (cociente por defecto {c39})')
controla_pagina(v30, d39, c39)
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
