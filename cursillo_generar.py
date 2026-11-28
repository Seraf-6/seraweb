"""SeraWeb · Cursillo: genera cursillo/index.html desde cursillo_datos.py.

Lo llama build.py, que le pasa su plantilla (`pagina`, `barra`, `pie`) para
que la página tenga la misma barra, el mismo pie, Proyección y Timer.

Arriba van las semanas, cada una plegable: un guion chico pliega las que ya
pasaron, deja abiertas la de hoy y las que vienen, marca el día y avisa los
jueves. Una semana sin clases es una grilla que todavía no llegó. Abajo, el
banco de temas. Sin JavaScript quedan abiertas la última semana con clases y
las siguientes.
"""
import datetime as dt
import html

from cursillo_datos import INSTITUCIONES, MODALIDADES, TURNOS, DIAS, TEMAS, SEMANAS

NOMBRE_DIA = {'lun': 'Lunes', 'mar': 'Martes', 'mie': 'Miércoles',
              'jue': 'Jueves', 'vie': 'Viernes', 'sab': 'Sábado'}
DIA_CORTO = {'lun': 'lun', 'mar': 'mar', 'mie': 'mié', 'jue': 'jue', 'vie': 'vie', 'sab': 'sáb'}
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']

e = html.escape


def fecha(semana, dia):
    return dt.date.fromisoformat(semana['lunes']) + dt.timedelta(days=DIAS.index(dia))


def corta(d):
    return f'{d.day}/{d.month}'


def institucion(grupo):
    return grupo.split()[0]


def nombre_grupo(grupo):
    """'POLI INT 3' → 'Politécnica · intensivo 3' (para el title)."""
    partes = grupo.split()
    if len(partes) == 3 and partes[0] in INSTITUCIONES and partes[1] in MODALIDADES:
        return f'{INSTITUCIONES[partes[0]]} · {MODALIDADES[partes[1]]} {partes[2]}'
    return grupo


def rotulo_semana(s):
    lun = dt.date.fromisoformat(s['lunes'])
    sab = lun + dt.timedelta(days=5)
    if lun.month == sab.month:
        return f'Semana del {lun.day} al {sab.day} de {MESES[sab.month - 1]}'
    return f'Semana del {lun.day} de {MESES[lun.month - 1]} al {sab.day} de {MESES[sab.month - 1]}'


def material_tema(tid, sube):
    """Los enlaces de un tema: clase, teoría, ejercicios."""
    t = TEMAS[tid]
    out = []
    if t.get('clase'):
        out.append(f'<a class="cur-mat clase" href="{sube}{e(t["clase"])}">Clase</a>')
    else:
        out.append('<span class="cur-mat por-hacer">Clase por hacer</span>')
    for titulo, url in t.get('teoria', []):
        out.append(f'<a class="cur-mat teoria" href="{sube}{e(url)}">Teoría · {e(titulo)}</a>')
    for libro, donde, url in t.get('ejercicios', []):
        texto = f'{e(libro)} · {e(donde)}'
        out.append(f'<a class="cur-mat ejer" href="{sube}{e(url)}">{texto}</a>' if url
                   else f'<span class="cur-mat ejer">{texto}</span>')
    return ''.join(out)


def tarjeta_clase(c, sube):
    inst = institucion(c['grupo']).lower()
    temas = ''.join(
        f'<div class="cur-tema"><a class="cur-tema-nom" href="#tema-{tid}">{e(TEMAS[tid]["titulo"])}</a>'
        f'<div class="cur-mats">{material_tema(tid, sube)}</div></div>'
        for tid in c.get('temas', []))
    return f"""<article class="cur-clase">
          <div class="cur-cab"><span class="cur-grupo inst-{inst}" title="{e(nombre_grupo(c['grupo']))}">{e(c['grupo'])}</span>
            <span class="cur-materia">{e(c['materia'])}</span></div>
          <p class="cur-consigna">{e(c['consigna'])}</p>{temas}
        </article>"""


