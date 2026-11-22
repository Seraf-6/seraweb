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

Después:
3. Los problemas se vuelven a hacer desde el enunciado, con otro orden de
   cuentas (el control que dice la página).
4. La página tiene escrita tal cual cada respuesta final.
5. Dentro de un tema no se repite una respuesta.
6. Ningún renglón encadena dos igualdades.
7. Todo ejemplo tiene su control.

    python verificacion/cursillo_sistema_metrico.py
"""
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
    'm3': F(1), 'dm3': F(1, 1000), 'cm3': F(1, 1000000),
}
MAGNITUD = {**{u: 'L' for u in ('mam', 'km', 'hm', 'dam', 'm', 'dm', 'cm', 'mm')},
            **{u: 'C' for u in ('kl', 'hl', 'dal', 'l', 'dl', 'cl', 'ml')},
            **{u: 'M' for u in ('Tm', 'Qm', 'mag', 'kg', 'hg', 'dag', 'g', 'dg', 'cg', 'mg')},
            **{u: 'S' for u in ('km2', 'hm2', 'dam2', 'm2', 'dm2', 'cm2', 'mm2', 'ha', 'a', 'ca')},
            **{u: 'V' for u in ('m3', 'dm3', 'cm3')}}


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
BASE = {'L': 'm', 'C': 'l', 'M': 'g', 'S': 'm', 'V': 'm'}
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
    def a_puente(q, m, p):              # q en la unidad de posición p → en dm³/l/kg
        objetivo = {'V': ESCALERA.index('d'), 'C': ESCALERA.index(''), 'M': ESCALERA.index('k')}[m]
        return q * F(SALTO[m]) ** (objetivo - p)

    def de_puente(q, m, p):
        objetivo = {'V': ESCALERA.index('d'), 'C': ESCALERA.index(''), 'M': ESCALERA.index('k')}[m]
        return q * F(SALTO[m]) ** (p - objetivo)
    return de_puente(a_puente(cant, md, pd), ma, pa)


def conv(cant, de, a):
    """Las dos cuentas tienen que coincidir."""
    x, y = por_tabla(cant, de, a), por_escalera(cant, de, a)
    if x != y:
        mal(f'{cant} {de} → {a}: la tabla da {x} y la escalera {y}')
    return x


def suma(partes, a):
    return sum((conv(c, u, a) for c, u in partes), F(0))


def num(s):
    """'3,75' o '1.257,3' → Fraction."""
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


def unid(u):
    return u.replace('2', '²').replace('3', '³')


# ── las respuestas de la página ──
FINALES = {}          # tema → [respuesta final escrita en la página]


def cuenta(tema, valor, texto):
    """`texto` es la respuesta final de la página; el número que trae tiene que ser `valor`."""
    FINALES.setdefault(tema, []).append(texto)
    print(f'  {tema:8s} {texto}')
    return valor


def main():
    print('Para arrancar')
    # 1,8 km de camino, pasos de 60 cm
    pasos = conv(num('1,8'), 'km', 'm') / conv(F(60), 'cm', 'm')
    assert pasos == 3000
    cuenta('arranque', pasos, f'son {fmt(pasos)} pasos')
    if fmt(pasos * 60) != '180.000' or conv(F(180000), 'cm', 'km') != num('1,8'):
        mal('el control del arranque')

    print('Tema 1 · longitud')
    v = conv(num('3,75'), 'km', 'm');  cuenta('1', v, f'3,75 km = {fmt(v)} m')
    v = conv(F(4260), 'cm', 'm');      cuenta('1', v, f'4.260 cm = {fmt(v)} m')
    v = conv(num('0,48'), 'hm', 'dm'); cuenta('1', v, f'0,48 hm = {fmt(v)} dm')
    v = suma([(2, 'km'), (4, 'hm'), (15, 'm')], 'm'); cuenta('1', v, f'2 km 4 hm 15 m = {fmt(v)} m')
    # incomplejo → complejo
    total = F(3072)
    m_ = total // 100; resto = total - m_ * 100; dm_ = resto // 10; cm_ = resto - dm_ * 10
    if suma([(m_, 'm'), (dm_, 'dm'), (cm_, 'cm')], 'cm') != total:
        mal('3.072 cm no vuelve')
    cuenta('1', total, f'3.072 cm = {fmt(m_)} m {fmt(dm_)} dm {fmt(cm_)} cm')

    print('Tema 2 · capacidad y masa')
    v = conv(num('2,5'), 'l', 'ml');   cuenta('2', v, f'2,5 L = {fmt(v)} mL')
    v = suma([(4, 'dal'), (7, 'l'), (5, 'dl')], 'l'); cuenta('2', v, f'4 daL 7 L 5 dL = {fmt(v)} L')
    v = conv(num('0,85'), 'kg', 'g');  cuenta('2', v, f'0,85 kg = {fmt(v)} g')
    v = suma([(1, 'Tm'), (3, 'Qm'), (45, 'kg')], 'kg'); cuenta('2', v, f'1 Tm 3 Qm 45 kg = {fmt(v)} kg')
    cosecha = suma([(2, 'Tm'), (350, 'kg')], 'kg')
    bolsa = conv(F(5), 'mag', 'kg')
    quedan = cosecha - 40 * bolsa
    cuenta('2', quedan, f'quedaron {fmt(quedan)} kg')
    if quedan + 40 * bolsa != conv(F(2350000), 'g', 'kg'):
        mal('el control de la soja')

    print('Tema 3 · leer las unidades')
    # la décima del km, la centésima del km, la centena del dl, la milésima de la Tm,
    # 10 decenas de décimas del hm: cada una tiene que ser exactamente una unidad
    casos = [
        (conv(F(1), 'km', 'm') / 10, 'm', 'hm', 'la décima del km es el hm'),
        (conv(F(1), 'km', 'm') / 100, 'm', 'dam', 'la centésima del km es el dam'),
        (conv(F(100), 'dl', 'l'), 'l', 'dal', 'la centena del dL es el daL'),
        (conv(F(1), 'Tm', 'kg') / 1000, 'kg', 'kg', 'la milésima de la Tm es el kg'),
        (conv(10 * 10 * F(1, 10), 'hm', 'm'), 'm', 'km', '10 decenas de décimas del hm son 1 km'),
    ]
    for valor, en, unidad, texto in casos:
        if conv(valor, en, unidad) != 1:
            mal(f'{texto}: da {conv(valor, en, unidad)} {unidad}, no 1')
        cuenta('3', valor, texto)

    print('Tema 4 · superficie')
    v = conv(num('3,5'), 'm2', 'dm2');    cuenta('4', v, f'3,5 m² = {fmt(v)} dm²')
    v = conv(F(45000), 'cm2', 'm2');      cuenta('4', v, f'45.000 cm² = {fmt(v)} m²')
    v = conv(num('0,07'), 'km2', 'dam2'); cuenta('4', v, f'0,07 km² = {fmt(v)} dam²')
    v = suma([(3, 'ha'), (8, 'a'), (5, 'ca')], 'm2'); cuenta('4', v, f'3 ha 8 a 5 ca = {fmt(v)} m²')
    sup = F(250) * F(120)
    ha = conv(sup, 'm2', 'ha')
    precio = ha * 18000000
    cuenta('4', precio, f'el terreno cuesta ₲ {fmt(precio)}')
    if precio / 18000000 != conv(F(3), 'hm2', 'ha') or ha != 3:
        mal('el control del terreno')

    print('Tema 5 · volumen')
    v = conv(num('5,7'), 'dm3', 'cm3');  cuenta('5', v, f'5,7 dm³ = {fmt(v)} cm³')
    v = conv(num('0,35'), 'm3', 'l');    cuenta('5', v, f'0,35 m³ = {fmt(v)} L')
    v = conv(num('1,2'), 'm3', 'kg');    cuenta('5', v, f'el tanque tiene {fmt(v)} kg de agua')
    v = conv(F(3), 'm3', 'l') + conv(F(40), 'dm3', 'l') + conv(F(500), 'cm3', 'l')
    cuenta('5', v, f'3 m³ 40 dm³ 500 cm³ = {fmt(v)} L')
    consumo = num('2.326,15') - num('2.318,6')
    v = conv(consumo, 'm3', 'l')
    cuenta('5', v, f'se consumieron {fmt(v)} L')
    if conv(num('2.326,15'), 'm3', 'l') - conv(num('2.318,6'), 'm3', 'l') != v:
        mal('el control del medidor')

    print('Desafío')
    frente = conv(num('0,45'), 'km', 'm') + conv(F(5), 'dam', 'm')
    fondo = conv(F(2), 'hm', 'm') + conv(F(4), 'dam', 'm')
    alambre = 4 * 2 * (frente + fondo)
    rollos = -(-alambre // 500)
    cuenta('desafio', rollos, f'hacen falta {fmt(rollos)} rollos')
    if not (11 * 500 < alambre <= 12 * 500):
        mal('el control de los rollos')
    if conv(frente * fondo, 'm2', 'ha') != 12:
        mal('la finca no mide 12 ha (lo dice el observador del desafío)')
    print(f'  (frente {fmt(frente)} m, fondo {fmt(fondo)} m, alambre {fmt(alambre)} m, '
          f'superficie {fmt(conv(frente * fondo, "m2", "ha"))} ha)')

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
    # ningún renglón encadena dos igualdades: cada renglón de P() y de A() es
    # una cadena entre comillas simples
    for s in re.findall(r"'([^'\n]*)'", html):
        if len(re.findall(r'\s=\s', s)) > 1:
            mal(f'dos igualdades en un renglón: «{s[:70]}»')
    # todo ejemplo con su control
    n_final = len(re.findall(r'\bfinal:', html))
    n_control = len(re.findall(r'\bcontrol:', html))
    if n_final != n_control:
        mal(f'{n_final} respuestas y {n_control} controles: falta algún control')
    # el material del Poli no se copia: ningún ejemplo suyo
    for frase in ('48.504', '2 ha 25 a 60 ca', '1257,3', '1.257,3', '2742,8', '2 kl 34 dal',
                  '0,037 hm', 'mandioca', 'hacendado', 'tártago'):
        if frase in html:
            mal(f'la página trae «{frase}», que es del material del Poli')


main()
print()
print('Todo en orden.' if not fallos else f'{len(fallos)} falla(s).')
sys.exit(1 if fallos else 0)
