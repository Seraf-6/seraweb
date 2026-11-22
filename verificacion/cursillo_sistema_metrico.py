"""Verificación de la clase del cursillo: Sistema métrico decimal.

Cada respuesta de `cursillo/clases/sistema-metrico.html` se calcula acá con
Fraction (nada de float) y por DOS caminos que no se tocan:

1. Por la tabla de equivalencias: cuánto vale cada unidad en la unidad
   principal (1 km = 1000 m, 1 ha = 10 000 m², 1 Tm = 1 000 000 g…),
   escrita a mano, número por número.
2. Por la escalera: la posición de cada unidad en su escalera
   (km hm dam m dm cm mm) y el salto por escalón (10, 100 o 1000 según la
   dimensión). La Tm, el Qm y las unidades agrarias no están en la escalera:
   se ubican por su equivalencia con un escalón (ha = hm², a = dam², ca = m²).

La clase convierte con factores unitarios: `convierte('3,75 km',
['1.000 m', '1 km'], '3.750 m')`. Cada llamada de la página se lee y se
controla: que cada factor valga 1 (por los dos caminos), que la cuenta de
los números dé, que las unidades que se tachan se cancelen y quede la del
resultado, y que la medida de la izquierda sea la de la derecha.

Después:
3. Los problemas se vuelven a hacer desde el enunciado, con otro orden de
   cuentas (el control que dice la página).
4. La página tiene escrita tal cual cada respuesta final, también las de
   la práctica.
5. Dentro de un tema no se repite una respuesta (la práctica cuenta).
6. Ningún renglón encadena dos igualdades.
7. Todo ejemplo tiene su control; toda práctica, tres ejercicios.

    python verificacion/cursillo_sistema_metrico.py
"""
import ast
import re
import sys
from fractions import Fraction as F
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = RAIZ / 'cursillo' / 'clases' / 'sistema-metrico.html'
fallos = []


def mal(m):
    fallos.append(m)
    print('   FALLA:', m)


# ── camino 1: la tabla, en la unidad principal ──
TABLA = {
    # longitud, en m
    'mam': F(10000), 'km': F(1000), 'hm': F(100), 'dam': F(10), 'm': F(1),
    'dm': F(1, 10), 'cm': F(1, 100), 'mm': F(1, 1000),
    # capacidad, en l
    'kl': F(1000), 'hl': F(100), 'dal': F(10), 'l': F(1), 'dl': F(1, 10), 'cl': F(1, 100), 'ml': F(1, 1000),
    # masa, en g
    'Tm': F(1000000), 'Qm': F(100000), 'mag': F(10000), 'kg': F(1000), 'hg': F(100), 'dag': F(10),
    'g': F(1), 'dg': F(1, 10), 'cg': F(1, 100), 'mg': F(1, 1000),
    # superficie, en m²
    'km2': F(1000000), 'hm2': F(10000), 'dam2': F(100), 'm2': F(1), 'dm2': F(1, 100),
    'cm2': F(1, 10000), 'mm2': F(1, 1000000), 'ha': F(10000), 'a': F(100), 'ca': F(1),
    # volumen, en m³; el litro es el dm³
    'km3': F(10) ** 9, 'hm3': F(10) ** 6, 'dam3': F(1000), 'm3': F(1), 'dm3': F(1, 1000),
    'cm3': F(1, 10) ** 6, 'mm3': F(1, 10) ** 9,
}
MAGNITUD = {**{u: 'L' for u in ('mam', 'km', 'hm', 'dam', 'm', 'dm', 'cm', 'mm')},
            **{u: 'C' for u in ('kl', 'hl', 'dal', 'l', 'dl', 'cl', 'ml')},
            **{u: 'M' for u in ('Tm', 'Qm', 'mag', 'kg', 'hg', 'dag', 'g', 'dg', 'cg', 'mg')},
            **{u: 'S' for u in ('km2', 'hm2', 'dam2', 'm2', 'dm2', 'cm2', 'mm2', 'ha', 'a', 'ca')},
            **{u: 'V' for u in ('km3', 'hm3', 'dam3', 'm3', 'dm3', 'cm3', 'mm3')}}