def semana_html(s, abierta, sube):
    """Una semana, plegable: el rótulo y el resumen en el <summary>, la grilla adentro.
    Una semana sin clases es una grilla que todavía no llegó: cada turno dice «por llegar»."""
    por = {(c['dia'], c['turno']): c for c in s['clases']}
    espera = not s['clases']
    vacio = '<span class="cur-libre">por llegar</span>' if espera else '<span class="cur-libre">libre</span>'
    dias = []
    for d in DIAS:
        f = fecha(s, d)
        celdas = []
        for tid, (tnom, thoras) in TURNOS.items():
            c = por.get((d, tid))
            cuerpo = tarjeta_clase(c, sube) if c else vacio
            celdas.append(f"""<div class="cur-turno{'' if c else ' vacio'}">
        <span class="cur-turno-nom">{tnom} <small>{thoras}</small></span>
        {cuerpo}
      </div>""")
        libre = not espera and not any((d, t) in por for t in TURNOS)
        dias.append(f"""<div class="cur-dia{' libre' if libre else ''}" data-fecha="{f.isoformat()}">
      <h3><span>{NOMBRE_DIA[d]}</span> <small>{corta(f)}</small></h3>
      {''.join(celdas)}
    </div>""")
    n = len(s['clases'])
    resumen = 'la grilla todavía no llegó' if espera else f'{n} clase{"" if n == 1 else "s"}'
    return f"""<details class="cur-sem{' espera' if espera else ''}" data-lunes="{s['lunes']}"{' open' if abierta else ''}>
  <summary><h2>{e(rotulo_semana(s))}</h2><span class="cur-sem-cual"></span><span class="cur-sem-res">{resumen}</span></summary>
  <div class="cur-semana">
    {''.join(dias)}
  </div>
</details>"""


def se_dio(tid):
    """Dónde y cuándo se dio un tema, cruzando SEMANAS."""
    out = []
    for s in SEMANAS:
        for c in sorted(s['clases'], key=lambda c: (DIAS.index(c['dia']), c['turno'])):
            if tid in c.get('temas', []):
                out.append(f'{c["grupo"]} · {DIA_CORTO[c["dia"]]} {corta(fecha(s, c["dia"]))}')
    return out


def banco(sube):
    grupos = {}
    for tid, t in TEMAS.items():
        grupos.setdefault(t['materia'], {}).setdefault(t['bloque'], []).append(tid)
    out = []
    for materia, bloques in grupos.items():
        out.append(f'<h3 class="cur-banco-materia">{e(materia)}</h3>')
        for bloque, tids in bloques.items():
            out.append(f'<p class="eyebrow">{e(bloque)}</p><div class="tarjetas">')
            for tid in tids:
                t = TEMAS[tid]
                dado = se_dio(tid)
                et = ('<span class="etiqueta diapo-et">Clase lista</span>' if t.get('clase')
                      else '<span class="etiqueta pend">Clase por hacer</span>')
                dado_html = (f'<p class="cur-dado">Se dio en: {e(" / ".join(dado))}</p>'
                             if dado else '')
                if t.get('fuente'):
                    dado_html = f'<p class="cur-dado">Sale de: {e(t["fuente"])}</p>' + dado_html
                out.append(f"""<div class="tarjeta cur-tarjeta{'' if t.get('clase') else ' sin-clase'}" id="tema-{tid}">
      {et}<h3>{e(t['titulo'])}</h3>
      <div class="cur-mats">{material_tema(tid, sube)}</div>{dado_html}
    </div>""")
            out.append('</div>')
    return '\n'.join(out)


GUION = r"""<script>
(function () {
  var semanas = [].slice.call(document.querySelectorAll('.cur-sem'));
  if (!semanas.length) return;
  function lee(iso) { var p = iso.split('-'); return new Date(+p[0], p[1] - 1, +p[2]); }
  function iso(d) {
    return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  }
  function mas(d, n) { return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n); }
  var q = /[?&]hoy=(\d{4}-\d\d-\d\d)/.exec(location.search);
  var hoy = q ? lee(q[1]) : new Date(); hoy = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
  var dow = hoy.getDay();                          // 0 domingo … 6 sábado
  var lunesHoy = mas(hoy, dow === 0 ? -6 : 1 - dow);
  var objetivo = dow === 0 ? mas(lunesHoy, 7) : lunesHoy;   // el domingo ya mira la que viene
  var lunes = semanas.map(function (s) { return s.getAttribute('data-lunes'); });
  // las que ya pasaron, plegadas; la de ahora y las que vienen, abiertas
  var ahora = iso(objetivo), siguiente = iso(mas(objetivo, 7));
  semanas.forEach(function (s, k) {
    var l = lunes[k], cual = s.querySelector('.cur-sem-cual');
    s.open = l >= ahora;
    s.classList.toggle('pasada', l < ahora);
    cual.textContent = l < ahora ? 'ya pasó' : l === ahora ? (dow === 0 ? 'la que viene' : 'esta semana')
                     : l === siguiente ? 'la que viene' : '';
    cual.hidden = !cual.textContent;
  });
  var d = document.querySelector('.cur-dia[data-fecha="' + iso(hoy) + '"]');
  if (d) d.classList.add('hoy');
  // jueves: cargar la disponibilidad; viernes y sábado: ¿llegó la grilla?
  var prox = mas(lunesHoy, 7), aviso = document.getElementById('cur-aviso');
  var meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto',
               'septiembre','octubre','noviembre','diciembre'];
  var cual = prox.getDate() + ' de ' + meses[prox.getMonth()];
  var k = lunes.indexOf(iso(prox));                  // una semana sin clases todavía no está cargada
  var cargada = k >= 0 && !semanas[k].classList.contains('espera');
  if (dow === 4) aviso.innerHTML = '<strong>Hoy es jueves:</strong> cargá la disponibilidad para la semana del ' + cual + '.';
  else if ((dow === 5 || dow === 6) && !cargada)
    aviso.innerHTML = '<strong>Falta la grilla</strong> de la semana del ' + cual + ': cuando llegue, se carga en cursillo_datos.py.';
  aviso.hidden = !aviso.innerHTML;
})();
</script>"""


