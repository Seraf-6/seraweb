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
4. La página tiene escrita tal cual cada respuesta final.
5. Dentro de un tema no se repite una respuesta.
6. Ningún renglón encadena dos igualdades.
7. Todo ejemplo tiene su control.
8. Los ítems de opción múltiple (el diagnóstico y las puertas): cada opción
   se recalcula desde el error que la produce, y la página tiene que traer
   esas opciones, en ese orden, con ese error anotado.
9. Las franjas traen los ejercicios del libro según la clasificación de
   acá, sin repetir y sin referencias que no existan.
10. No hay rayas (—) en la página.

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

    # todo ejemplo con su control
    n_final = len(re.findall(r'\bfinal:[\'`]', html))
    n_control = len(re.findall(r'\bcontrol:[\'`]', html))
    if n_final != n_control:
        mal(f'{n_final} respuestas y {n_control} controles: falta algún control')

    # sin rayas en el texto de la página
    if '—' in html:
        mal(f'la página tiene {html.count("—")} raya(s) (—)')

    controla_items(html)
    controla_franjas(html)


# ══ los ítems de opción múltiple ══
# Cada ítem se arma acá: la correcta y cada distractor desde el error que lo
# produce, con su número y su descripción. La página tiene que traer
# exactamente esas opciones, en ese orden, con esa descripción del error.

def esc(q, k):
    """Corre la coma k lugares (k escalones de 10): positivo multiplica."""
    return F(q) * F(10) ** k


def seguidas(*cifras):
    """El error de escribir las cifras seguidas, sin completar con ceros."""
    return F(''.join(str(c) for c in cifras))


def unidad_de_longitud(valor_m):
    """La unidad de longitud que vale exactamente valor_m metros."""
    for u in ('mam', 'km', 'hm', 'dam', 'm', 'dm', 'cm', 'mm'):
        if TABLA[u] == valor_m:
            return u
    raise ValueError(valor_m)


def complejo(txt):
    """'7 km 8 m 3 dm' → su valor en m."""
    t = txt.split()
    return suma([(num(t[i]), t[i + 1]) for i in range(0, len(t), 2)], 'm')


ITEMS = {}      # cod → (tema, [(texto, None si es la correcta, o el error)])


def item(cod, tema, unidad, opciones):
    """opciones: [(valor, None) para la correcta, (valor, 'error') para las otras].
    El valor es un número (se escribe con fmt y la unidad) o un texto."""
    ops = [(v if isinstance(v, str) else f'{fmt(v)} {unidad}'.strip(), e) for v, e in opciones]
    textos = [t for t, _ in ops]
    if len(set(textos)) != len(textos):
        mal(f'{cod}: dos opciones iguales {textos}')
    if sum(e is None for _, e in ops) != 1:
        mal(f'{cod}: tiene que haber una sola correcta')
    ITEMS[cod] = (tema, ops)
    print(f'  {cod:5s} ' + ' | '.join(t + (' ✓' if e is None else '') for t, e in ops))