def por_tabla(cant, de, a):
    """Convierte con la tabla. El agua: 1 dm³ = 1 l = 1 kg."""
    md, ma = MAGNITUD[de], MAGNITUD[a]
    if md == ma:
        return cant * TABLA[de] / TABLA[a]
    # pasar por el litro (capacidad), que es el puente entre las tres
    en_l = {'C': lambda q, u: q * TABLA[u],
            'V': lambda q, u: q * TABLA[u] * 1000,            # 1 m³ = 1000 l
            'M': lambda q, u: q * TABLA[u] / 1000}[md](cant, de)   # 1 kg de agua = 1 l
    return {'C': lambda q: q / TABLA[a],
            'V': lambda q: q / 1000 / TABLA[a],
            'M': lambda q: q * 1000 / TABLA[a]}[ma](en_l)


# ── camino 2: la escalera ──
ESCALERA = ['k', 'h', 'da', '', 'd', 'c', 'm']        # de arriba hacia abajo
SALTO = {'L': 10, 'C': 10, 'M': 10, 'S': 100, 'V': 1000}
FUERA = {'mam': ('km', 1, 'L'), 'Tm': ('kg', 3, 'M'), 'Qm': ('kg', 2, 'M'), 'mag': ('kg', 1, 'M'),
         'ha': ('hm2', 0, 'S'), 'a': ('dam2', 0, 'S'), 'ca': ('m2', 0, 'S')}


def escalon(u):
    """(magnitud, posición) en su escalera; más alto = número más chico."""
    if u in FUERA:                      # mam = 10 km, Tm = 10³ kg, ha = hm²…
        ref, sube, _ = FUERA[u]
        m, p = escalon(ref)
        return m, p - sube
    if u[-1] in '23':                   # km2, dam2, m3: el prefijo va antes de «m»
        return ('S' if u[-1] == '2' else 'V'), ESCALERA.index(u[:-2])
    for mag, base in (('C', 'l'), ('M', 'g'), ('L', 'm')):
        if u.endswith(base) and u[:-1] in ESCALERA:
            return mag, ESCALERA.index(u[:-1])
    raise ValueError(u)


def por_escalera(cant, de, a):
    md, pd = escalon(de)
    ma, pa = escalon(a)
    if md == ma:
        return cant * F(SALTO[md]) ** (pa - pd)
    # el puente del agua: 1 dm³ = 1 l = 1 kg; se lleva todo a esos tres
    objetivo = {'V': ESCALERA.index('d'), 'C': ESCALERA.index(''), 'M': ESCALERA.index('k')}
    al_puente = cant * F(SALTO[md]) ** (objetivo[md] - pd)
    return al_puente * F(SALTO[ma]) ** (pa - objetivo[ma])


def conv(cant, de, a):
    """Las dos cuentas tienen que coincidir."""
    x, y = por_tabla(cant, de, a), por_escalera(cant, de, a)
    if x != y:
        mal(f'{cant} {de} → {a}: la tabla da {x} y la escalera {y}')
    return x


def suma(partes, a):
    return sum((conv(F(c), u, a) for c, u in partes), F(0))


def num(s):
    """'3,75', '1.257,3' o '3/4' → Fraction."""
    if '/' in s:
        n, d = s.split('/')
        return F(int(n), int(d))
    return F(s.replace('.', '').replace(',', '.'))


def fmt(q):
    """Fraction → '3.750', '42,6', '3.040,5': como se escribe en Paraguay."""
    q = F(q)
    ent, resto = divmod(q, 1)
    dec = ''
    if resto:
        for k in range(1, 12):
            if (resto * 10 ** k).denominator == 1:
                dec = ',' + str(int(resto * 10 ** k)).rjust(k, '0')
                break
        else:
            raise ValueError(f'{q} no es decimal finito')
    s = f'{int(ent):,}'.replace(',', '.')
    return s + dec


def unidad(u):
    """Como se escribe en la página (kL, m², dm³) → la clave de la TABLA."""
    u = u.replace('²', '2').replace('³', '3')
    if u.endswith('L'):
        u = u[:-1] + 'l'
    return u


def medida(s):
    """'3,75 km' → (Fraction, 'km')."""
    s = s.replace('✓', '').strip()
    n, u = s.split(' ', 1)
    return num(n), unidad(u.strip())


# ── las respuestas de la página ──
FINALES = {}          # tema → [respuesta escrita en la página]


def cuenta(tema, valor, texto):
    """`texto` es la respuesta de la página; el número que trae tiene que ser `valor`."""
    FINALES.setdefault(tema, []).append(texto)
    print(f'  {tema:8s} {texto}')
    return valor