def pagina_cursillo(pagina, barra, pie):
    sube = '../'
    orden = sorted(SEMANAS, key=lambda s: s['lunes'])
    cuerpo = [barra(1, [('Cursillo', None)])]
    cuerpo.append('<div class="envoltura ancha">')
    cuerpo.append("""<header class="portada cur-portada">
  <p class="sello">Ingreso a la facultad</p>
  <h1>Cursillo</h1>
  <p class="bajada">La semana de clases y, debajo, los temas: cada uno con su clase para
    proyectar, la teoría y los ejercicios del libro.</p>
</header>""")
    # sin JavaScript: abiertas la última semana con clases y las que vienen después
    con_clases = [s['lunes'] for s in orden if s['clases']]
    desde = con_clases[-1] if con_clases else ''
    semanas = ''.join(semana_html(s, s['lunes'] >= desde, sube) for s in orden) \
        or '<p>Todavía no hay semanas cargadas.</p>'
    cuerpo.append(f"""<section class="bloque" id="semana">
  <p class="eyebrow">Mi semana</p>
  <div class="aviso" id="cur-aviso" hidden></div>
  {semanas}
</section>""")
    cuerpo.append(f"""<section class="bloque" id="temas">
  <p class="eyebrow">El banco</p>
  <h2>Los temas</h2>
  <p>No van en orden de programa: se suman a medida que hace falta darlos.</p>
  {banco(sube)}
</section>""")
    cuerpo.append('</div>')
    cuerpo.append(pie(1))
    cuerpo.append(GUION)
    return pagina('Cursillo', '\n'.join(cuerpo), prof=1, css_extra=('assets/cursillo.css',),
                  descripcion='Cursillo de ingreso: la semana de clases y los temas, '
                              'con sus clases para proyectar.')


def pagina_alumnos(pagina):
    """La portada de los alumnos del cursillo: cursillo/alumnos/index.html.

    Es adonde llega una cuenta con alcance «cursillo» (ver ALCANCES en
    assets/acceso.js): las clases del banco que ya tienen página, y nada
    más. Sin la barra del sitio, sin la semana ni otros enlaces: de acá solo
    se va a una clase, y de una clase solo se vuelve acá."""
    sube = '../../'
    tarjetas = []
    for tid, t in TEMAS.items():
        if not t.get('clase'):
            continue
        tarjetas.append(
            f'<a class="tarjeta" href="{sube}{e(t["clase"])}">'
            f'<span class="rotulo">{e(t["materia"])} · {e(t["bloque"])}</span>'
            f'<h3>{e(t["titulo"])}</h3><p>{e(t["fuente"])}</p></a>')
    cuerpo = f"""<div class="envoltura ancha">
<header class="portada">
  <p class="sello">Cursillo de ingreso</p>
  <h1>Los materiales de clase</h1>
  <p class="bajada">Las clases que se proyectan en el cursillo, para repasarlas en casa.
    Material de teoría y ejercicios recopilado por Lic. Juan Serafini.</p>
</header>
<section class="bloque">
  <p class="eyebrow">Las clases</p>
  <h2>Elegí una</h2>
  <div class="tarjetas">
    {''.join(tarjetas)}
  </div>
</section>
<p class="alu-salir"><button class="boton" type="button" onclick="AESAcceso.salir()">Salir</button></p>
</div>
<style>.alu-salir{{margin:28px 0 40px}}
.alu-salir button{{font:inherit; font-weight:700; padding:9px 18px; border:1px solid var(--linea-fuerte); border-radius:6px; background:var(--papel-2); color:var(--tinta); cursor:pointer}}
.alu-salir button:hover{{border-color:var(--acento)}}</style>"""
    return pagina('Cursillo · materiales', cuerpo, prof=2,
                  descripcion='Los materiales de clase del cursillo de ingreso.')