def items():
    print('Diagnóstico')
    ok = suma([(2, 'km'), (3, 'dam'), (4, 'dm')], 'm')
    item('D1', '1', 'm', [
        (suma([(2, 'km'), (3, 'dam'), (4, 'm')], 'm'), 'pasó los 4 dm como si fueran 4 m'),
        (ok, None),
        (suma([(2, 'km'), (3, 'hm'), (4, 'dm')], 'm'), 'contó mal los escalones: tomó el dam como hm'),
        (suma([(2, 'km'), (3, 'dam')], 'm'), 'se olvidó de una parte: los 4 dm'),
        (suma([(2, 'km'), (3, 'dam'), (4, 'cm')], 'm'), 'corrió la coma un lugar de más en los dm')])

    ok = conv(F(2340), 'ml', 'dal')
    if ok != esc(2340, -4):
        mal('D2: de mL a daL no son cuatro escalones')
    item('D2', '2', 'daL', [
        (esc(2340, -3), 'contó 3 escalones: se quedó en el litro'),
        (esc(2340, -2), 'contó 2 escalones'),
        (ok, None),
        (esc(2340, -5), 'contó 5 escalones: uno de más al cruzar el litro'),
        (esc(2340, 4), 'multiplicó en vez de dividir')])

    item('D3', '2', 'kg', [
        (seguidas(3, 4, 5), 'escribió las cifras seguidas, sin completar con ceros'),
        (conv(F(3), 'Tm', 'kg') + conv(F(4), 'mag', 'kg') + 5, 'tomó el Qm como 10 kg, que es el mag'),
        (conv(F(3), 'Tm', 'kg') + conv(F(4), 'Qm', 'kg') + 5 * 10,
         'completó el cero del lado equivocado: el 5 quedó en las decenas'),
        (suma([(3, 'Tm'), (4, 'Qm'), (5, 'kg')], 'kg'), None),
        (suma([(3, 'Tm'), (4, 'Qm')], 'kg'), 'se olvidó de una parte: los 5 kg')])

    item('D4', '3', 'dm²', [
        (conv(num('6,5'), 'm2', 'dm2'), None),
        (esc(num('6,5'), 1), 'usó el escalón de 10, como en longitud'),
        (esc(num('6,5'), 3), 'usó el escalón de 1.000, como en volumen'),
        (esc(num('6,5'), -2), 'dividió en vez de multiplicar'),
        (esc(num('6,5'), 4), 'contó dos escalones')])

    item('D5', '3', 'm²', [
        (seguidas(4, 7, 3), 'escribió las cifras seguidas, sin completar con ceros'),
        (4 * 1000 + conv(F(7), 'a', 'm2') + 3, 'tomó la ha como 1.000 m²: escalón equivocado'),
        (conv(F(4), 'ha', 'm2') + conv(F(7), 'a', 'm2') + 30, 'completó el cero de las ca del lado equivocado'),
        (conv(F(4), 'ha', 'm2') + 7 * 1000 + 3, 'usó el escalón de 1.000 para el área'),
        (suma([(4, 'ha'), (7, 'a'), (3, 'ca')], 'm2'), None)])

    item('D6', '4', 'dm³', [
        (esc(num('2,4'), 2), 'usó el escalón de 100, como en superficie'),
        (conv(num('2,4'), 'm3', 'dm3'), None),
        (esc(num('2,4'), 1), 'usó el escalón de 10, como en longitud'),
        (esc(num('2,4'), -3), 'dividió en vez de multiplicar'),
        (esc(num('2,4'), 4), 'corrió la coma un lugar de más')])

    item('D7', '4', 'kg', [
        (esc(num('0,75'), 2), 'pasó de m³ a dm³ con el escalón de 100'),
        (esc(num('0,75'), 4), 'corrió la coma un lugar de más'),
        (conv(num('0,75'), 'm3', 'kg'), None),
        (conv(num('0,75'), 'dm3', 'kg'), 'creyó que 1 m³ de agua pesa 1 kg: confundió el m³ con el dm³'),
        (esc(num('0,75'), 1), 'pasó de m³ a dm³ con el escalón de 10')])

    dam = TABLA['dam']
    item('D8', '5', '', [
        (unidad_de_longitud(dam * 100), 'creyó que «centésima» agranda: multiplicó por 100'),
        (unidad_de_longitud(dam / 10), 'dividió por 10: la tomó como décima'),
        (unidad_de_longitud(dam / 100), None),
        (unidad_de_longitud(F(1, 100)), 'contó los escalones desde el metro y no desde el dam'),
        (unidad_de_longitud(dam * 10), 'multiplicó por 10: la tomó como decena')])

    print('La puerta del tema 1')
    q = num('0,036')
    if conv(q, 'hm', 'cm') != esc(q, 4):
        mal('L-P1: de hm a cm no son cuatro escalones')
    item('L-P1', '1', 'cm', [
        (esc(q, 3), 'contó 3 escalones en vez de 4'),
        (conv(q, 'hm', 'cm'), None),
        (esc(q, 2), 'se quedó en el metro: contó 2 escalones'),
        (esc(q, 5), 'contó 5 escalones'),
        (esc(q, -4), 'dividió en vez de multiplicar')])

    q = F(45800)
    item('L-P2', '1', 'dam', [
        (esc(q, -3), 'se quedó en el metro: contó un escalón de menos al cruzarlo'),
        (esc(q, -2), 'contó 2 escalones'),
        (esc(q, -5), 'contó un escalón de más'),
        (conv(q, 'mm', 'dam'), None),
        (esc(q, 4), 'multiplicó en vez de dividir')])

    item('L-P3', '1', 'm', [
        (seguidas(5, 6, 8), 'escribió las cifras seguidas, sin completar con ceros'),
        (suma([(5, 'hm'), (6, 'm'), (8, 'dm')], 'm'), 'no completó con cero los decimales: tomó 8 cm como 8 dm'),
        (suma([(5, 'hm'), (6, 'm'), (8, 'cm')], 'm'), None),
        (suma([(5, 'hm'), (6, 'dam'), (8, 'cm')], 'm'), 'contó mal los escalones: tomó los 6 m como dam'),
        (suma([(5, 'hm'), (8, 'cm')], 'm'), 'se olvidó de una parte: los 6 m')])

    meta = num('7.008,3')
    ops = [('7 km 8 m 3 dm', None),
           ('7 km 8 dam 3 dm', 'no completó con ceros: el 8 quedó en los dam'),
           ('7 km 8 m 3 cm', 'corrió la coma un lugar en la parte decimal'),
           ('7 hm 8 m 3 dm', 'contó un escalón de menos: tomó el km como hm'),
           ('7 km 8 hm 3 dm', 'contó mal los escalones al cruzar el metro')]
    valores = [complejo(t) for t, _ in ops]
    for (t, e), v in zip(ops, valores):
        if (v == meta) != (e is None):
            mal(f'L-P4: «{t}» vale {fmt(v)} m')
    if len(set(valores)) != len(valores):
        mal('L-P4: dos complejos valen lo mismo')
    item('L-P4', '1', '', ops)

    frente = suma([(1, 'hm'), (2, 'dam')], 'm')
    fondo = suma([(num('0,08'), 'km'), (5, 'm')], 'm')
    fondo_mal = suma([(esc(num('0,08'), 2), 'm'), (5, 'm')], 'm')      # 0,08 km leído como 8 m
    frente_mal = suma([(1, 'hm'), (2, 'm')], 'm')
    item('L-P5', '1', 'm', [
        (3 * (frente + fondo), 'sumó el frente y el fondo una sola vez: la mitad del contorno'),
        (2 * (frente + fondo), 'se olvidó de los 3 hilos'),
        (3 * 2 * (frente + fondo_mal), 'pasó 0,08 km como 8 m: corrió la coma de menos'),
        (3 * 2 * (frente + fondo), None),
        (3 * 2 * (frente_mal + fondo), 'tomó los 2 dam como 2 m')])
    # el control del problema, por otro camino: el contorno en dam
    if conv(3 * 2 * (F(12) + num('8,5')), 'dam', 'm') != 3 * 2 * (frente + fondo):
        mal('L-P5: el contorno no da')

    print('Tema 1, franja A')
    q = num('3,2')
    item('L-A1', '1', 'm', [
        (esc(q, 2), 'contó 2 escalones en vez de 3'),
        (esc(q, 4), 'contó 4 escalones'),
        (conv(q, 'km', 'm'), None),
        (esc(q, -3), 'dividió en vez de multiplicar'),
        (esc(q, 1), 'contó 1 escalón')])

    item('L-A2', '1', 'm', [
        (esc(85, 2), 'multiplicó en vez de dividir'),
        (esc(85, -1), 'contó 1 escalón en vez de 2'),
        (esc(85, -3), 'contó 3 escalones'),
        (F(85), 'cambió la unidad sin cambiar el número'),
        (conv(F(85), 'cm', 'm'), None)])

    q = num('4,7')
    item('L-A3', '1', 'dm', [
        (esc(q, 3), 'contó 3 escalones'),
        (conv(q, 'dam', 'dm'), None),
        (esc(q, 1), 'contó 1 escalón: no cruzó el metro'),
        (esc(q, -2), 'dividió en vez de multiplicar'),
        (q, 'cambió la unidad sin cambiar el número')])

    item('L-A4', '1', 'm', [
        (suma([(6, 'hm'), (4, 'dam')], 'm'), 'tomó los 4 m como 4 dam: el cero quedó del lado equivocado'),
        (seguidas(6, 4), 'escribió las cifras seguidas, sin completar con ceros'),
        (suma([(6, 'km'), (4, 'm')], 'm'), 'tomó el hm como km'),
        (suma([(6, 'hm'), (4, 'm')], 'm'), None),
        (suma([(6, 'hm')], 'm'), 'se olvidó de una parte: los 4 m')])

    print('Tema 1, franja B')
    meta = conv(F(40506), 'cm', 'm')
    ops = [('4 hm 5 dam 6 cm', 'no completó con ceros: el 5 quedó en los dam'),
           ('4 km 5 m 6 cm', 'contó un escalón de más: tomó el hm como km'),
           ('4 hm 5 m 60 cm', 'completó el cero del lado equivocado en los cm'),
           ('4 hm 5 m 6 mm', 'corrió la coma un lugar en la parte decimal'),
           ('4 hm 5 m 6 cm', None)]
    valores = [complejo(t) for t, _ in ops]
    for (t, e), v in zip(ops, valores):
        if (v == meta) != (e is None):
            mal(f'L-B1: «{t}» vale {fmt(v)} m')
    if len(set(valores)) != len(valores):
        mal('L-B1: dos complejos valen lo mismo')
    item('L-B1', '1', '', ops)

    tramo = suma([(2, 'km'), (8, 'hm')], 'm')
    total = tramo + 950
    item('L-B2', '1', 'km', [
        (esc(conv(total, 'm', 'km'), 1), 'contó 2 escalones al pasar a km'),
        (conv(suma([(2, 'km'), (8, 'dam')], 'm') + 950, 'm', 'km'), 'tomó los 8 hm como 8 dam'),
        (conv(tramo, 'm', 'km') + 950, 'sumó km con m sin pasar a la misma unidad'),
        (esc(conv(total, 'm', 'km'), -1), 'contó 4 escalones al pasar a km'),
        (conv(total, 'm', 'km'), None)])
    # control: sumado en hm
    if conv(F(28) + conv(F(950), 'm', 'hm'), 'hm', 'km') != conv(total, 'm', 'km'):
        mal('L-B2: la suma no da')

    vuelta = num('0,4')
    item('L-B3', '1', 'hm', [
        (num('12,5') * vuelta, 'dejó el resultado en km'),
        (12 * conv(vuelta, 'km', 'hm'), 'se olvidó de la media vuelta'),
        (num('12,5') * conv(vuelta, 'km', 'hm'), None),
        (num('12,5') * conv(vuelta, 'km', 'dam'), 'pasó a dam y no a hm: un escalón de más'),
        (num('12,5') * esc(vuelta, -1), 'dividió en vez de multiplicar al pasar de km a hm')])

    print('Tema 1, franja C')
    cinta = suma([(2, 'dam'), (5, 'm')], 'm')
    item('L-C1', '1', 'trozos', [
        (conv(cinta, 'm', 'mm') * 10 / 125, 'corrió la coma un lugar de más al pasar a mm'),
        (conv(cinta, 'm', 'mm') / 125, None),
        (conv(suma([(2, 'dam')], 'm'), 'm', 'mm') / 125, 'se olvidó de una parte: los 5 m'),
        (conv(cinta, 'm', 'cm') / 125, 'pasó a cm y no a mm'),
        (cinta / 125, 'dividió los metros por 125 sin pasar a la misma unidad')])

    frente = suma([(num('0,6'), 'km'), (F(1, 2), 'hm'), (30, 'm')], 'm')
    lateral = 1000 * suma([(F(1, 4), 'dm'), (num('12,5'), 'cm'), (25, 'mm')], 'm')
    lateral_mal = 1000 * suma([(F(1, 4), 'm'), (num('12,5'), 'cm'), (25, 'mm')], 'm')
    item('L-C2', '1', 'm', [
        (4 * (frente + 2 * lateral), None),
        (4 * (2 * frente + 2 * lateral), 'alambró también el fondo'),
        (4 * (frente + lateral), 'contó un solo lateral'),
        (frente + 2 * lateral, 'se olvidó de los 4 hilos'),
        (4 * (frente + 2 * lateral_mal), 'pasó 1/4 dm como 0,25 m: corrió la coma de menos')])
    if 4 * (conv(F(68), 'dam', 'm') + 2 * conv(num('1,75'), 'hm', 'm')) != 4 * (frente + 2 * lateral):
        mal('L-C2: el alambre no da')

    recorre = 3 * 2 * 60 * 60                         # cm, en 2 horas
    item('L-C3', '1', 'hm', [
        (esc(recorre, -3), 'contó un escalón de menos al pasar a hm'),
        (conv(F(3 * 2 * 60), 'cm', 'hm'), 'pasó las 2 horas a minutos y no a segundos'),
        (esc(recorre, -2), 'se quedó en el metro'),
        (conv(F(recorre), 'cm', 'hm'), None),
        (esc(recorre, -5), 'contó un escalón de más')])


