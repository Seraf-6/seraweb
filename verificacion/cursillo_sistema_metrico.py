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
8. Los ítems de opción múltiple del diagnóstico: cada opción se recalcula
   desde el error que la produce, y la página tiene que traer esas
   opciones, en ese orden, con ese error anotado.
9. Los ejercicios del material, transcriptos tal cual: la correcta se
   calcula por dos caminos, las opciones son las del material (en ese
   orden), y la que lleva un error anotado se recalcula desde ese error.
   El enunciado de la página trae los datos del material.
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
    print('Tema 2 · longitud, los ejemplos de la ayuda (lectura, ejemplo 1; ejercitario 5.2, ej. 3)')
    c('2', '0,64', 'km', 'm')
    v = conv(F(3, 4), 'hm', 'm');  cuenta('2', v, '${Q(3, 4)} hm = ' + f'{fmt(v)} m')
    c('2', '18,5', 'cm', 'm')
    lat = suma([(F(1, 5), 'dm'), (num('16,5'), 'cm'), (35, 'mm')], 'm')
    cuenta('2', lat, '${Q(1, 5)} dm 16,5 cm 35 mm = ' + f'{fmt(lat)} m')
    frente = suma([(num('0,64'), 'km'), (F(3, 4), 'hm'), (25, 'm')], 'm')
    lateral = 1000 * lat
    alambre = 4 * (frente + 2 * lateral)
    cuenta('2', alambre, f'hacen falta {fmt(alambre)} m de alambre')
    # control: un hilo es el frente y los dos laterales, sin el fondo
    if alambre / 4 != conv(F(740), 'm', 'm') + 2 * conv(F(22), 'dam', 'm'):
        mal('el control del alambrado')

    print('Tema 3 · masa, los ejemplos de la ayuda (lectura, ejemplo 2; ejercitario 5.2, ej. 9)')
    c('3', '700', 'hg', 'kg')
    cosecha = suma([(4, 'Tm'), (30, 'kg'), (6000, 'g')], 'kg')
    cuenta('3', cosecha, f'4 Tm 30 kg 6.000 g = {fmt(cosecha)} kg')
    bolsa = suma([(700, 'hg'), (500, 'dag')], 'kg')
    quedan = cosecha - 50 * bolsa
    cuenta('3', quedan, f'quedaron {fmt(quedan)} kg')
    if suma([(50 * 700, 'hg'), (50 * 500, 'dag')], 'g') + conv(quedan, 'kg', 'g') != conv(cosecha, 'kg', 'g'):
        mal('el control de la mandioca')

    print('Tema 4 · superficie, los ejemplos de la ayuda (lectura, ejemplos 3 y 4; ejercitario 5.1, ej. 7; 5.2, ej. 5)')
    c('4', '5.208', 'm²', 'dam²')
    c('4', '6.000', 'cm²', 'm²')
    campo = suma([(3, 'ha'), (15, 'a'), (40, 'ca')], 'm2')
    cuenta('4', campo, f'3 ha 15 a 40 ca = {fmt(campo)} m²')
    precio = (94620000 + 63080000) / campo
    cuenta('4', precio, f'cada m² a ₲ {fmt(precio)}')
    if precio * campo - 63080000 != 94620000:
        mal('el control del campo')
    ter = suma([(2, 'ha'), (50, 'a')], 'a')
    precio2 = (75000000 + 20000 * ter) / conv(ter, 'a', 'm2')
    cuenta('4', precio2, f'cada m² a ₲ {fmt(precio2)}')
    # control: lo que cobra por área, menos la ganancia de esa área, es lo que costó
    if (precio2 * 100 - 20000) * ter != 75000000:
        mal('el control del terreno')

    print('Tema 6 · capacidad y volumen, los ejemplos de la ayuda (ejercitario 5.2, ej. 4; cuestionario 2 y 5; lectura, ejemplo 5; ejercitario 5.1, ej. 9)')
    c('6', '7', 'hL', 'L')
    c('6', '350', 'L', 'daL')
    c('6', '0,62', 'm³', 'dm³')
    c('6', '4.200', 'kL', 'dam³')
    v = suma([(3, 'kl'), (25, 'dal'), (400, 'cl')], 'm3')
    cuenta('6', v, f'3 kL 25 daL 400 cL = {fmt(v)} m³')
    consumo = num('1.362,25') - num('1.348,6')
    v = conv(consumo, 'm3', 'l')
    cuenta('6', v, f'se consumieron {fmt(v)} L')
    if conv(num('1.348,6'), 'm3', 'l') + v != conv(num('1.362,25'), 'm3', 'l'):
        mal('el control del medidor')
    agua = conv(F(12 * 2), 'l', 'kg')               # 12 botellas de 2 L, de agua
    caja = agua + conv(F(12 * 60), 'g', 'kg') + conv(F(1200), 'g', 'kg')
    carga = 40 * caja
    cuenta('6', carga, f'la carga pesa {fmt(carga)} kg')
    # control: todo en gramos, sumado por separado
    if conv(F(40 * 12 * 2), 'l', 'g') + 40 * 12 * 60 + 40 * 1200 != conv(carga, 'kg', 'g'):
        mal('el control de las botellas')

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
    item('D1', '2', 'm', [
        (suma([(2, 'km'), (3, 'dam'), (4, 'm')], 'm'), 'pasó los 4 dm como si fueran 4 m'),
        (ok, None),
        (suma([(2, 'km'), (3, 'hm'), (4, 'dm')], 'm'), 'contó mal los escalones: tomó el dam como hm'),
        (suma([(2, 'km'), (3, 'dam')], 'm'), 'se olvidó de una parte: los 4 dm'),
        (suma([(2, 'km'), (3, 'dam'), (4, 'cm')], 'm'), 'corrió la coma un lugar de más en los dm')])

    ok = conv(F(2340), 'ml', 'dal')
    if ok != esc(2340, -4):
        mal('D2: de mL a daL no son cuatro escalones')
    item('D2', '6', 'daL', [
        (esc(2340, -3), 'contó 3 escalones: se quedó en el litro'),
        (esc(2340, -2), 'contó 2 escalones'),
        (ok, None),
        (esc(2340, -5), 'contó 5 escalones: uno de más al cruzar el litro'),
        (esc(2340, 4), 'multiplicó en vez de dividir')])

    item('D3', '3', 'kg', [
        (seguidas(3, 4, 5), 'escribió las cifras seguidas, sin completar con ceros'),
        (conv(F(3), 'Tm', 'kg') + conv(F(4), 'mag', 'kg') + 5, 'tomó el Qm como 10 kg, que es el mag'),
        (conv(F(3), 'Tm', 'kg') + conv(F(4), 'Qm', 'kg') + 5 * 10,
         'completó el cero del lado equivocado: el 5 quedó en las decenas'),
        (suma([(3, 'Tm'), (4, 'Qm'), (5, 'kg')], 'kg'), None),
        (suma([(3, 'Tm'), (4, 'Qm')], 'kg'), 'se olvidó de una parte: los 5 kg')])

    item('D4', '4', 'dm²', [
        (conv(num('6,5'), 'm2', 'dm2'), None),
        (esc(num('6,5'), 1), 'usó el escalón de 10, como en longitud'),
        (esc(num('6,5'), 3), 'usó el escalón de 1.000, como en volumen'),
        (esc(num('6,5'), -2), 'dividió en vez de multiplicar'),
        (esc(num('6,5'), 4), 'contó dos escalones')])

    item('D5', '4', 'm²', [
        (seguidas(4, 7, 3), 'escribió las cifras seguidas, sin completar con ceros'),
        (4 * 1000 + conv(F(7), 'a', 'm2') + 3, 'tomó la ha como 1.000 m²: escalón equivocado'),
        (conv(F(4), 'ha', 'm2') + conv(F(7), 'a', 'm2') + 30, 'completó el cero de las ca del lado equivocado'),
        (conv(F(4), 'ha', 'm2') + 7 * 1000 + 3, 'usó el escalón de 1.000 para el área'),
        (suma([(4, 'ha'), (7, 'a'), (3, 'ca')], 'm2'), None)])

    item('D6', '6', 'dm³', [
        (esc(num('2,4'), 2), 'usó el escalón de 100, como en superficie'),
        (conv(num('2,4'), 'm3', 'dm3'), None),
        (esc(num('2,4'), 1), 'usó el escalón de 10, como en longitud'),
        (esc(num('2,4'), -3), 'dividió en vez de multiplicar'),
        (esc(num('2,4'), 4), 'corrió la coma un lugar de más')])

    item('D7', '6', 'kg', [
        (esc(num('0,75'), 2), 'pasó de m³ a dm³ con el escalón de 100'),
        (esc(num('0,75'), 4), 'corrió la coma un lugar de más'),
        (conv(num('0,75'), 'm3', 'kg'), None),
        (conv(num('0,75'), 'dm3', 'kg'), 'creyó que 1 m³ de agua pesa 1 kg: confundió el m³ con el dm³'),
        (esc(num('0,75'), 1), 'pasó de m³ a dm³ con el escalón de 10')])

    dam = TABLA['dam']
    item('D8', '2', '', [
        (unidad_de_longitud(dam * 100), 'creyó que «centésima» agranda: multiplicó por 100'),
        (unidad_de_longitud(dam / 10), 'dividió por 10: la tomó como décima'),
        (unidad_de_longitud(dam / 100), None),
        (unidad_de_longitud(F(1, 100)), 'contó los escalones desde el metro y no desde el dam'),
        (unidad_de_longitud(dam * 10), 'multiplicó por 10: la tomó como decena')])

    print('Los ejercicios del material, tal cual')
    # P1 · Ejercitario 5.2, ej. 3: el hacendado. El fondo no se alambra.
    frente = suma([(num('0,75'), 'km'), (F(1, 4), 'hm'), (25, 'm')], 'm')
    parte = suma([(1 + F(1, 5), 'dm'), (num('13,5'), 'cm'), (45, 'mm')], 'm')
    lateral = 1000 * parte
    ok = 5 * (frente + 2 * lateral)
    # otro camino: todo en dm, el lateral con decimales
    if conv(5 * (conv(frente, 'm', 'dm') + 2 * 1000 * (num('1,2') + num('1,35') + num('0,45'))), 'dm', 'm') != ok:
        mal('P1: el alambre no da por los dm')
    item('P1', '2', '', [
        (5 * (2 * frente + 2 * lateral), 'alambró también el fondo'),
        (5 * (frente + lateral), 'contó un solo lateral'),
        (5 * (frente + parte), 'contó un solo lateral y se olvidó del millar'),
        (ok, None),
        (5 * (2 * frente + lateral), 'alambró el fondo y contó un solo lateral')])

    # P2 · Ejercitario 5.2, ej. 9: la mandioca
    cosecha = suma([(5, 'Tm'), (20, 'kg'), (5000, 'g')], 'kg')
    bolsa = suma([(750, 'hg'), (500, 'dag')], 'kg')
    q = cosecha - 60 * bolsa
    if suma([(5, 'Tm'), (20, 'kg'), (5000, 'g')], 'g') - 60 * suma([(750, 'hg'), (500, 'dag')], 'g') != conv(q, 'kg', 'g'):
        mal('P2: lo que queda no da en gramos')
    item('P2', '3', '', [
        (conv(q, 'kg', 'Tm'), 'dejó el resultado en Tm'),
        (conv(q, 'kg', 'mag'), 'dejó el resultado en mag'),
        (q, None),
        (conv(q, 'kg', 'hg'), 'dejó el resultado en hg'),
        (conv(q, 'kg', 'Qm'), 'dejó el resultado en Qm')])

    # P3 · Ejercitario 5.1, ej. 7: el campo
    campo = suma([(2, 'ha'), (25, 'a'), (60, 'ca')], 'm2')
    ok = F(48504 + 41736) / campo
    if ok * campo - 48504 != 41736:
        mal('P3: vendiendo a ese precio no gana lo que quiere')
    item('P3', '4', '$', [
        (F(41736) / campo, 'repartió solo la ganancia'),
        (F(48504) / campo, 'repartió solo lo que pagó'),
        (ok, None),
        (F(3), ''),
        (F(5), '')])

    # P4 · el basquetbolista: 1 ft = 30,48 cm; por otro camino, 12 in de 2,54 cm
    ok = 7 * num('30,48')
    if 7 * 12 * num('2,54') != ok:
        mal('P4: el pie no da por las pulgadas')
    if conv(ok, 'cm', 'mm') != num('2.133,6'):
        mal('P4: la opción C no es el resultado en mm')
    item('P4', '5', '', [
        (num('30,48'), 'pasó un solo pie'),
        (ok, None),
        ('2133,6', 'dejó el resultado en mm'),          # así, sin el punto, en el material
        (num('231,36'), ''),
        (num('236,13'), '')])

    # P5 · Ejercitario 5.2, ej. 4: los toneles
    hl = F(120) / 24
    otro = conv(hl, 'hl', 'l') - 280
    ok = conv(otro, 'l', 'dal')
    if conv(hl, 'hl', 'dal') - conv(F(280), 'l', 'dal') != ok:
        mal('P5: el otro tonel no da en daL')
    item('P5', '6', '', [
        (conv(hl, 'hl', 'dal'), 'no restó el primer tonel: son los dos'),
        (ok, None),
        (conv(F(280), 'l', 'dal'), 'dio el primer tonel'),
        (F(18), ''),
        (F(40), '')])