def c(tema, cant, de, a, txt_de=None, txt_a=None):
    """Una conversión con su respuesta escrita «3,75 km = 3.750 m»."""
    v = conv(num(cant), unidad(de), unidad(a))
    cuenta(tema, v, f'{txt_de or cant + " " + de} = {fmt(v)} {txt_a or a}')
    return v


def main():
    print('Para arrancar')
    pasos = conv(num('1,8'), 'km', 'm') / conv(F(60), 'cm', 'm')
    cuenta('arranque', pasos, f'son {fmt(pasos)} pasos')
    if conv(pasos * 60, 'cm', 'km') != num('1,8'):
        mal('el control del arranque')

    print('Tema 1 · longitud (lectura, ejemplo 1; ejercitario 5.2, ej. 3)')
    c('1', '0,64', 'km', 'm')
    v = conv(F(3, 4), 'hm', 'm');  cuenta('1', v, '${Q(3, 4)} hm = ' + f'{fmt(v)} m')
    c('1', '18,5', 'cm', 'm')
    lat = suma([(F(1, 5), 'dm'), (num('16,5'), 'cm'), (35, 'mm')], 'm')
    cuenta('1', lat, '${Q(1, 5)} dm 16,5 cm 35 mm = ' + f'{fmt(lat)} m')
    frente = suma([(num('0,64'), 'km'), (F(3, 4), 'hm'), (25, 'm')], 'm')
    lateral = 1000 * lat
    alambre = 4 * (frente + 2 * lateral)
    cuenta('1', alambre, f'hacen falta {fmt(alambre)} m de alambre')
    # control: un hilo es el frente y los dos laterales, sin el fondo
    if alambre / 4 != conv(F(740), 'm', 'm') + 2 * conv(F(22), 'dam', 'm'):
        mal('el control del alambrado')
    print('  práctica')
    v = conv(num('2,35'), 'km', 'm');  cuenta('1', v, f'{fmt(v)} m')
    v = conv(F(870), 'mm', 'm');       cuenta('1', v, f'{fmt(v)} m')
    perim = 2 * (conv(num('0,12'), 'km', 'm') + suma([(8, 'dam'), (5, 'm')], 'm'))
    cuenta('1', 3 * perim, f'{fmt(3 * perim)} m')

    print('Tema 2 · capacidad y masa (ejercitario 5.2, ej. 4 y 9; lectura, ejemplo 2)')
    c('2', '7', 'hL', 'L')
    c('2', '350', 'L', 'daL')
    c('2', '700', 'hg', 'kg')
    cosecha = suma([(4, 'Tm'), (30, 'kg'), (6000, 'g')], 'kg')
    cuenta('2', cosecha, f'4 Tm 30 kg 6.000 g = {fmt(cosecha)} kg')
    bolsa = suma([(700, 'hg'), (500, 'dag')], 'kg')
    quedan = cosecha - 50 * bolsa
    cuenta('2', quedan, f'quedaron {fmt(quedan)} kg')
    if suma([(50 * 700, 'hg'), (50 * 500, 'dag')], 'g') + conv(quedan, 'kg', 'g') != conv(cosecha, 'kg', 'g'):
        mal('el control de la mandioca')
    print('  práctica')
    v = conv(num('3,6'), 'dal', 'l');  cuenta('2', v, f'{fmt(v)} L')
    v = suma([(2, 'Tm'), (4, 'Qm'), (15, 'kg')], 'kg');  cuenta('2', v, f'{fmt(v)} kg')
    paq = conv(suma([(1, 'Tm'), (200, 'kg')], 'kg'), 'kg', 'g') / 500
    cuenta('2', paq, f'{fmt(paq)} paquetes')

    print('Tema 3 · superficie (lectura, ejemplos 3 y 4; ejercitario 5.1, ej. 7; 5.2, ej. 5)')
    c('3', '5.208', 'm²', 'dam²')
    c('3', '6.000', 'cm²', 'm²')
    campo = suma([(3, 'ha'), (15, 'a'), (40, 'ca')], 'm2')
    cuenta('3', campo, f'3 ha 15 a 40 ca = {fmt(campo)} m²')
    precio = (94620000 + 63080000) / campo
    cuenta('3', precio, f'cada m² a ₲ {fmt(precio)}')
    if precio * campo - 63080000 != 94620000:
        mal('el control del campo')
    ter = suma([(2, 'ha'), (50, 'a')], 'a')
    precio2 = (75000000 + 20000 * ter) / conv(ter, 'a', 'm2')
    cuenta('3', precio2, f'cada m² a ₲ {fmt(precio2)}')
    # control: lo que cobra por área, menos la ganancia de esa área, es lo que costó
    if (precio2 * 100 - 20000) * ter != 75000000:
        mal('el control del terreno')
    print('  práctica')
    v = conv(num('2,4'), 'ha', 'm2');  cuenta('3', v, f'{fmt(v)} m²')
    v = conv(F(56000), 'cm2', 'm2');   cuenta('3', v, f'{fmt(v)} m²')
    v = suma([(1, 'ha'), (20, 'a')], 'm2') * 2500;  cuenta('3', v, f'₲ {fmt(v)}')

    print('Tema 4 · volumen (cuestionario 2 y 5; lectura, ejemplo 5; ejercitario 5.1, ej. 9)')
    c('4', '0,62', 'm³', 'dm³')
    c('4', '4.200', 'kL', 'dam³')
    v = suma([(3, 'kl'), (25, 'dal'), (400, 'cl')], 'm3')
    cuenta('4', v, f'3 kL 25 daL 400 cL = {fmt(v)} m³')
    consumo = num('1.362,25') - num('1.348,6')
    v = conv(consumo, 'm3', 'l')
    cuenta('4', v, f'se consumieron {fmt(v)} L')
    if conv(num('1.348,6'), 'm3', 'l') + v != conv(num('1.362,25'), 'm3', 'l'):
        mal('el control del medidor')
    agua = conv(F(12 * 2), 'l', 'kg')               # 12 botellas de 2 L, de agua
    caja = agua + conv(F(12 * 60), 'g', 'kg') + conv(F(1200), 'g', 'kg')
    carga = 40 * caja
    cuenta('4', carga, f'la carga pesa {fmt(carga)} kg')
    # control: todo en gramos, sumado por separado
    if conv(F(40 * 12 * 2), 'l', 'g') + 40 * 12 * 60 + 40 * 1200 != conv(carga, 'kg', 'g'):
        mal('el control de las botellas')
    print('  práctica')
    v = conv(num('2,5'), 'm3', 'l');   cuenta('4', v, f'{fmt(v)} L')
    v = conv(num('1,8'), 'm3', 'kg');  cuenta('4', v, f'{fmt(v)} kg')
    v = conv(F(3), 'm3', 'l') / 12;    cuenta('4', v, f'{fmt(v)} baldes')

    print('Tema 5 · leer las unidades (lectura, ejemplos 4 y 5; cuestionario 3)')
    casos = [
        (conv(F(1, 10), 'km', 'm'), 'm', 'hm', 'la décima del km es el hm'),
        (conv(F(1, 100), 'hm', 'm'), 'm', 'm', 'la centésima del hm es el m'),
        (conv(F(100), 'dl', 'l'), 'l', 'dal', 'la centena del dL es el daL'),
        (conv(100 * 10 * 100 * F(1, 1000), 'dg', 'g'), 'g', 'dag',
         '100 decenas de centenas de milésimas del dg son 1 dag'),
    ]
    for valor, en, u, texto in casos:
        if conv(valor, en, u) != 1:
            mal(f'{texto}: da {conv(valor, en, u)} {u}, no 1')
        cuenta('5', valor, texto)
    # «La centésima de la Tm, en agua, equivale a 10 L»
    v = conv(F(1, 100), 'Tm', 'l')
    if v != 10:
        mal('la centésima de la Tm no son 10 L de agua')
    cuenta('5', v, 'es verdadera: 10 kg de agua son 10 L')
    print('  práctica')
    if conv(F(1, 100), 'km', 'dam') != 1:
        mal('la centésima del km no es el dam')
    cuenta('5', 1, 'el dam')
    if conv(F(1000), 'mg', 'g') != 1:
        mal('el millar del mg no es el g')
    cuenta('5', 1, 'el gramo')
    if conv(F(1), 'kl', 'kg') != conv(F(1), 'Tm', 'kg') or conv(F(1), 'kl', 'kg') == conv(F(1), 'Qm', 'kg'):
        mal('1 kL de agua no pesa 1 Tm')
    cuenta('5', 1, 'falsa: pesa 1.000 kg, que es 1 Tm')

    print('Desafío (ejercitario 5.1, ej. 4)')
    areas = conv(F(6400), 'm2', 'a')
    kg = areas * 15
    m3 = kg / 800                                # 800 kg de trigo ocupan 1 m³
    hl = conv(m3, 'm3', 'hl')
    cobro = hl * 150000
    cuenta('desafio', cobro, f'se cobran ₲ {fmt(cobro)}')
    # control: por el camino de los litros
    if conv(kg / 800 * 1000, 'dm3', 'l') / 100 * 150000 != cobro:
        mal('el control del desafío')
    print(f'  ({fmt(areas)} a, {fmt(kg)} kg, {fmt(m3)} m³, {fmt(hl)} hL)')

    # ── la página ──
    print('La página')
    html = PAGINA.read_text(encoding='utf-8') if PAGINA.exists() else ''
    if not html:
        mal(f'no existe {PAGINA.relative_to(RAIZ)}')
        return
    plano = html.replace('^2', '²').replace('^3', '³')
    for tema, lista in FINALES.items():
        for t in lista:
            if t not in plano:
                mal(f'la página no trae escrito «{t}»')
        repetidas = {t for t in lista if lista.count(t) > 1}
        if repetidas:
            mal(f'tema {tema}: respuestas repetidas {repetidas}')

    # cada factor unitario de la página
    llamadas = re.findall(r'convierte\(([^()]*)\)', html)
    n = 0
    for args in llamadas:
        if args.startswith('...'):           # la definición, en pizarra.js no; por las dudas
            continue
        try:
            partes = ast.literal_eval('(' + args + ',)')
        except (ValueError, SyntaxError):
            mal(f'no puedo leer convierte({args[:60]})')
            continue
        n += 1
        cant, *facs, res = partes
        q, u = medida(cant)
        r, ur = medida(res)
        arriba, abajo, cuentas = [u], [], q
        for f_ in facs:
            (qa, ua), (qb, ub) = medida(f_[0]), medida(f_[1])
            if conv(qa, ua, ub) != qb:
                mal(f'el factor {f_[0]} / {f_[1]} no vale 1')
            cuentas = cuentas * qa / qb
            arriba.append(ua)
            abajo.append(ub)
        for d in abajo:
            if d in arriba:
                arriba.remove(d)
            else:
                mal(f'convierte({cant!r}, …): la unidad {d} de abajo no se tacha con nada')
        if arriba != [ur]:
            mal(f'convierte({cant!r}, …): quedan {arriba} y el resultado está en {ur}')
        if cuentas != r:
            mal(f'convierte({cant!r}, …): la cuenta da {fmt(cuentas)}, no {res}')
        if conv(q, u, ur) != r:
            mal(f'{cant} no son {res}')
    print(f'  {n} conversiones con factor unitario, todas controladas')
    if n < 30:
        mal(f'solo {n} conversiones con convierte(): ¿se volvió a dividir por 100?')

    # ningún renglón encadena dos igualdades: cada renglón de P() y de A() es
    # una cadena entre comillas simples, o una plantilla sin lo de adentro de ${}
    cadenas = re.findall(r"'([^'\n]*)'", html)
    cadenas += [re.sub(r'\$\{[^{}]*\}', '', s) for s in re.findall(r'`([^`]*)`', html)]
    for s in cadenas:
        if len(re.findall(r'\s=\s', s)) > 1:
            mal(f'dos igualdades en un renglón: «{s[:70]}»')
    # en una clase con factor unitario no se divide por 10, 100, 1.000 para cambiar de unidad
    for s in re.findall(r"'([^'\n]*)'", html):
        if re.search(r'\d\s+:\s*(10|100|1\.000|10\.000)\s+(m|L|g|dm|cm|ha|a)\b', s):
            mal(f'un cambio de unidad dividiendo: «{s[:70]}»')

    # todo ejemplo con su control; toda práctica con tres ejercicios
    n_final = len(re.findall(r'\bfinal:[\'`]', html))
    n_control = len(re.findall(r'\bcontrol:[\'`]', html))
    if n_final != n_control:
        mal(f'{n_final} respuestas y {n_control} controles: falta algún control')
    n_prac = len(re.findall(r'\bpractica:\s*\[', html))
    n_resp = len(re.findall(r'\bresp:', html))
    if n_prac == 0 or n_resp != 3 * n_prac:
        mal(f'{n_prac} prácticas y {n_resp} ejercicios: tienen que ser tres por práctica')
    if n_prac and '.practica-diapo' not in html:
        mal('la página tiene práctica y no pone .practica-diapo en data-diapos')


main()
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
