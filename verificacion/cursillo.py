"""Cursillo · verificador del módulo.

    python verificacion/cursillo.py

Comprueba cursillo_datos.py y la página que build.py generó:

  · cada semana arranca un lunes y no se repite; cada clase tiene un día de
    lunes a sábado y un turno que existe; no hay dos clases en el mismo día y
    turno; el grupo es «INSTITUCIÓN MODALIDAD N» con institución conocida;
  · cada clase apunta a temas que existen en el banco, y cada archivo
    enlazado (clase, PDF) está en el repositorio;
  · no hay PDF de clave en cursillo/;
  · en los datos no aparece ningún nombre de otro docente (la lista está acá,
    a propósito: los datos no la importan);
  · cursillo/index.html trae cada semana, cada día con su fecha y cada
    consigna, escritas tal cual.

Sale con código 1 si algo falla. Lo que falta y no es un error (temas sin
clase, la semana que viene sin cargar) se lista aparte.
"""
import datetime as dt
import html
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import cursillo_datos as D  # noqa: E402

# Los nombres que aparecen en las grillas de la coordinación. Ninguno va al sitio.
OTROS_DOCENTES = ['Ivan', 'Iván', 'Daynin', 'Eche', 'Guille', 'Genez', 'Joseca', 'Bruno',
                  'Araceli', 'Maldonado', 'Santi', 'Alejandro', 'Orlando']

DIAS_ISO = {'lun': 0, 'mar': 1, 'mie': 2, 'jue': 3, 'vie': 4, 'sab': 5}
errores, pendientes = [], []


def error(msg):
    errores.append(msg)


# ── las semanas ──
vistos = set()
for s in D.SEMANAS:
    try:
        lun = dt.date.fromisoformat(s['lunes'])
    except ValueError:
        error(f'semana {s["lunes"]!r}: la fecha no se lee')
        continue
    if lun.weekday() != 0:
        error(f'semana {s["lunes"]}: no es lunes')
    if s['lunes'] in vistos:
        error(f'semana {s["lunes"]}: está dos veces')
    vistos.add(s['lunes'])
    ocupados = set()
    for c in s['clases']:
        donde = f'{s["lunes"]} {c.get("dia")} {c.get("turno")}'
        if c.get('dia') not in DIAS_ISO:
            error(f'{donde}: el día no es lun…sab')
        if c.get('turno') not in D.TURNOS:
            error(f'{donde}: el turno no es TM ni TT')
        if (c.get('dia'), c.get('turno')) in ocupados:
            error(f'{donde}: hay dos clases en el mismo día y turno')
        ocupados.add((c.get('dia'), c.get('turno')))
        m = re.fullmatch(r'([A-Z]+) (INT|EXT) (\d+)', c.get('grupo', ''))
        if not m or m.group(1) not in D.INSTITUCIONES:
            error(f'{donde}: el grupo {c.get("grupo")!r} no es «INSTITUCIÓN INT|EXT N» '
                  f'con institución de {sorted(D.INSTITUCIONES)}')
        for k in ('materia', 'consigna'):
            if not c.get(k, '').strip():
                error(f'{donde}: falta {k}')
        if not c.get('temas'):
            pendientes.append(f'{donde}: la clase no apunta a ningún tema')
        for t in c.get('temas', []):
            if t not in D.TEMAS:
                error(f'{donde}: el tema {t!r} no está en TEMAS')

# ── el banco ──
for tid, t in D.TEMAS.items():
    if not re.fullmatch(r'[a-z0-9-]+', tid):
        error(f'tema {tid!r}: el id va en minúsculas, con guiones')
    for k in ('titulo', 'materia', 'bloque'):
        if not t.get(k):
            error(f'tema {tid}: falta {k}')
    archivos = ([t['clase']] if t.get('clase') else []) + \
               [u for _, u in t.get('teoria', [])] + \
               [u for _, _, u in t.get('ejercicios', []) if u]
    for a in archivos:
        if not (RAIZ / a).is_file():
            error(f'tema {tid}: no existe {a}')
    if not t.get('clase'):
        pendientes.append(f'tema {tid}: sin clase para proyectar')

# ── nada de claves ──
for p in (RAIZ / 'cursillo').rglob('*'):
    if p.is_file() and re.search(r'CLAVE|RESPUESTA', p.name, re.I):
        error(f'{p.relative_to(RAIZ)}: parece una clave; las claves no se publican')

# ── nada de otros docentes en los datos ──
fuente = (RAIZ / 'cursillo_datos.py').read_text(encoding='utf-8')
for n in OTROS_DOCENTES:
    if re.search(r'\b' + re.escape(n) + r'\b', fuente):
        error(f'cursillo_datos.py nombra a «{n}»: solo van las clases propias')

# ── la página generada ──
pagina = RAIZ / 'cursillo' / 'index.html'
if not pagina.is_file():
    error('falta cursillo/index.html: correr python build.py')
else:
    txt = pagina.read_text(encoding='utf-8')
    for s in D.SEMANAS:
        if f'data-lunes="{s["lunes"]}"' not in txt:
            error(f'la página no trae la semana {s["lunes"]}: correr python build.py')
        lun = dt.date.fromisoformat(s['lunes'])
        for c in s['clases']:
            f = lun + dt.timedelta(days=DIAS_ISO.get(c['dia'], 0))
            if f'data-fecha="{f.isoformat()}"' not in txt:
                error(f'la página no trae el día {f}')
            if html.escape(c['consigna']) not in txt:
                error(f'la página no trae la consigna {c["consigna"]!r}: correr python build.py')
    for tid in D.TEMAS:
        if f'id="tema-{tid}"' not in txt:
            error(f'la página no trae el tema {tid}: correr python build.py')
    for n in OTROS_DOCENTES:
        if re.search(r'\b' + re.escape(n) + r'\b', txt):
            error(f'cursillo/index.html nombra a «{n}»')

# ── la semana que viene ──
hoy = dt.date.today()
prox = hoy + dt.timedelta(days=7 - hoy.weekday())
if prox.isoformat() not in vistos and hoy.weekday() >= 3:
    pendientes.append(f'la semana del {prox} todavía no está cargada')

print(f'Cursillo: {len(D.SEMANAS)} semana(s), '
      f'{sum(len(s["clases"]) for s in D.SEMANAS)} clase(s), {len(D.TEMAS)} tema(s).')
if pendientes:
    print('Pendiente (no es error):')
    for p in pendientes:
        print('  ·', p)
if errores:
    print(f'{len(errores)} error(es):')
    for e in errores:
        print('  ✗', e)
    sys.exit(1)
print('Todo en orden.')
