"""Verificación de la clase del cursillo: Divisibilidad, refuerzo y profundización.

`cursillo/clases/divisibilidad-refuerzo.html` es la continuación de
divisibilidad.html: casi todo sale de dos ideas (A: lo que ya es múltiplo se
ignora; B: un número es su tabla de exponentes). Los ejercicios son los del
Ejercitario 3.1, el 3.2 y el Cuestionario de la unidad 4 del material, tal
cual y con sus opciones, más algunos propios. Acá cada uno se resuelve de
nuevo, con enteros, por un camino distinto del de la clase:

1. Cada ejercicio, por fuerza bruta (se recorren las cifras, los números, los
   exponentes): de ahí sale cuál opción es la correcta, y tiene que ser una
   sola. Las opciones de la página son las del material, en ese orden.
2. Cada opción incorrecta que sale de un error se rehace desde ese error.
3. Las demostraciones: cada renglón del cuaderno se evalúa. El de 2.340 con
   números; el de abc, para los 900 números de tres cifras. Los criterios del
   3, el 4 y el 11 de la tabla, contra la división.
4. Se proyectan entre 10 y 12; los de tarea tienen su resolución en las Notas
   con la letra correcta, y ninguno repite uno que ya se proyecta en
   divisibilidad.html.
5. Cada afirmación con números escrita con ∣ o ∤ se rehace dividiendo, y no
   hay barra del teclado.
6. Ningún renglón propio encadena dos igualdades, no hay rayas (—) y no
   aparece el nombre de otro docente.
7. El diagnóstico: cada ítem se resuelve recorriendo y cada opción
   incorrecta se rehace desde su error; los pares I y F miden lo mismo.

    python verificacion/cursillo_divisibilidad_refuerzo.py
"""
import re
import sys
from itertools import product
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = RAIZ / 'cursillo' / 'clases' / 'divisibilidad-refuerzo.html'
PRIMERA = RAIZ / 'cursillo' / 'clases' / 'divisibilidad.html'
fallos = []


def mal(m):
    fallos.append(m)
    print('   FALLA:', m)


EJ = {}        # cod -> (bloque, [(texto, ok)], {k: valor del error}, nombre en las Notas)
TAREA = {}     # cod -> (letras correctas, nombre en las Notas)


def cifras(n):
    return [int(c) for c in str(n)]


def alterna(n):
    """las cifras de lugar impar menos las de lugar par, desde la derecha"""
    c = cifras(n)[::-1]
    return sum(c[0::2]) - sum(c[1::2])


def unica(cod, verdades):
    k = [i for i, v in enumerate(verdades) if v]
    if len(k) != 1:
        mal(f'{cod}: las opciones verdaderas son {k}, tiene que haber una sola')
        return None
    return k[0]


def ejercicio(cod, bloque, textos, correcta, errores=None, nombre=None):
    if correcta is None:
        return
    if len(set(textos)) != len(textos):
        mal(f'{cod}: dos opciones iguales')
    EJ[cod] = (bloque, [(t, i == correcta) for i, t in enumerate(textos)], errores or {}, nombre)
    print(f'  {cod:6s} la {"ABCDE"[correcta]}: {textos[correcta]}')


def valor(expr, **letras):
    """El valor de un renglón del cuaderno: números con punto de miles, +, −,
    ·, paréntesis, y letras (100a es 100 · a). Solo enteros."""
    s = expr.replace('.', '').replace('−', '-').replace('·', '*')
    s = re.sub(r'(\d)([a-z(])', r'\1*\2', s)
    s = re.sub(r'\)([a-z(\d])', r')*\1', s)
    if not re.fullmatch(r'[\d\sa-z+\-*()]*', s):
        raise ValueError(f'no sé leer «{expr}»')
    return eval(s, {'__builtins__': {}}, letras)


