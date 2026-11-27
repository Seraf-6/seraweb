#!/usr/bin/env python3
"""Las cuentas de la pantalla de acceso (assets/acceso.js).

    python herramientas/clave.py                  lista las cuentas
    python herramientas/clave.py docente          crea la cuenta o le cambia la contraseña
    python herramientas/clave.py --quitar alumnos quita una cuenta
    python herramientas/clave.py poli-int-1 --alcance cursillo
                                                  una cuenta que solo ve las clases del
                                                  cursillo (ALCANCES en acceso.js);
                                                  --alcance ninguno se lo saca

Al cambiar la contraseña, la cuenta conserva su alcance.

La contraseña se pide sin mostrarla y no se guarda en ningún lado: en
acceso.js queda solo su huella, con una sal nueva cada vez. Después de
cambiarla, commit y push de assets/acceso.js; las computadoras que la
tenían recordada vuelven a pedirla.

Recordatorio: esto desalienta, no protege. El contenido del sitio está en
el HTML de un repositorio público.
"""
import getpass
import hashlib
import json
import re
import secrets
import sys
from pathlib import Path

ARCHIVO = Path(__file__).resolve().parent.parent / 'assets' / 'acceso.js'
BLOQUE = re.compile(r'(/\* CUENTAS:inicio \*/\n)(.*?)(\n\s*/\* CUENTAS:fin \*/)', re.S)
MINIMO = 10


def huella(usuario, clave, sal, vueltas):
    """La misma cuenta que huella() en acceso.js."""
    h = hashlib.sha256(f'{sal}|{usuario}|{clave}'.encode('utf-8')).digest()
    for _ in range(vueltas - 1):
        h = hashlib.sha256(h).digest()
    return h.hex()


def lee():
    texto = ARCHIVO.read_text(encoding='utf-8')
    m = BLOQUE.search(texto)
    if not m:
        sys.exit('No encuentro el bloque CUENTAS en assets/acceso.js.')
    vueltas = int(re.search(r'VUELTAS = (\d+);', m.group(2)).group(1))
    cuentas = json.loads(re.search(r'CUENTAS = (\{.*\});', m.group(2), re.S).group(1))
    return texto, m, vueltas, cuentas


def escribe(texto, m, vueltas, cuentas):
    filas = ',\n'.join(f'    {json.dumps(u)}: {json.dumps(v)}' for u, v in sorted(cuentas.items()))
    cuerpo = (f'  var VUELTAS = {vueltas};\n'
              f'  var CUENTAS = {{\n{filas}\n  }};')
    ARCHIVO.write_text(texto[:m.start(2)] + cuerpo + texto[m.end(2):], encoding='utf-8')


def main(args):
    texto, m, vueltas, cuentas = lee()
    if not args:
        print('Cuentas:', ', '.join(u + (f' (solo {v[2]})' if len(v) > 2 else '')
                                    for u, v in sorted(cuentas.items())) or '(ninguna)')
        return
    alcance = None
    if '--alcance' in args:
        i = args.index('--alcance')
        if i + 1 >= len(args):
            sys.exit('Uso: clave.py <usuario> --alcance <cursillo|ninguno>')
        alcance = args[i + 1]
        args = args[:i] + args[i + 2:]
        if alcance != 'ninguno' and not re.search(r'\b%s\s*:' % re.escape(alcance), texto):
            sys.exit(f'No hay un alcance «{alcance}» en ALCANCES de assets/acceso.js.')
    if args[0] == '--quitar':
        if len(args) != 2 or args[1] not in cuentas:
            sys.exit('Uso: clave.py --quitar <usuario existente>')
        if len(cuentas) == 1:
            sys.exit('Es la única cuenta: si la quito, nadie puede entrar.')
        del cuentas[args[1]]
        escribe(texto, m, vueltas, cuentas)
        print(f'Quité la cuenta {args[1]}.')
        return
    usuario = args[0].strip().lower()
    if not re.fullmatch(r'[a-z0-9._-]{2,32}', usuario):
        sys.exit('El usuario va en minúsculas, sin espacios ni tildes (letras, números, . _ -).')
    clave = getpass.getpass(f'Contraseña nueva para {usuario}: ')
    if len(clave) < MINIMO:
        sys.exit(f'Muy corta: que tenga al menos {MINIMO} caracteres. Una frase sirve.')
    if getpass.getpass('Otra vez: ') != clave:
        sys.exit('No coinciden. No cambié nada.')
    nueva = usuario not in cuentas
    if alcance is None and not nueva and len(cuentas[usuario]) > 2:
        alcance = cuentas[usuario][2]          # cambiar la contraseña no le saca el alcance
    sal = secrets.token_hex(8)
    cuentas[usuario] = [sal, huella(usuario, clave, sal, vueltas)] + (
        [alcance] if alcance and alcance != 'ninguno' else [])
    escribe(texto, m, vueltas, cuentas)
    print(f'Listo: {usuario} {"creada" if nueva else "con contraseña nueva"}. '
          'Ahora commit y push de assets/acceso.js.')


if __name__ == '__main__':
    main(sys.argv[1:])
