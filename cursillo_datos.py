"""SeraWeb · Cursillo de ingreso: LA FUENTE del módulo.

El cursillo no se recorre de principio a fin: cada jueves se carga la
disponibilidad, el fin de semana llega la grilla de la semana siguiente y las
clases se arman según lo que toque. Por eso hay dos cosas:

  · TEMAS, el banco: un tema por id, con su clase para proyectar (si ya
    existe), la teoría en PDF y los ejercicios del libro. Crece a pedido.
  · SEMANAS, el horario: una entrada por semana (identificada por su lunes),
    con SOLO las clases de Juan. Nunca los nombres de otros docentes.

`build.py` arma `cursillo/index.html` con `cursillo_generar.py`. El
verificador es `verificacion/cursillo.py`.
"""

# El grupo se escribe como en la grilla: 'POLI INT 3' = Politécnica, intensivo 3.
INSTITUCIONES = {
    'POLI': 'Politécnica',
    'FIUNA': 'FIUNA',
    'FCQ': 'FCQ',
    'CT': 'Colegios Técnicos',
    'UPTP': 'UPTP',
}
MODALIDADES = {'INT': 'intensivo', 'EXT': 'extensivo'}

TURNOS = {
    'TM': ('Mañana', '8:00 a 12:00'),
    'TT': ('Tarde', '14:00 a 18:00'),
}

DIAS = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab']

# ══════════════════════════════════════════════════════════════════
#  El banco de temas
#  'clase':      'cursillo/clases/<id>.html' cuando exista, si no None
#  'teoria':     [('Título', 'cursillo/pdf/teoria/<archivo>.pdf'), …]
#  'ejercicios': [('Libro', 'dónde', 'cursillo/pdf/libro/<archivo>.pdf' o None), …]
# ══════════════════════════════════════════════════════════════════
TEMAS = {
    'operaciones': {
        'titulo': 'Operaciones fundamentales',
        'materia': 'Matemática 1', 'bloque': 'Aritmética',
        'clase': None, 'teoria': [],
        'ejercicios': [('Matemáticas esenciales', 'Capítulo 1', None)],
    },
    'divisibilidad': {
        'titulo': 'Divisibilidad',
        'materia': 'Matemática 1', 'bloque': 'Aritmética',
        'clase': None, 'teoria': [],
        'ejercicios': [('Matemáticas esenciales', 'Capítulo 1', None)],
    },
    'sistema-metrico': {
        'titulo': 'Sistema métrico decimal',
        'materia': 'Matemática 1', 'bloque': 'Aritmética',
        'clase': None, 'teoria': [], 'ejercicios': [],
    },
    'vectores': {
        'titulo': 'Vectores',
        'materia': 'Analítica', 'bloque': 'Geometría analítica',
        'clase': None, 'teoria': [],
        'ejercicios': [('Ejercitario Principia', 'Capítulo 2', None)],
    },
}

# ══════════════════════════════════════════════════════════════════
#  El horario: solo las clases de Juan
#  dia: lun mar mie jue vie sab · turno: TM o TT
#  consigna: tal como la manda la coordinación · temas: ids del banco
# ══════════════════════════════════════════════════════════════════
SEMANAS = [
    {'lunes': '2026-11-23', 'clases': [
        {'dia': 'mar', 'turno': 'TM', 'grupo': 'POLI INT 3', 'materia': 'Matemática 1',
         'consigna': 'Teoría de Sistema Métrico Decimal. Ejemplos.',
         'temas': ['sistema-metrico']},
        {'dia': 'mie', 'turno': 'TM', 'grupo': 'POLI INT 4', 'materia': 'Matemática 1',
         'consigna': 'Ejercicios de Sistema métrico decimal. Completar pendientes de aritmética.',
         'temas': ['sistema-metrico']},
        {'dia': 'mie', 'turno': 'TT', 'grupo': 'POLI INT 8', 'materia': 'Matemática 1',
         'consigna': 'Teoría de Operaciones fundamentales. Ejemplos.',
         'temas': ['operaciones']},
        {'dia': 'jue', 'turno': 'TT', 'grupo': 'POLI INT 1', 'materia': 'Matemática 1',
         'consigna': 'Terminar ejercicios pendientes del libro Matemáticas esenciales. '
                     'Teoría de Divisibilidad con ejemplos.',
         'temas': ['divisibilidad']},
        {'dia': 'vie', 'turno': 'TM', 'grupo': 'POLI EXT 3', 'materia': 'Analítica',
         'consigna': 'Ejercitario Principia, Capítulo 2: Vectores.',
         'temas': ['vectores']},
    ]},
]