# ═══════════════════════ Bloque 2 · por qué funcionan los criterios ═══════════════════════
# Los renglones del cuaderno, tal cual están en la página (sin los N()).
CUADERNO_2340 = ['2.340 = 2 · 1.000 + 3 · 100 + 4 · 10 + 0',
                 ' = 2 · (999 + 1) + 3 · (99 + 1) + 4 · (9 + 1) + 0',
                 ' = 2 · 999 + 2 + 3 · 99 + 3 + 4 · 9 + 4 + 0',
                 ' = (2 · 999 + 3 · 99 + 4 · 9) + (2 + 3 + 4 + 0)',
                 ' = 9 · (2 · 111 + 3 · 11 + 4) + (2 + 3 + 4 + 0)',
                 ' = 9 · 259 + 9']
CUADERNO_ABC = [' = 100a + 10b + c',
                ' = (99 + 1)a + (9 + 1)b + c',
                ' = 99a + a + 9b + b + c',
                ' = (99a + 9b) + (a + b + c)',
                ' = 9 · (11a + b) + (a + b + c)']


def bloque2():
    print('Bloque 2 · por qué funcionan los criterios')
    # la demostración con 2.340: cada renglón vale 2.340
    for r in CUADERNO_2340:
        der = r.split(' = ')[-1]
        if valor(der) != 2340:
            mal(f'el renglón «{r}» no vale 2.340')
    if 2 * 111 + 3 * 11 + 4 != 259 or 9 * 259 + 9 != 2340 or 9 * 260 != 2340 or sum(cifras(2340)) != 9:
        mal('la cuenta final de 2.340 no da')
    # la de abc: cada renglón vale 100a + 10b + c, para los 900 números
    for a, b, c in product(range(1, 10), range(10), range(10)):
        n = 100 * a + 10 * b + c
        for r in CUADERNO_ABC:
            if valor(r.split(' = ')[-1], a=a, b=b, c=c) != n:
                mal(f'el renglón «{r}» no vale {n} con a = {a}, b = {b}, c = {c}')
                return
        # lo que dice la demostración: 9 ∣ n si y solo si 9 ∣ a + b + c, y el mismo resto
        if (n % 9 == 0) != ((a + b + c) % 9 == 0) or n % 9 != (a + b + c) % 9:
            mal(f'el criterio del 9 falla con {n}')
        # la tabla del mismo molde: 3, 4 y 11
        if 99 * a + 9 * b != 3 * (33 * a + 3 * b) or 100 * a != 4 * 25 * a:
            mal('una igualdad de la tabla del molde no vale')
        if n != 11 * (9 * a + b) + (a - b + c):
            mal(f'abc = 11 · (9a + b) + (a − b + c) falla con {n}')
        if n % 3 != (a + b + c) % 3 or n % 4 != (10 * b + c) % 4 or n % 11 != (a - b + c) % 11:
            mal(f'el criterio del 3, del 4 o del 11 falla con {n}')
    # el control con 567 y el ejemplo del mismo resto: 2.341
    if 567 != 9 * 63 or sum(cifras(567)) != 18:
        mal('el control con 567 no da')
    if 2341 % 9 != 1 or sum(cifras(2341)) != 10 or 10 % 9 != 1:
        mal('2.341 y la suma de sus cifras no dejan resto 1')
    # cada potencia de 10 es un múltiplo de 9 más 1 (y de 3), y 100 ya es múltiplo de 4
    if any((10 ** k - 1) % 9 for k in range(1, 12)) or 100 % 4 or 10 % 4 == 0:
        mal('lo que se dice de las potencias de 10 no vale')

    # Ejercitario 3.1, ejercicio 3: tres cifras, múltiplo de 9; al revés,
    # múltiplo de 5; el número de decenas, múltiplo de 8
    def cumple(n, criterio9=True, decenas='total'):
        c = str(n)
        nueve = n % 9 == 0 if criterio9 else n % 3 == 0
        d = n // 10 if decenas == 'total' else int(c[1])
        return nueve and c[0] != '0' and int(c[::-1]) % 5 == 0 and d % 8 == 0
    prod = lambda n: cifras(n)[0] * cifras(n)[1] * cifras(n)[2]
    sol = [n for n in range(100, 1000) if cumple(n)]
    if sol != [567]:
        mal(f'E31-3: los números que cumplen son {sol}')
    # el que usa el criterio del 3: 564 cumple todo con «múltiplo de 3»
    e3 = 564
    if not (cumple(e3, criterio9=False) and e3 % 9):
        mal('E31-3: 564 no sale de usar el criterio del 3')
    # el que toma la cifra de las decenas (y no el número de decenas)
    e_dec = [n for n in range(100, 1000) if cumple(n, decenas='cifra') and prod(n)]
    if e_dec != [585]:
        mal(f'E31-3: con la cifra de las decenas salen {e_dec}')
    textos = ['120', '210', '200', '180', '20']
    ejercicio('E31-3', '2', textos, unica('E31-3', [int(t) == prod(567) for t in textos]),
              {0: prod(e3), 2: prod(585)}, 'Ejercitario 3.1, ejercicio 3')

    # P1 (propio): 3□52 múltiplo de 11; cada distractor sale de un criterio mal usado
    num = lambda a: 3052 + 100 * a
    bien = [a for a in range(10) if num(a) % 11 == 0]
    if bien != [a for a in range(10) if alterna(num(a)) % 11 == 0]:
        mal('P1: el criterio del 11 y la división no dan lo mismo')
    errores = {
        'suma11': next(a for a in range(10) if sum(cifras(num(a))) % 11 == 0),   # sumó todas y pidió 11
        'tres': next(a for a in range(10) if num(a) % 3 == 0),                    # el criterio del 3, la menor
        'seguidas': next(a for a in range(10) if ((2 + 5) - (a + 3)) % 11 == 0),  # agrupó cifras seguidas
        'nueve': next(a for a in range(10) if num(a) % 9 == 0),                   # el criterio del 9
    }
    textos = [str(errores['suma11']), str(errores['tres']), str(errores['seguidas']), str(bien[0]), str(errores['nueve'])]
    if textos != sorted(textos, key=int):
        mal(f'P1: las opciones no quedan en orden: {textos}')
    ejercicio('P1', '2', textos, unica('P1', [num(int(t)) % 11 == 0 for t in textos]),
              {0: errores['suma11'], 1: errores['tres'], 2: errores['seguidas'], 4: errores['nueve']})

    # P2 (propio): abab es siempre divisible por… (los 90 números)
    abab = [int(f'{a}{b}{a}{b}') for a in range(1, 10) for b in range(10)]
    textos = ['11', '101', '1.001', '111', '3']
    ejercicio('P2', '2', textos, unica('P2', [all(n % int(t.replace('.', '')) == 0 for n in abab) for t in textos]))
    if any(int(f'{a}{b}{a}{b}') != 101 * (10 * a + b) for a in range(1, 10) for b in range(10)):
        mal('P2: abab no es 101 · (10a + b)')
    # de dónde sale cada distractor: abcabc es abc · 1.001; aaa es 111 · a;
    # la suma alternada de abab es 2(b − a), que no siempre es 0
    if any(int(str(n) * 2) != n * 1001 for n in range(100, 1000)) or any(int(str(a) * 3) != 111 * a for a in range(1, 10)):
        mal('P2: lo que se dice de abcabc o de aaa no vale')
    if all(alterna(n) % 11 == 0 for n in abab) or all((2 * (n // 1000) + 2 * (n % 10)) % 3 == 0 for n in abab):
        mal('P2: el 11 o el 3 dividen a todos')

    # Ejercitario 3.2, ejercicio 4 (de tarea): 4a327 múltiplo de 9. a = 2 es
    # par y primo: la B y la D son verdaderas las dos
    a = [a for a in range(10) if int(f'4{a}327') % 9 == 0]
    if a != [2]:
        mal(f'E32-4: a puede ser {a}')
    else:
        a = a[0]
        primo = a > 1 and all(a % k for k in range(2, a))
        verdades = [all(n % a == 0 for n in range(1, 50)), a % 2 == 0, a % 3 == 0, primo, 7 % a == 0]
        letras = ''.join('ABCDE'[k] for k, v in enumerate(verdades) if v)
        if letras != 'BD':
            mal(f'E32-4: las verdaderas son {letras}')
        TAREA['E32-4'] = (letras, 'Ejercitario 3.2, ejercicio 4')
        print(f'  E32-4  de tarea: a = {a}, son verdaderas la B y la D (el ejercicio es ambiguo)')


# ═══════════════════════ El diagnóstico ═══════════════════════
def diagnostico():
    """Los ítems propios del diagnóstico, de a pares: I y F miden lo mismo
    con otros números. Devuelve, por código: (bloque, datos, [(texto, ok)])."""
    print('El diagnóstico')
    D = {}

    def item(cod, bloque, datos, opciones):
        textos = [t for t, _ in opciones]
        if len(set(textos)) != 5 or sum(ok for _, ok in opciones) != 1:
            mal(f'{cod}: tiene que tener 5 opciones distintas y una sola correcta')
        D[cod] = (bloque, datos, opciones)
        k = [ok for _, ok in opciones].index(True)
        print(f'  {cod}  la {"ABCDE"[k]}: {textos[k]}')

    # bloque 2: la cifra del □ para que sea múltiplo de 9
    def cifra9(cod, izq, der, olvida, orden):
        num = lambda c: int(f'{izq}{c}{der}')
        conocidas = cifras(izq) + cifras(der)
        bien = [c for c in range(10) if num(c) % 9 == 0]
        if len(bien) != 1:
            mal(f'{cod}: {len(bien)} cifras posibles')
            return
        ops = {'ok': bien[0],
               'tres': next(c for c in range(10) if num(c) % 3 == 0),            # el criterio del 3
               'once': next(c for c in range(10) if alterna(num(c)) % 11 == 0),  # el criterio del 11
               'resto': sum(conocidas) % 9,                                      # puso el resto como cifra
               # se olvidó de sumar una de las cifras conocidas
               'olvido': next(c for c in range(10) if (sum(conocidas) - olvida + c) % 9 == 0)}
        if olvida not in conocidas:
            mal(f'{cod}: el {olvida} no es una de las cifras')
        if sum(cifras(num(bien[0]))) % 9:
            mal(f'{cod}: la suma de las cifras y la división no dan lo mismo')
        item(cod, '2', [f'{izq}□{der}'], [(str(ops[e]), e == 'ok') for e in orden])

    cifra9('I2', 8, 61, 1, ['tres', 'once', 'ok', 'olvido', 'resto'])
    cifra9('F2', 6, 42, 4, ['tres', 'olvido', 'resto', 'ok', 'once'])
    return D


def controla_diagnostico(D, html):
    if not re.search(r'data-diapos="[^"]*\.diagnostico-diapo', html):
        mal('data-diapos no trae .diagnostico-diapo')
    if 'id="diagnostico-lugar"' not in html:
        mal('la página no tiene #diagnostico-lugar')
    fin = html.find('final:{', html.find('const DIAGNOSTICO'))
    pag = {}
    for cod, bloque, enun, ops in re.findall(
            r"\{\s*cod:'([IF]\d)',\s*tema:'(\d)',\s*enun:'([^']*)',\s*opciones:\[(.*?)\]\s*\}", html, flags=re.S):
        lista = re.findall(r"\{\s*t:'([^']*)',\s*(?:(ok:true)|error:'([^']*)')\s*\}", ops)
        pag[cod] = (bloque, enun, lista, html.find(f"cod:'{cod}'"))
    for cod, (bloque, datos, ops) in D.items():
        if cod not in pag:
            mal(f'{cod}: no está en la página')
            continue
        b, enun, lista, pos = pag[cod]
        if b != bloque:
            mal(f'{cod}: es del bloque {bloque}, la página dice {b}')
        if [(a, bool(ok)) for a, ok, _ in lista] != ops:
            mal(f'{cod}: las opciones de la página no son las calculadas: {[(a, bool(ok)) for a, ok, _ in lista]}')
        for a, ok, err in lista:
            if not ok and not err:
                mal(f'{cod}: la opción «{a}» no anota de qué error sale')
        for d in datos:
            if d not in enun:
                mal(f'{cod}: el enunciado no trae «{d}»')
        if (cod[0] == 'I') != (fin < 0 or pos < fin):
            mal(f'{cod}: está en el diagnóstico equivocado')
    for cod in pag:
        if cod not in D:
            mal(f'{cod}: está en la página y no en el verificador')
        par = ('F' if cod[0] == 'I' else 'I') + cod[1]
        if par not in pag:
            mal(f'{cod}: no tiene su par {par}')
    print(f'  {len(pag)} ítems en la página, de a pares')


# ═══════════════════════ La página ═══════════════════════
# los datos de cada ejercicio del material, como están en el material
FUENTE = {
    'E31-3': ['numero de 3 cifras múltiplo de 9', 'se invierte el orden', 'múltiplo de 5',
              'número total de decenas es múltiplo de 8', 'producto de las cifras'],
}
# lo que ya se proyecta en divisibilidad.html, con su número en el material
EN_LA_PRIMERA = {'E31-1': 'E1', 'E31-2': 'E2', 'E31-9': 'E26', 'E32-2': 'E28', 'E32-8': 'E30'}


def divide_bien(html):
    """Cada afirmación con números, n ∣ A o n ∤ A, se rehace dividiendo."""
    n_af = 0
    for n, rel, expr in re.findall(r'(?<![\d.])(\d+) ([∣∤]) (\d[\d.]*(?: [+·−] \d[\d.]*)*)(?![\d.]*[a-z(])', html):
        a = valor(expr)
        if (a % int(n) == 0) != (rel == '∣'):
            mal(f'«{n} {rel} {expr}» es falso: {expr} es {a}')
        n_af += 1
    for arg in re.findall(r"\bM\('([^']*)'\)", html):
        if '|' in arg:
            mal(f'M() con la barra del teclado: {arg}')
        if re.search(r'\S[∣∤]|[∣∤]\S', arg):
            mal(f'∣ o ∤ sin espacios a los lados: {arg}')
    return n_af


def controla_pagina():
    print('La página')
    if not PAGINA.exists():
        mal(f'no existe {PAGINA}')
        return None
    html = PAGINA.read_text(encoding='utf-8')

    # los ejercicios: las opciones, la correcta y los errores
    en_pagina = {}
    for cod, cuerpo, ops in re.findall(r"\{\s*cod:'([A-Z][\w-]*)'(.*?)opciones:\[(.*?)\]\s*\}", html, flags=re.S):
        if re.fullmatch(r'[IF]\d', cod):
            continue
        lista = re.findall(r"\{\s*t:'([^']*)'(?:,\s*(?:(ok:true)|error:'([^']*)'))?\s*\}", ops)
        tras = re.search(r"tras:'([^']+)'", cuerpo)
        en_pagina[cod] = ([(t, bool(ok), err) for t, ok, err in lista], tras.group(1) if tras else None)
    teorias = set(re.findall(r"\{\s*id:'([^']+)',\s*cajon:", html))
    proyectados = [c for c in en_pagina]
    if not 3 <= len(proyectados) <= 12:          # 10 a 12 cuando estén los cinco bloques
        mal(f'se proyectan {len(proyectados)}: en esta clase entran entre 10 y 12')
    for cod, (bloque, ops, errores, nombre) in EJ.items():
        if cod not in en_pagina:
            mal(f'{cod}: no está en la página')
            continue
        pag, tras = en_pagina[cod]
        if [(t, ok) for t, ok, _ in pag] != ops:
            mal(f'{cod}: las opciones de la página son {[(t, ok) for t, ok, _ in pag]}, tienen que ser {ops}')
        for k, v in errores.items():
            if not pag[k][2]:
                mal(f'{cod}, opción {"ABCDE"[k]}: sale de un error, y la página no lo anota')
            if re.sub(r'[^\d]', '', ops[k][0]) != str(v):
                mal(f'{cod}, opción {"ABCDE"[k]}: el error anotado da {v}, no {ops[k][0]}')
        if not tras or tras not in teorias:
            mal(f'{cod}: tiene que ir después de una teoría de la página (tras: {tras})')
        if nombre:
            m = re.search(r'<b>%s</b>\.(.*?)</p>' % re.escape(nombre), html, flags=re.S)
            letra = 'ABCDE'[[ok for _, ok in ops].index(True)]
            if not m or not re.search(r'\b[Ll]a %s\b' % letra, m.group(1)):
                mal(f'{cod}: su resolución en las Notas no dice «la {letra}»')
    for cod in en_pagina:
        if cod not in EJ:
            mal(f'{cod}: está en la página y no en el verificador')
        if cod in EN_LA_PRIMERA:
            mal(f'{cod}: ya se proyecta en divisibilidad.html (es el {EN_LA_PRIMERA[cod]})')
    for cod, (letras, nombre) in TAREA.items():
        if cod in en_pagina:
            mal(f'{cod}: va de tarea y está proyectado')
        m = re.search(r'<b>%s</b> \(de tarea\)\.(.*?)</p>' % re.escape(nombre), html, flags=re.S)
        if not m:
            mal(f'{cod}: va de tarea y su resolución no está en las Notas')
            continue
        for l in letras:
            if not re.search(r'\b[Ll]a %s\b' % l, m.group(1)):
                mal(f'{cod}: la resolución de las Notas no dice «la {l}»')

    # los enunciados del material traen sus datos, tal cual
    for cod, datos in FUENTE.items():
        m = re.search(r"\{\s*cod:'%s'.*?enun:`([^`]*)`" % cod, html, flags=re.S)
        if not m:
            mal(f'{cod}: no encuentro su enunciado')
            continue
        for d in datos:
            if d not in m.group(1):
                mal(f'{cod}: el enunciado no trae «{d}», como el material')

    # las demostraciones: los renglones del cuaderno están tal cual
    limpio = re.sub(r"\$\{N\('([^']*)'\)\}", r'\1', html)
    for r in CUADERNO_2340 + CUADERNO_ABC:
        if f"{r}'" not in limpio and f'{r}`' not in limpio:
            mal(f'el cuaderno no trae el renglón «{r}»')
    for frag in ("M('99a + 9b = 3 · (33a + 3b)')", "M('100a = 4 · 25a')", "M('10 = 11 − 1')",
                 "= 11 · (9a + b) + (a − b + c)", "9 · 260 = 2.340 ✓", "567 = 9 · 63 ✓", "2.341"):
        if frag not in html:
            mal(f'la página no trae «{frag}»')
    # cada paso de una demostración dice qué ley o principio usa
    for ley in ('Valor posicional', 'Disociativa', 'Distributiva.', 'Conmutativa y asociativa',
                'Distributiva, al revés', 'Principio de la suma', 'principio de un sumando'):
        if ley not in html:
            mal(f'las demostraciones no nombran «{ley}»')

    # la notación
    n_af = divide_bien(html)
    if n_af < 4:
        mal(f'solo encontré {n_af} afirmaciones con ∣ o ∤')

    # cada teoría tiene su pregunta
    n_teo, n_preg = len(teorias), len(re.findall(r"\bpregunta:[`']", html))
    if n_preg < n_teo:
        mal(f'hay {n_teo} teorías y solo {n_preg} preguntas')

    # ningún renglón propio encadena dos igualdades; sin rayas; sin otros docentes
    transcripto = {t for _, ops, _, _ in EJ.values() for t, _ in ops}
    cadenas = re.findall(r"'([^'\n]*)'", html)
    cadenas += [re.sub(r'\$\{[^{}]*\}', '', s) for s in re.findall(r'`([^`]*)`', html)]
    for s in cadenas:
        if s not in transcripto and len(re.findall(r'\s=\s', s)) > 1:
            mal(f'dos igualdades en un renglón: {s[:90]}')
    if '—' in html:
        mal('la página tiene rayas (—)')
    if re.search(r'Duarte|Rol[oó]n|Caballero|Camila', html, flags=re.I):
        mal('la página nombra a otro docente')

    # ninguno de los que se proyectan acá se proyecta en la primera clase
    primera = PRIMERA.read_text(encoding='utf-8')
    for cod, otro in EN_LA_PRIMERA.items():
        if f"cod:'{otro}'" not in primera:
            mal(f'divisibilidad.html ya no proyecta el {otro}: revisar EN_LA_PRIMERA')
    print(f'  {len(proyectados)} ejercicios proyectados, {len(TAREA)} de tarea, {n_teo} teorías, '
          f'{n_af} afirmaciones con ∣ o ∤')
    return html


bloque2()
D = diagnostico()
html = controla_pagina()
if html:
    controla_diagnostico(D, html)
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