DIAGNOSTICO = [f'D{i}' for i in range(1, 9)]
# los datos de cada ejercicio, como están en el material: el enunciado de la página los trae
FUENTE = {
    'P1': ['alambrar con 5 hilos', 'fondo no es necesario alambrar porque limita por un estero',
           '0,75 km ${Q(1, 4)} hm 25 m de frente', '1 millar por 1${Q(1, 5)} dm 13,5 cm 45 mm'],
    'P2': ['5 Tm 20 kg 5.000 g de mandioca', '60 bolsas de 750 hg 500 dag cada bolsa'],
    'P3': ['2 ha 25 a 60 ca por 48.504 $', 'ganancia de 41.736 $'],
    'P4': ['mide 7 ft de altura', 'en cm es'],
    'P5': ['$ 24 el hL', '$ 120 entre los dos', 'contiene 280 L', 'cantidad de daL'],
}


def controla_items(html):
    print('Los ítems de la página')
    en_pagina = {}
    for cod, cuerpo, ops in re.findall(r"\{\s*cod:'([^']+)'(.*?)opciones:\[(.*?)\]\s*\}", html, flags=re.S):
        lista = []
        for t, ok, err in re.findall(r"\{\s*t:'([^']*)'(?:,\s*(?:(ok:true)|error:'([^']*)'))?\s*\}", ops):
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
    # el diagnóstico: 8 ítems, y cada tema con tabla tiene al menos uno
    temas = {ITEMS[cod][0] for cod in DIAGNOSTICO}
    if len(DIAGNOSTICO) != 8 or not {'2', '3', '4', '6'} <= temas:
        mal(f'el diagnóstico tiene que tener 8 ítems, de longitud, masa, superficie y capacidad: {temas}')
    # los ejercicios del material traen sus datos tal cual
    for cod, datos in FUENTE.items():
        m = re.search(r"\{\s*cod:'%s'.*?enun:`([^`]*)`" % cod, html, flags=re.S)
        if not m:
            mal(f'{cod}: no encuentro su enunciado')
            continue
        for d in datos:
            if d not in m.group(1):
                mal(f'{cod}: el enunciado no trae «{d}», como el material')
    print(f'  {len(ITEMS)} ítems, con sus {sum(len(o) for _, o in ITEMS.values())} opciones controladas')


items()
main()
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