DIAGNOSTICO = [f'D{i}' for i in range(1, 9)]
PUERTAS = {'1': ['L-P1', 'L-P2', 'L-P3', 'L-P4', 'L-P5']}


def controla_items(html):
    print('Los ítems de la página')
    en_pagina = {}
    for cod, cuerpo, ops in re.findall(r"\{\s*cod:'([^']+)'(.*?)opciones:\[(.*?)\]\s*\}", html, flags=re.S):
        lista = []
        for t, ok, err in re.findall(r"\{\s*t:'([^']*)',\s*(?:(ok:true)|error:'([^']*)')\s*\}", ops):
            lista.append((t, None if ok else err))
        tema = re.search(r"tema:'([^']+)'", cuerpo)
        en_pagina[cod] = (tema.group(1) if tema else None, lista)
    for cod, (tema, ops) in ITEMS.items():
        if cod not in en_pagina:
            mal(f'{cod}: no está en la página')
            continue
        t_pag, ops_pag = en_pagina[cod]
        if ops_pag != ops:
            for k, (a, b) in enumerate(zip(ops, ops_pag + [None] * 5)):
                if a != b:
                    mal(f'{cod}, opción {"ABCDE"[k]}: la página dice {b}, tiene que ser {a}')
        if cod in DIAGNOSTICO and t_pag != tema:
            mal(f'{cod}: es del tema {tema}, la página dice {t_pag}')
    for cod in en_pagina:
        if cod not in ITEMS:
            mal(f'{cod}: está en la página y no en el verificador')
    # el diagnóstico: 8 ítems, de 1 a 2 por tema, los cinco temas
    por_tema = {}
    for cod in DIAGNOSTICO:
        por_tema[ITEMS[cod][0]] = por_tema.get(ITEMS[cod][0], 0) + 1
    if sorted(por_tema) != ['1', '2', '3', '4', '5'] or not all(1 <= v <= 2 for v in por_tema.values()):
        mal(f'el diagnóstico tiene que tener 1 o 2 ítems de cada tema: {por_tema}')
    # cada puerta: 5 ítems, en orden, del tema
    puertas = [html[m.end() - 1:cierra(html, m.end() - 1) + 1] for m in re.finditer(r'puerta:\s*\{', html)]
    if len(puertas) != len(PUERTAS):
        mal(f'la página tiene {len(puertas)} puertas y el verificador {len(PUERTAS)}')
    for (tema, cods), bloque in zip(sorted(PUERTAS.items()), puertas):
        if len(cods) != 5:
            mal(f'la puerta del tema {tema} tiene que tener 5 ítems')
        if re.findall(r"cod:'([^']+)'", bloque) != cods:
            mal(f'la puerta del tema {tema} no trae {cods}')
    print(f'  {len(ITEMS)} ítems, con sus {sum(len(o) for _, o in ITEMS.values())} opciones controladas')


# ══ las franjas: qué ejercicios del libro van en cada tema y franja ══
# La clasificación es la del plan (22/11/2026). Un ejercicio que se repite en
# otra parte del material (cuestionario 6 = 1, ejercitario 5.2 ej. 7 = 5.1 ej. 9)
# va una sola vez.
LIBRO = {'5.1': range(1, 11), '5.2': range(1, 11), 'cuest': range(1, 11)}
CLASIFICACION = {
    '1': {'A': [], 'B': [('5.2', 1)], 'C': [('5.2', 3)]},
    '2': {'A': [], 'B': [('5.2', 4), ('5.2', 9)],
          'C': [('5.1', 2), ('5.1', 6), ('5.1', 10), ('5.2', 6), ('5.2', 8)]},
    '3': {'A': [], 'B': [('5.1', 7), ('5.2', 5)], 'C': [('5.1', 3), ('cuest', 4), ('cuest', 8)]},
    '4': {'A': [], 'B': [('cuest', 2), ('cuest', 5), ('5.1', 5), ('5.1', 8), ('5.1', 9)],
          'C': [('5.1', 4), ('5.2', 10), ('cuest', 9), ('cuest', 10)]},
    '5': {'A': [], 'B': [('5.1', 1), ('cuest', 1), ('cuest', 3), ('cuest', 7)], 'C': []},
}
# los ítems nuevos de cada franja, en orden (van después de los del libro)
NUEVOS = {
    '1': {'A': ['L-A1', 'L-A2', 'L-A3', 'L-A4'], 'B': ['L-B1', 'L-B2', 'L-B3'], 'C': ['L-C1', 'L-C2', 'L-C3']},
}


def cierra(s, i):
    """El índice de la llave o corchete que cierra el que abre en s[i]."""
    par = {'{': '}', '[': ']'}[s[i]]
    prof = 0
    for j in range(i, len(s)):
        if s[j] == s[i]:
            prof += 1
        elif s[j] == par:
            prof -= 1
            if not prof:
                return j
    raise ValueError('sin cerrar')


def controla_franjas(html):
    print('Las franjas')
    bloques = [html[m.end() - 1:cierra(html, m.end() - 1) + 1] for m in re.finditer(r'franjas:\s*\{', html)]
    if len(bloques) != len(CLASIFICACION):
        mal(f'{len(bloques)} temas con franjas; tienen que ser {len(CLASIFICACION)}')
    vistos = set()
    for tema, bloque in zip(sorted(CLASIFICACION), bloques):
        for k in 'ABC':
            m = re.search(k + r':\s*\[', bloque)
            lista = bloque[m.end() - 1:cierra(bloque, m.end() - 1) + 1] if m else '[]'
            libro = [(a, int(n)) for a, n in re.findall(r"libro:'([^']+)',\s*n:(\d+)", lista)]
            for a, n in libro:
                if a not in LIBRO or n not in LIBRO[a]:
                    mal(f'tema {tema}, franja {k}: {a} ej. {n} no existe en el material')
                if (a, n) in vistos:
                    mal(f'{a} ej. {n} está dos veces en la grilla')
                vistos.add((a, n))
            if libro != CLASIFICACION[tema][k]:
                mal(f'tema {tema}, franja {k}: la página trae {libro}, la clasificación dice {CLASIFICACION[tema][k]}')
            nuevos = re.findall(r"cod:'([^']+)'", lista)
            if nuevos != NUEVOS.get(tema, {}).get(k, []):
                mal(f'tema {tema}, franja {k}: la página trae los ítems {nuevos}, tienen que ser {NUEVOS.get(tema, {}).get(k, [])}')
            if re.search(r"cod:.*libro:", lista, flags=re.S):
                mal(f'tema {tema}, franja {k}: los ítems nuevos van después de los del libro')
            print(f'  tema {tema} {k}: {len(libro)} del libro, {len(re.findall(r"cod:", lista))} nuevos')


items()
main()
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
