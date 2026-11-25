/* ═══════════════════════════════════════════════════════════════
   SeraWeb · la pizarra: el motor de las páginas de clase

   Una página de clase trae solo sus datos (los temas, los ejemplos, las
   preguntas del observador, las notas) y llama a Pizarra.unidad(). Todo
   lo demás vive acá y es igual en todas las clases:

   - la notación: I(), M(), Q(), N(), A(), P() y convierte();
   - las fracciones exactas y el plano cartesiano;
   - la pizarra de cada ejemplo, sus botones y su movimiento;
   - el armado de la unidad: concepto, ejemplos, taller, ficha, desafío,
     el navegador y lo que necesitan los botones de assets/clase.js.

   La pizarra es como en los videos de Khan Academy: a la izquierda el
   enunciado, lo que queda fijo y lo que se dice en este paso, que se
   borra y se reescribe en el mismo lugar; a la derecha, grande, lo que se
   va acumulando: el cuaderno con la resolución, o el plano. Nada empuja
   nada: cambia solo lo que tiene que cambiar.

   Se carga sin defer, antes del guion de la página:
     <script src="../../assets/pizarra.js"></script>
   ═══════════════════════════════════════════════════════════════ */

/* ═══ la notación ═══
   M() pone en cursiva las letras sueltas y envuelve en .ec; Q() arma una
   fracción apilada, como las del libro. Las letras son x, y, a, b, c, d;
   una página que use otras las cambia antes de escribir sus datos:
     Pizarra.letras = /[xyn]/g;
   M() e I() se usan solo con matemática pura: en "1 y 13" la y es una
   palabra, y quedaría en cursiva. */
const Pizarra = { letras:/[xyabcd]/g, lienzos:{} };
window.Pizarra = Pizarra;

/* La raíz como en el pizarrón: la raya de arriba cubre todo lo de adentro.
   Se escribe √25, √(x^2), 3√3, √(9 · 3), y acá se convierte. Lo de adentro
   es lo que está entre los paréntesis (que se sacan), o un número, o una
   letra. El signo lo dibuja clase.css, así que el resultado ya no tiene
   ningún √ y pasarlo dos veces no cambia nada. */
function raices(s){
  s = String(s);
  let out = '', i = 0;
  while (i < s.length){
    const j = s.indexOf('√', i);
    if (j < 0){ out += s.slice(i); break; }
    out += s.slice(i, j);
    // adentro de una etiqueta (un aria-label) no se toca
    if (s.lastIndexOf('<', j) > s.lastIndexOf('>', j)){ out += '√'; i = j + 1; continue; }
    let k = j + 1, rad = null;
    if (s[k] === '('){
      let prof = 0, m = k;
      for (; m < s.length; m++){
        if (s[m] === '<'){ m = s.indexOf('>', m); if (m < 0) break; continue; }
        if (s[m] === '(') prof++;
        else if (s[m] === ')' && !--prof) break;
      }
      if (m > 0 && m < s.length){ rad = s.slice(k + 1, m); k = m + 1; }
    } else {
      const t = /^(?:\d+(?:,\d+)?|<i>[^<]<\/i>|[a-zA-Zℓ])(?:<sup>[^<]*<\/sup>)?/.exec(s.slice(k));
      if (t){ rad = t[0]; k += t[0].length; }
    }
    if (rad === null){ out += '√'; i = j + 1; continue; }
    out += `<span class="raiz"><span class="raiz-r">${rad}</span></span>`;
    i = k;
  }
  return out;
}

/* Un exponente se puede escribir con ^: 'x^2 + 5x + 6', '(a + b)^3', 'x^n'.
   Un exponente de varios términos va entre paréntesis, que no se dibujan:
   '3^(m + 3)', '6^(3 − a)'. */
const I = s => raices(String(s).replace(/\^\(([^()]*)\)/g, '<sup>$1</sup>')
  .replace(/\^(\d+|[a-z])/g, '<sup>$1</sup>').split(/(<[^>]+>)/)
  .map(t => t.startsWith('<') ? t : t.replace(Pizarra.letras, '<i>$&</i>')).join(''));
const M = s => '<span class="ec">' + I(s) + '</span>';
const Q = (n, d) => `<span class="fr"><span>${I(String(n))}</span><span>${I(String(d))}</span></span>`;

/* S() escribe un sistema de ecuaciones, una debajo de la otra, con su llave. */
const S = (...ecs) => `<span class="sistema"><span class="llave">{</span><span class="sis-ecs">${ecs.map(M).join('')}</span></span>`;

/* Los ángulos con sombrero (Â, B̂, Ĉ, D̂): B̂ y D̂ no existen como una sola
   letra, y en cursiva el sombrero se corre. Se escriben como siempre y acá
   se dibujan todos igual (.ang, en clase.css). El nombre entero (AÔB) va
   en un .ang-nom, que no se corta entre dos renglones. No va dentro de un SVG. */
const sombrero = s => raices(s).replace(/([A-Z]?)(?:([A-Z])̂|([ÂÊÎÔÛĈĜĤĴŜŴŶ]))([A-Z]?)/g,
  (m, a, l, pre, b) => `<span class="ang-nom">${a}<span class="ang">${l || pre.normalize('NFD')[0]}</span>${b}</span>`);

/* N() resalta lo nuevo: lo que se agrega a los dos miembros, el valor que
   se reemplaza, la palabra que cambió respecto del ejemplo anterior. Va
   siempre adentro de M(), de A() o de un .ec: no pone cursivas. */
const N = s => `<span class="nuevo">${s}</span>`;

/* tacha() tacha un factor que se simplifica, como en el pizarrón: el mismo
   factor arriba y abajo, cada uno con su raya. Va adentro de M(), A(), P()
   o Q(). En el cuaderno la raya se dibuja después de escribir el renglón,
   cuando ya se leyó lo que se tacha. */
const tacha = s => `<span class="tacha">${s}</span>`;

/* A() alinea una cadena de igualdades: una por renglón y todos los signos
   = en la misma columna, como en el cuaderno. Cada fila es una igualdad
   ('3(1 + 2) = 3 · 1 + 6'), una continuación (' = 9'), o un par
   ['rótulo', '3(1 + 2) = 9'] con un rótulo a la izquierda ("izquierda",
   "con x = 1"). También alinea ≠ (cuando los dos miembros no coinciden),
   ≈ (una aproximación, después del valor exacto), < y >.
   El rótulo es texto: no pasa por I(). */
function celdas(f, n, cls = '', extra = ''){
  const [rot, e] = Array.isArray(f) ? f : ['', f];
  const m = / (=|≠|≈|<|>) /.exec(' ' + e);
  const izq = m ? e.slice(0, Math.max(0, m.index - 1)) : '';
  const sig = m ? m[1] : '';
  const der = m ? e.slice(m.index + m[0].length - 1) : e;
  const at = k => ` class="${k}${cls ? ' ' + cls : ''}" style="--f:${n}"${extra}`;
  return sombrero(`<span${at('al-rot')}>${rot}</span><span${at('al-izq')}>${I(izq)}</span>` +
         `<span${at('al-sig')}>${{ '<':'&lt;', '>':'&gt;' }[sig] || sig}</span><span${at('al-der')}>${I(der)}</span>`);
}
function A(...filas){
  return '<div class="alineado">' + filas.map((f, n) => celdas(f, n)).join('') + '</div>';
}

/* P() es un paso que escribe en el cuaderno: a la izquierda queda solo lo
   que se dice ("Sumo 5 a los dos miembros"), y los renglones van al
   cuaderno de la derecha, alineados con todo lo anterior.
     P('Sumo 5 a los dos miembros.', `6x − 5 ${N('+ 5')} = 25 ${N('+ 5')}`, '6x = 30')
   Un paso que es solo un texto se da como texto, sin P(). */
const P = (t, ...q) => ({ t, q });

/* convierte() escribe un cambio de unidad con factores unitarios, como en
   el pizarrón: la medida, por una o más fracciones que valen 1 (arriba la
   unidad que se quiere, abajo la que se saca), igual a la medida nueva. Las
   unidades que se simplifican se tachan solas.
     convierte('3,75 km', ['1.000 m', '1 km'], '3.750 m')
     convierte('0,35 m³', ['1.000 dm³', '1 m³'], ['1 L', '1 dm³'], '350 L')
   Cada medida es un número (3, 2,5, 1.000 o 3/4) y su unidad, separados por
   un espacio. Devuelve un renglón con un solo =, para P() o A(). El
   verificador de la página lee cada llamada y rehace la cuenta. */
function convierte(...args){
  const res = args.pop(), cant = args.shift(), facs = args;
  const parte = s => { const k = s.indexOf(' '); return { n:s.slice(0, k), u:s.slice(k + 1) }; };
  const arriba = [parte(cant), ...facs.map(f => parte(f[0]))];
  const abajo = facs.map(f => parte(f[1]));
  abajo.forEach(d => {
    const a = arriba.find(x => !x.fuera && x.u === d.u);
    if (a) a.fuera = d.fuera = true;
  });
  const num = n => { const m = /^(\d+)\/(\d+)$/.exec(n); return m ? Q(m[1], m[2]) : n; };
  const med = x => `${num(x.n)} ${x.fuera ? tacha(x.u) : x.u}`;
  return `${med(arriba[0])} · ${abajo.map((d, i) => Q(med(arriba[i + 1]), med(d))).join(' · ')} = ${res}`;
}

/* ═══ fracciones exactas ═══
   Nada de decimales: una ecuación con enteros puede dar 16/5, y
   escribirlo redondeado sería perder exactitud sin necesidad. */
const mcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b){ [a, b] = [b, a % b]; } return a || 1; };
function fr(n, d = 1){
  if (d === 0) return null;
  if (d < 0){ n = -n; d = -d; }
  const g = mcd(n, d);
  return { n: n / g, d: d / g };
}
const suma  = (p, q) => fr(p.n * q.d + q.n * p.d, p.d * q.d);
const resta = (p, q) => fr(p.n * q.d - q.n * p.d, p.d * q.d);
const prod  = (p, q) => fr(p.n * q.n, p.d * q.d);
const coc   = (p, q) => (q.n === 0 ? null : fr(p.n * q.d, p.d * q.n));
const cero  = p => p.n === 0;
const igual = (p, q) => p.n === q.n && p.d === q.d;
const valor = p => p.n / p.d;

/* el signo va adelante, como en todo el material de la casa */
function txt(p){
  const s = p.n < 0 ? '−' : '';
  const a = Math.abs(p.n);
  return p.d === 1 ? s + a : s + Q(a, p.d);
}
/* dentro de un SVG no hay HTML: la fracción va con barra */
function txtPlano(p){
  const s = p.n < 0 ? '−' : '';
  return p.d === 1 ? s + Math.abs(p.n) : s + Math.abs(p.n) + '/' + p.d;
}

/* lee 3, −5, 3/2, 2x, −x */
function lee(bruto){
  let t = String(bruto).trim().replace(/−/g, '-').replace(/\s+/g, '');
  const esx = /x$/i.test(t);
  if (esx) t = t.slice(0, -1);
  if (t === '' || t === '+') t = '1';
  if (t === '-') t = '-1';
  const m = t.match(/^(-?\d+)\/(\d+)$/);
  if (m) return { f:fr(Number(m[1]), Number(m[2])), esx };
  if (/^-?\d+$/.test(t)) return { f:fr(Number(t)), esx };
  return null;
}
/* un número: 3, −2, 1/2 y también 2,5 */
function leeNumero(bruto){
  const r = lee(bruto);
  if (r && !r.esx) return r.f;
  const m = String(bruto).trim().replace(/−/g, '-').match(/^(-?)(\d+)[.,](\d+)$/);
  if (!m) return null;
  const den = Math.pow(10, m[3].length);
  const num = Number(m[2]) * den + Number(m[3]);
  return fr(m[1] ? -num : num, den);
}

/* un miembro de una ecuación: a·x + b */
function lado(a, b){
  if (cero(a)) return txt(b);
  let s;
  if (igual(a, fr(1))) s = '<i>x</i>';
  else if (igual(a, fr(-1))) s = '−<i>x</i>';
  else s = txt(a) + '<i>x</i>';
  if (cero(b)) return s;
  return s + (b.n > 0 ? ' + ' + txt(b) : ' − ' + txt(fr(-b.n, b.d)));
}
const ecuacion = e => lado(e.a, e.b) + ' = ' + lado(e.c, e.d);

/* ═══ el plano cartesiano ═══
   Una recta y = ax + b recortada al recuadro, con sus puntos rotulados.
   op, para animar: pop = [[índice, retraso]] de los puntos que caen;
   guia = índice del punto con sus guías (animaGuia: si suben ahora);
   dibujaRecta = si la recta se traza sola, desde retrasoRecta. Con
   anterior = {a, b}, la recta de antes queda en punteado. */
function lienzoRecta(a, b, puntos, R = 8, tam = 400, destacado = 2, conRecta = true, anterior = null, op = {}){
  const M_ = 22, U = (tam - 2 * M_) / (2 * R);
  const px = u => M_ + (u + R) * U;
  const py = v => M_ + (R - v) * U;
  let g = '';
  for (let i = -R; i <= R; i++){
    const cls = (i % 4 === 0) ? 'grilla-fuerte' : 'grilla';
    g += `<line class="${cls}" x1="${px(i)}" y1="${py(-R)}" x2="${px(i)}" y2="${py(R)}"/>`;
    g += `<line class="${cls}" x1="${px(-R)}" y1="${py(i)}" x2="${px(R)}" y2="${py(i)}"/>`;
  }
  g += `<line class="eje" x1="${px(-R)}" y1="${py(0)}" x2="${px(R)}" y2="${py(0)}"/>`;
  g += `<line class="eje" x1="${px(0)}" y1="${py(-R)}" x2="${px(0)}" y2="${py(R)}"/>`;
  for (let i = -R; i <= R; i += 2){
    if (i === 0) continue;
    g += `<text class="rotulo-eje" x="${px(i)}" y="${py(0) + 14}" text-anchor="middle">${i}</text>`;
    g += `<text class="rotulo-eje" x="${px(0) - 6}" y="${py(i) + 4}" text-anchor="end">${i}</text>`;
  }
  const dentro = t => t >= -R - 1e-9 && t <= R + 1e-9;
  const segmento = (av, bv, cls, traza = false) => {
    const pts = [];
    for (const xx of [-R, R]){ const yy = av * xx + bv; if (dentro(yy)) pts.push([xx, yy]); }
    if (av !== 0) for (const yy of [-R, R]){ const xx = (yy - bv) / av; if (dentro(xx)) pts.push([xx, yy]); }
    const u = pts.filter((p, i) => pts.findIndex(q => Math.abs(q[0] - p[0]) < 1e-9 && Math.abs(q[1] - p[1]) < 1e-9) === i);
    if (u.length < 2) return '';
    u.sort((p, q) => p[0] - q[0]);          // se traza desde la izquierda
    const [x1, y1, x2, y2] = [px(u[0][0]), py(u[0][1]), px(u[1][0]), py(u[1][1])];
    const estilo = traza
      ? ` style="--largo:${Math.hypot(x2 - x1, y2 - y1).toFixed(1)}; animation-delay:${op.retrasoRecta || 0}s"` : '';
    return `<line class="${cls}${traza ? ' dibuja' : ''}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"${estilo}/>`;
  };
  if (anterior) g += segmento(valor(anterior.a), valor(anterior.b), 'recta-anterior');
  if (conRecta) g += segmento(valor(a), valor(b), 'recta1', !!op.dibujaRecta);
  // las guías del punto del momento: desde su x en el eje, sube a su altura
  if (op.guia != null && puntos[op.guia]){
    const X = valor(puntos[op.guia][0]), Y = valor(puntos[op.guia][1]);
    if (dentro(X) && dentro(Y)){
      const an = op.animaGuia;
      g += `<line class="guia${an ? ' sube' : ''}" x1="${px(X)}" y1="${py(0)}" x2="${px(X)}" y2="${py(Y)}"
               style="transform-origin:${px(X)}px ${py(0)}px"/>`;
      g += `<line class="guia${an ? ' cruza' : ''}" x1="${px(X)}" y1="${py(Y)}" x2="${px(0)}" y2="${py(Y)}"
               style="transform-origin:${px(X)}px ${py(Y)}px"/>`;
      g += `<circle class="marca-x${an ? ' late' : ''}" cx="${px(X)}" cy="${py(0)}" r="4"
               style="transform-origin:${px(X)}px ${py(0)}px"/>`;
    }
  }
  puntos.forEach((p, i) => {
    const X = valor(p[0]), Y = valor(p[1]);
    if (!dentro(X) || !dentro(Y)) return;
    const cae = (op.pop || []).find(q => q[0] === i);
    const origen = `transform-origin:${px(X)}px ${py(Y)}px`;
    if (cae) g += `<circle class="onda" cx="${px(X)}" cy="${py(Y)}" r="6.5" style="${origen}; animation-delay:${cae[1] + .05}s"/>`;
    g += `<circle class="${i === destacado ? 'punto-control' : 'punto-tabla'}${cae ? ' aparece' : ''}" cx="${px(X)}" cy="${py(Y)}" r="6.5"
             style="${origen}${cae ? `; animation-delay:${cae[1]}s` : ''}"/>`;
    const etiqueta = `(${txtPlano(p[0])}, ${txtPlano(p[1])})`;
    // abajo del eje, el rótulo va abajo del punto: arriba se pisaría con los
    // números del eje; cerca del borde derecho, va a la izquierda
    const yRot = Y < 0 ? py(Y) + 20 : py(Y) - 9;
    const aLaIzq = X > R - 3;
    g += `<text class="rotulo-punto${cae ? ' aparece-rot' : ''}" x="${aLaIzq ? px(X) - 9 : px(X) + 9}" y="${yRot}"${aLaIzq ? ' text-anchor="end"' : ''}${cae ? ` style="animation-delay:${cae[1] + .12}s"` : ''}>${etiqueta}</text>`;
  });
  return g;
}

/* ═══════════════════════════════════════════════════════════════
   La pizarra de un ejemplo
   Un ejemplo es { titulo, enun, prosa?, fija?, inicio?, pasos, final,
   control?, construye? }:
   - pasos: textos o P(); el orden es siempre pasos, respuesta, control;
   - fija: cuántos pasos del principio quedan escritos arriba (la
     pregunta, la incógnita con nombre);
   - inicio: los renglones con que arranca el cuaderno (la ecuación);
   - construye: { a, b, xs, desde, control } si a la derecha va el plano
     en lugar del cuaderno: cada paso desde `desde` agrega un renglón a la
     tabla y un punto al plano, la recta aparece con la respuesta y el
     punto de control con el control;
   - lienzo: { tipo, … } para un dibujo propio de la página, registrado en
     Pizarra.lienzos[tipo] = (clave, ej, k, avanzando, div) => {…}.
   El atributo de los botones NO puede llamarse data-paso: el panel de
   proyección usa ese nombre para cambiar de diapositiva.
   ═══════════════════════════════════════════════════════════════ */
const BLOQUES = {};        // clave → ejemplo
const avance = {};         // clave → cuántos pasos se mostraron

/* El orden es siempre: los pasos, la respuesta, y después el control. El
   control no puede ir antes: controla una respuesta que todavía no está. */
function totalPasos(ej){ return ej.pasos.length + 1 + (ej.control ? 1 : 0); }
const textoPaso = p => typeof p === 'string' ? p : p.t;
const filasPaso = p => typeof p === 'string' ? [] : (p.q || []);
const tieneFilas = ej => !!((ej.inicio && [].concat(ej.inicio).length) || ej.pasos.some(p => filasPaso(p).length));
const usaCuaderno = ej => !ej.construye && !ej.lienzo && tieneFilas(ej);

function navPasos(clave, total){
  return `<div class="pasos-nav abajo" data-nav="${clave}">
      <button class="boton" type="button" data-accion="atras" data-bloque="${clave}" disabled>← Anterior</button>
      <span class="pasos-cuenta">${total} pasos</span>
      <button class="boton" type="button" data-accion="revelar" data-bloque="${clave}">Siguiente →</button>
    </div>`;
}

/* o: { rotulo, cinta, clase ('ejemplo-diapo'), id ('e-clave'), attrs } */
function bloque(clave, ej, o = {}){
  BLOQUES[clave] = ej;
  const derecha = ej.construye || ej.lienzo || usaCuaderno(ej);
  return `
  <section class="${o.clase || 'ejemplo-diapo'} pizarra" id="${o.id || 'e-' + clave}"${o.attrs ? ' ' + o.attrs : ''}>
    ${o.cinta ? `<p class="cinta">${o.cinta}</p>` : ''}
    <div class="ejemplo-cab">
      <h4 class="ej-titulo">${o.rotulo ? `<span class="num">${o.rotulo}</span>` : ''}${sombrero(ej.titulo)}</h4>
    </div>
    <div class="pizarra-grid${derecha ? '' : ' sola'}${ej.prosa && !ej.construye && !ej.lienzo ? ' prosa' : ''}">
      <div class="pizarra-izq">
        <div class="pizarra-cab">
          <div class="enunciado${ej.prosa ? ' frase' : ''}">${sombrero(ej.enun)}</div>
          ${ej.construye ? `<div class="tabla-mini" id="tabla-${clave}"></div>` : ''}
        </div>
        <div class="pizarra-fija" id="fija-${clave}"></div>
        <div class="pizarra-trabajo" id="trabajo-${clave}">${navPasos(clave, totalPasos(ej))}</div>
      </div>
      ${derecha ? `<div class="pizarra-der" id="der-${clave}"></div>` : ''}
    </div>
  </section>`;
}

/* ═══ el movimiento ═══
   Lo que ya está se queda quieto; lo nuevo aparece en su lugar. Con
   "reducir movimiento" en el sistema, nada se anima. */
const movimiento = () => !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const SUAVE = 'cubic-bezier(.22,.8,.24,1)';

/* Lo que ordena la página al terminar una animación (borrar la cuenta
   vieja, soltar un alto fijo) no puede depender solo del aviso de fin: si
   la ventana no está dibujando, ese aviso se demora. Un reloj lo respalda,
   y lo que sea que llegue primero lo hace, una sola vez. */
function alTerminar(anim, ms, fn){
  let hecho = false;
  const una = () => { if (!hecho){ hecho = true; fn(); } };
  anim.onfinish = una;
  setTimeout(una, ms + 80);
}

/* Lleva un elemento a la vista, lo justo y con suavidad, sin dejarlo
   debajo de los botones flotantes. Si la ventana no está dibujando (el
   proyector en otra pantalla) el desplazamiento suave no avanza: a los
   700 ms se corrige de una. */
function llevaAlaVista(el){
  const r = el.getBoundingClientRect();
  const abajo = innerHeight - 90, arriba = 80;
  let delta = 0;
  if (r.bottom > abajo) delta = r.bottom - abajo;
  else if (r.top < arriba) delta = r.top - arriba;
  if (!delta) return;
  const destino = window.scrollY + delta;
  window.scrollTo({ top:destino, behavior: movimiento() ? 'smooth' : 'auto' });
  setTimeout(() => { if (Math.abs(window.scrollY - destino) > 4) window.scrollTo(0, destino); }, 700);
}

/* una caja nueva se abre desde alto cero: no empuja todo de golpe */
function abreCaja(el){
  if (!movimiento() || !el.animate) return;
  const alto = el.getBoundingClientRect().height;
  const cs = getComputedStyle(el);
  el.style.overflow = 'hidden';
  alTerminar(el.animate([
    { height:'0px', paddingTop:'0px', paddingBottom:'0px', opacity:0 },
    { height:alto + 'px', paddingTop:cs.paddingTop, paddingBottom:cs.paddingBottom, opacity:1 }
  ], { duration:420, easing:SUAVE }), 420, () => { el.style.overflow = ''; });
}

/* y se cierra igual, antes de irse */
function cierraCaja(el, listo){
  if (!movimiento() || !el.animate){ listo(); return; }
  const alto = el.getBoundingClientRect().height;
  el.style.overflow = 'hidden';
  alTerminar(el.animate([
    { height:alto + 'px', opacity:1 },
    { height:'0px', paddingTop:'0px', paddingBottom:'0px', marginTop:'0px', opacity:0 }
  ], { duration:320, easing:'cubic-bezier(.4,0,.6,1)', fill:'forwards' }), 320, listo);
}

/* una caja que cambia de alto lo hace despacio */
function acompanaAlto(el, antes){
  const despues = el.getBoundingClientRect().height;
  if (!movimiento() || !el.animate || Math.abs(antes - despues) < 2) return;
  el.style.overflow = 'hidden';
  alTerminar(el.animate([{ height:antes + 'px' }, { height:despues + 'px' }],
               { duration:380, easing:SUAVE }), 380, () => { el.style.overflow = ''; });
}

function actualizaNav(clave){
  const total = totalPasos(BLOQUES[clave]);
  const i = avance[clave] || 0;
  const nav = document.querySelector(`[data-nav="${clave}"]`);
  nav.querySelector('[data-accion="atras"]').disabled = (i === 0);
  nav.querySelector('[data-accion="revelar"]').disabled = (i >= total);
  nav.querySelector('.pasos-cuenta').textContent = i ? `paso ${i} de ${total}` : `${total} pasos`;
}

/* ═══ la izquierda: lo que se dice en este paso ═══
   Si la derecha es un dibujo (el plano, una figura), la cuenta del paso
   va acá, debajo de lo que se dice: abajo del dibujo no entraría. */
function laminaDe(ej, k){
  const s = k - 1;
  if (s < ej.pasos.length){
    const p = ej.pasos[s], filas = filasPaso(p);
    const cuenta = filas.length && (ej.lienzo || ej.construye) ? A(...filas) : '';
    return { cls:'', html:`<div class="t">${textoPaso(p)}${cuenta}</div>` };
  }
  if (s === ej.pasos.length) return { cls:'final', html:`<span class="n">=</span><span class="final-txt">${ej.final}</span>` };
  return { cls:'control', html:`<span class="n">✓</span><div class="t">${ej.control}</div>` };
}

function nuevaLamina(lam){
  const d = document.createElement('div');
  d.className = `lamina ${lam.cls} recien`;
  d.innerHTML = sombrero(lam.html);
  return d;
}

/* la cuenta anterior se borra en su lugar y la nueva se escribe encima */
function cambiaTrabajo(clave, lam){
  const zona = document.getElementById('trabajo-' + clave);
  const nav = zona.querySelector('.pasos-nav');
  const antes = zona.getBoundingClientRect().height;
  zona.querySelectorAll(':scope > .lamina:not(.saliendo)').forEach(v => {
    v.classList.add('saliendo');
    if (!movimiento() || !v.animate){ v.remove(); return; }
    Object.assign(v.style, { position:'absolute', top:v.offsetTop + 'px', left:v.offsetLeft + 'px',
                             width:v.offsetWidth + 'px', margin:'0' });
    alTerminar(v.animate([{ opacity:1 }, { opacity:0, transform:'translateY(-10px)' }],
              { duration:240, easing:'ease-in', fill:'forwards' }), 240, () => v.remove());
  });
  if (lam) zona.insertBefore(nuevaLamina(lam), nav);
  acompanaAlto(zona, antes);
}

/* el control se escribe debajo de la respuesta, que se queda */
function agregaLamina(clave, lam){
  const zona = document.getElementById('trabajo-' + clave);
  const d = nuevaLamina(lam);
  zona.insertBefore(d, zona.querySelector('.pasos-nav'));
  abreCaja(d);
}
function quitaUltimaLamina(clave){
  const vivas = [...document.getElementById('trabajo-' + clave).querySelectorAll(':scope > .lamina:not(.saliendo)')];
  const u = vivas[vivas.length - 1];
  if (!u) return;
  u.classList.add('saliendo');
  cierraCaja(u, () => u.remove());
}

/* ═══ la derecha: lo que se acumula ═══ */

/* El cuaderno: la resolución entera, con todos los = en una columna. Los
   renglones del paso de ahora se escriben de a uno; los de antes quedan,
   un poco más tenues. */
function filasHasta(ej, k){
  const filas = [].concat(ej.inicio || []).map(f => ({ f, paso:0 }));
  ej.pasos.slice(0, Math.min(k, ej.pasos.length))
    .forEach((p, i) => filasPaso(p).forEach(f => filas.push({ f, paso:i + 1 })));
  return filas;
}

/* ¿Algún renglón del cuaderno entero es más ancho que el lugar que tiene
   (₲ 75.000.000 + ₲ 5.000.000 = ₲ 80.000.000)? Se mide de verdad: la
   primera vez que el cuaderno está a la vista, se escriben todos sus
   renglones en una copia invisible. Si la ventana cambia de ancho, se vuelve
   a medir; si no, la letra no cambia a mitad del ejemplo. */
function noEntra(ej, div){
  const w = div.clientWidth;
  if (!w) return false;
  if (div.dataset.medido === String(w)) return div.dataset.noEntra === '1';
  const prueba = document.createElement('div');
  prueba.className = 'cuaderno';
  prueba.style.cssText = `position:absolute; visibility:hidden; left:0; top:0; width:${w}px`;
  prueba.innerHTML = `<div class="alineado">${filasHasta(ej, Infinity).map(({ f }) => celdas(f, 0)).join('')}</div>`;
  div.appendChild(prueba);
  const no = prueba.scrollWidth > prueba.clientWidth + 1;
  prueba.remove();
  div.dataset.medido = w;
  div.dataset.noEntra = no ? '1' : '0';
  return no;
}

function pintaCuaderno(clave, avanzando, borrados = false, div = document.getElementById('der-' + clave)){
  const ej = BLOQUES[clave];
  const k = avance[clave] || 0;
  const filas = filasHasta(ej, k);
  // al volver, los renglones que sobran se borran antes de redibujar
  const sobran = [...div.querySelectorAll('[data-cu]')].filter(s => Number(s.dataset.cu) > k);
  if (!avanzando && !borrados && sobran.length && movimiento() && sobran[0].animate){
    if (div.dataset.borrando) return;
    div.dataset.borrando = '1';
    let ultima;
    sobran.forEach(s => { ultima = s.animate([{ opacity:1 }, { opacity:0 }], { duration:220, fill:'forwards' }); });
    alTerminar(ultima, 220, () => { delete div.dataset.borrando; pintaCuaderno(clave, false, true, div); });
    return;
  }
  const ultimo = filas.length ? filas[filas.length - 1].paso : 0;
  // los renglones que hasta recién eran los últimos se apagan despacio
  const hayNuevas = avanzando && ultimo === k && k > 0;
  const previo = Math.max(-1, ...filas.filter(r => r.paso < ultimo).map(r => r.paso));
  let n = 0;
  const cuerpo = filas.map(({ f, paso }) => {
    const nueva = hayNuevas && paso === k;
    const cls = [nueva ? 'cu-nueva' : '', paso < ultimo ? 'cu-antes' : '',
                 hayNuevas && paso === previo ? 'cu-atenua' : ''].join(' ').trim();
    return celdas(f, nueva ? n++ : 0, cls, ` data-cu="${paso}"`);
  }).join('');
  const antes = div.getBoundingClientRect().height;
  // un cuaderno largo usa letra más chica desde el principio: que entre entero
  // en la pantalla, sin cambiar de tamaño a mitad del ejemplo
  // (un renglón con fracción apilada ocupa casi dos)
  const peso = filasHasta(ej, Infinity).reduce((s, { f }) => s + (/class="fr"/.test([].concat(f).join('')) ? 1.8 : 1), 0);
  const largo = peso > 9 || noEntra(ej, div) ? ' largo' : '';
  div.innerHTML = `<div class="cuaderno${largo}"><span class="cu-rot">${ej.rotCuaderno || 'en el cuaderno'}</span>
      <div class="alineado">${cuerpo}</div></div>`;
  acompanaAlto(div, antes);
}

/* El plano: está vacío al principio; desde el paso `desde`, cada paso
   agrega un renglón a la tabla y un punto al plano; con la respuesta
   aparece la recta, y con el control, el punto que nadie calculó. */
function pintaConstruccion(clave, avanzando = false){
  const ej = BLOQUES[clave], c = ej.construye;
  const k = avance[clave] || 0;
  const a = fr(...c.a), b = fr(...c.b);
  const X = v => Array.isArray(v) ? fr(v[0], v[1]) : fr(v);
  const hechos = Math.max(0, Math.min(c.xs.length, k - c.desde + 1));
  const conRecta = k >= ej.pasos.length + 1;
  const conControl = ej.control && c.control != null && k >= ej.pasos.length + 2;
  const puntos = c.xs.slice(0, hechos).map(v => [X(v), suma(prod(a, X(v)), b)]);
  if (conControl) puntos.push([X(c.control), suma(prod(a, X(c.control)), b)]);
  const ultimo = puntos.length - 1;

  // qué acaba de pasar, para animar solo eso
  const recienPunto = avanzando && !conRecta && hechos > 0 && k - c.desde + 1 === hechos;
  const recienRecta = avanzando && k === ej.pasos.length + 1;
  const recienControl = avanzando && conControl && k === ej.pasos.length + 2;
  const op = {};
  if ((!conRecta && hechos > 0) || conControl){
    op.guia = ultimo;
    op.animaGuia = recienPunto || recienControl;
    if (op.animaGuia) op.pop = [[ultimo, .82]];
  }
  if (recienRecta){ op.dibujaRecta = true; op.retrasoRecta = .1; }

  const filas = puntos.map((p, i) => {
    const cls = [conControl && i === ultimo ? 'control' : '',
                 (recienPunto || recienControl) && i === ultimo ? 'fila-nueva' : ''].join(' ');
    return `<tr class="${cls}"><td>${txt(p[0])}</td><td>${txt(p[1])}</td></tr>`;
  }).join('');
  document.getElementById('tabla-' + clave).innerHTML =
    `<table class="t-mini"><tr><th>x</th><th>y</th></tr>${filas ||
      '<tr class="vacia"><td colspan="2">sin valores</td></tr>'}</table>`;
  document.getElementById('der-' + clave).innerHTML = `<div class="lienzo"><svg viewBox="0 0 400 400" role="img"
      aria-label="El plano cartesiano con los puntos de la tabla">${
      lienzoRecta(a, b, puntos, 8, 400, conControl ? ultimo : -1, conRecta, null, op)}</svg></div>`;
}

function pintaDerecha(clave, avanzando){
  const ej = BLOQUES[clave];
  if (ej.construye) return pintaConstruccion(clave, avanzando);
  const der = document.getElementById('der-' + clave);
  if (!der) return;
  if (ej.lienzo){
    const f = Pizarra.lienzos[ej.lienzo.tipo];
    if (f) f(clave, ej, avance[clave] || 0, avanzando, der);
    return;
  }
  pintaCuaderno(clave, avanzando, false, der);
}

/* ═══ la figura: un dibujo que se arma por capas ═══
   lienzo:{ tipo:'figura', vb:'0 0 400 300', rot:'…', capas:[[en, svg, hasta], …] }
   Cada capa se ve desde el paso `en` (0 es desde el principio; también
   'final' y 'control') hasta antes del paso `hasta`, si lo tiene. La capa
   que aparece en este paso se dibuja: sus trazos (.traza) se hacen de
   punta a punta y sus puntos (.pop) caen con un pulso.
   Una capa con un cuarto elemento { desde:[dx, dy] } no se dibuja: llega
   deslizándose desde ese corrimiento, como una pieza que se mueve a su
   lugar. Sirve también para volver: la pieza que se había ido regresa
   desde donde está la otra.
   Con { gira:[grados, x, y] } llega girando alrededor del punto (x, y):
   arranca girada esos grados (como el rotate de CSS: positivo es el
   sentido del reloj) y vuelve a su lugar. Es el lado de un ángulo que gira
   desde el otro lado, o el opuesto por el vértice que da media vuelta. */
Pizarra.lienzos.figura = (clave, ej, k, avanzando, div) => {
  const nP = ej.pasos.length;
  const num = v => v === 'final' ? nP + 1 : v === 'control' ? nP + 2 : (v == null ? Infinity : v);
  const capas = ej.lienzo.capas.map(([en, svg, hasta, op]) => ({ en:num(en), svg, hasta:num(hasta), op:op || {} }));
  const vis = capas.filter(c => c.en <= k && k < c.hasta);
  const g = c => {
    const llega = avanzando && c.en === k && k > 0;
    const vuelve = !avanzando && c.hasta === k + 1;
    if ((llega || vuelve) && c.op.desde)
      return `<g class="capa capa-mueve" style="--dx:${c.op.desde[0]}px; --dy:${c.op.desde[1]}px">${c.svg}</g>`;
    if ((llega || vuelve) && c.op.gira)
      return `<g class="capa capa-gira" style="--giro:${c.op.gira[0]}deg; transform-origin:${c.op.gira[1]}px ${c.op.gira[2]}px">${c.svg}</g>`;
    return `<g class="capa${llega ? ' capa-nueva' : ''}">${c.svg}</g>`;
  };
  div.innerHTML = `<div class="lienzo figura-lienzo"><svg viewBox="${ej.lienzo.vb || '0 0 400 300'}" role="img"
      aria-label="${ej.lienzo.rot || 'La figura del ejemplo'}">${vis.map(g).join('')}</svg></div>`;
};

/* ═══ el plano con rectas y puntos, que se arma por capas ═══
   lienzo:{ tipo:'plano', R:8, capas:[[en, cosa, hasta], …] }, con cosa:
     { recta:[a, b, c], cls:'recta1', rot:'x + y = 5' }   la recta ax + by = c
     { punto:[x, y], rot:'(3, 2)', guias:true }           x e y pueden ser [n, d]
     { parabola:[a, b, c], cls:'recta1', rot:'y = x² − 4' } la parábola y = ax² + bx + c
     { vertical:h }                                       el eje de simetría x = h, punteado
   La recta que aparece en este paso se traza; el punto cae con un pulso. */
Pizarra.lienzos.plano = (clave, ej, k, avanzando, div) => {
  const nP = ej.pasos.length, R = ej.lienzo.R || 8, T = 400, Mg = 22, Un = (T - 2 * Mg) / (2 * R);
  const px = u => Mg + (u + R) * Un, py = v => Mg + (R - v) * Un;
  const num = v => v === 'final' ? nP + 1 : v === 'control' ? nP + 2 : (v == null ? Infinity : v);
  const val = v => Array.isArray(v) ? v[0] / v[1] : v;
  const dentro = t => t >= -R - 1e-9 && t <= R + 1e-9;
  let g = lienzoRecta(fr(0), fr(0), [], R, T, -1, false);
  ej.lienzo.capas.forEach(([en, c, hasta]) => {
    const e = num(en);
    if (!(e <= k && k < num(hasta))) return;
    const nueva = avanzando && e === k && k > 0;
    if (c.recta){
      const [a, b, cc] = c.recta, pts = [];
      if (b !== 0) for (const x of [-R, R]){ const y = (cc - a * x) / b; if (dentro(y)) pts.push([x, y]); }
      if (a !== 0) for (const y of [-R, R]){ const x = (cc - b * y) / a; if (dentro(x)) pts.push([x, y]); }
      const u = pts.filter((p, i) => pts.findIndex(q => Math.abs(q[0] - p[0]) < 1e-9 && Math.abs(q[1] - p[1]) < 1e-9) === i)
                   .sort((p, q) => p[0] - q[0] || p[1] - q[1]);
      if (u.length < 2) return;
      const [x1, y1, x2, y2] = [px(u[0][0]), py(u[0][1]), px(u[1][0]), py(u[1][1])];
      const largo = Math.hypot(x2 - x1, y2 - y1);
      g += `<line class="${c.cls || 'recta1'}${nueva ? ' dibuja' : ''}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"${
             nueva ? ` style="--largo:${largo.toFixed(1)}"` : ''}/>`;
      if (c.rot){
        // el nombre de la recta, cerca de la punta de la derecha, corrido hacia afuera
        const t = .86, lx = x1 + (x2 - x1) * t, ly = y1 + (y2 - y1) * t;
        const nx = -(y2 - y1) / largo, ny = (x2 - x1) / largo;
        const s = ny > 0 ? -1 : 1;
        g += `<text class="rot-recta ${c.cls === 'recta2' ? 'rot-r2' : 'rot-r1'}${nueva ? ' aparece-rot' : ''}" x="${(lx + s * nx * 16).toFixed(1)}"
               y="${(ly + s * ny * 16).toFixed(1)}" text-anchor="middle">${c.rot}</text>`;
      }
    }
    if (c.parabola){
      // y = ax² + bx + c: la parte que se ve es un solo tramo (la curva es
      // convexa), y se recorta al recuadro
      const [a, b, cc] = c.parabola.map(val), pts = [];
      for (let x = -R; x <= R + 1e-9; x += R / 160){
        const y = a * x * x + b * x + cc;
        if (y >= -R - 1.5 && y <= R + 1.5) pts.push([px(x), py(y)]);
      }
      if (pts.length > 1){
        let largo = 0;
        for (let i = 1; i < pts.length; i++) largo += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
        const d = 'M' + pts.map(p => p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' L');
        g += `<path class="${c.cls || 'recta1'} parabola${nueva ? ' dibuja' : ''}" clip-path="url(#clip-${clave})" d="${d}"${
               nueva ? ` style="--largo:${largo.toFixed(1)}"` : ''}/>`;
        if (c.rot){
          const [lx, ly] = pts[Math.floor(pts.length * .9)];
          g += `<text class="rot-recta ${c.cls === 'recta2' ? 'rot-r2' : 'rot-r1'}${nueva ? ' aparece-rot' : ''}" x="${(lx - 12).toFixed(1)}"
                 y="${Math.max(Mg + 14, ly).toFixed(1)}" text-anchor="end">${c.rot}</text>`;
        }
      }
    }
    if (c.vertical != null){
      // el eje de simetría: una recta vertical punteada
      const X = val(c.vertical);
      g += `<line class="eje-sim${nueva ? ' aparece-rot' : ''}" x1="${px(X)}" y1="${py(R)}" x2="${px(X)}" y2="${py(-R)}"/>`;
    }
    if (c.punto){
      const X = val(c.punto[0]), Y = val(c.punto[1]);
      if (!dentro(X) || !dentro(Y)) return;
      const o = `transform-origin:${px(X)}px ${py(Y)}px`;
      if (c.guias){
        g += `<line class="guia${nueva ? ' sube' : ''}" x1="${px(X)}" y1="${py(0)}" x2="${px(X)}" y2="${py(Y)}" style="transform-origin:${px(X)}px ${py(0)}px"/>`;
        g += `<line class="guia${nueva ? ' cruza' : ''}" x1="${px(X)}" y1="${py(Y)}" x2="${px(0)}" y2="${py(Y)}" style="transform-origin:${px(X)}px ${py(Y)}px"/>`;
      }
      if (nueva) g += `<circle class="onda" cx="${px(X)}" cy="${py(Y)}" r="7" style="${o}; animation-delay:${c.guias ? .85 : .1}s"/>`;
      g += `<circle class="${c.cls || 'punto-tabla'}${nueva ? ' aparece' : ''}" cx="${px(X)}" cy="${py(Y)}" r="7" style="${o}${nueva ? `; animation-delay:${c.guias ? .8 : .05}s` : ''}"/>`;
      if (c.rot){
        // dos puntos a la misma altura (las raíces, dos simétricos): el de la
        // izquierda lleva el rótulo a su izquierda, para que no se pisen
        const misma = ej.lienzo.capas.filter(([, o]) => o.punto && val(o.punto[1]) === Y).map(([, o]) => val(o.punto[0]));
        const izq = X > R - 3 || (misma.length > 1 && X === Math.min(...misma)), abajo = Y < 0;
        g += `<text class="rotulo-punto${nueva ? ' aparece-rot' : ''}" x="${px(X) + (izq ? -10 : 10)}" y="${py(Y) + (abajo ? 22 : -10)}"${izq ? ' text-anchor="end"' : ''}>${c.rot}</text>`;
      }
    }
  });
  div.innerHTML = `<div class="lienzo"><svg viewBox="0 0 ${T} ${T}" role="img" aria-label="${ej.lienzo.rot || 'Las rectas del sistema en el plano'}">
    <defs><clipPath id="clip-${clave}"><rect x="${Mg}" y="${Mg}" width="${T - 2 * Mg}" height="${T - 2 * Mg}"/></clipPath></defs>${g}</svg></div>`;
};

/* ═══ herramientas para dibujar figuras ═══
   Coordenadas del SVG: x a la derecha, y hacia abajo. */
const Geo = {
  f: v => +v.toFixed(1),
  pts: ps => ps.map(p => Geo.f(p[0]) + ',' + Geo.f(p[1])).join(' '),
  medio: (p, q) => [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2],
  dist: (p, q) => Math.hypot(q[0] - p[0], q[1] - p[1]),
  /* el pie de la perpendicular desde a a la recta pq */
  pie(a, p, q){
    const dx = q[0] - p[0], dy = q[1] - p[1];
    const t = ((a[0] - p[0]) * dx + (a[1] - p[1]) * dy) / (dx * dx + dy * dy);
    return [p[0] + t * dx, p[1] + t * dy];
  },
  /* un punto a distancia d de p, yendo hacia q */
  hacia(p, q, d){ const L = Geo.dist(p, q); return [p[0] + (q[0] - p[0]) * d / L, p[1] + (q[1] - p[1]) * d / L]; },
  regular(n, cx, cy, R, giro = -90){
    return Array.from({ length:n }, (_, k) => {
      const a = (giro + k * 360 / n) * Math.PI / 180;
      return [cx + R * Math.cos(a), cy + R * Math.sin(a)];
    });
  },
  /* lo punteado no se traza: pathLength cambiaría el largo de sus rayitas */
  traza: cls => /g-diag|g-aux|g-altura/.test(cls) ? `class="${cls}"` : `class="${cls} traza" pathLength="1"`,
  pol: (ps, cls = 'g-fig') => `<polygon ${Geo.traza(cls)} points="${Geo.pts(ps)}"/>`,
  linea: (ps, cls = 'g-linea') => `<polyline ${Geo.traza(cls)} points="${Geo.pts(ps)}"/>`,
  seg: (p, q, cls = 'g-linea') => `<line ${Geo.traza(cls)}
      x1="${Geo.f(p[0])}" y1="${Geo.f(p[1])}" x2="${Geo.f(q[0])}" y2="${Geo.f(q[1])}"/>`,
  pto: (p, cls = 'g-vert', r = 5) => `<circle class="${cls} pop" cx="${Geo.f(p[0])}" cy="${Geo.f(p[1])}" r="${r}"/>`,
  circ: (c, r, cls = 'g-circ') => `<circle ${Geo.traza(cls)} cx="${Geo.f(c[0])}" cy="${Geo.f(c[1])}" r="${Geo.f(r)}"/>`,
  txt: (p, s, cls = 'g-rot', ancla = 'middle') =>
    `<text class="${cls}" x="${Geo.f(p[0])}" y="${Geo.f(p[1])}" text-anchor="${ancla}" dominant-baseline="middle">${s}</text>`,
  /* el ángulo en v entre las semirrectas hacia p y hacia q; grande: el de más de 180° */
  arco(v, p, q, r = 26, cls = 'g-arco', grande = false){
    const a1 = Math.atan2(p[1] - v[1], p[0] - v[0]), a2 = Math.atan2(q[1] - v[1], q[0] - v[0]);
    let d = a2 - a1;
    while (d <= -Math.PI) d += 2 * Math.PI;
    while (d > Math.PI) d -= 2 * Math.PI;
    if (grande) d = d > 0 ? d - 2 * Math.PI : d + 2 * Math.PI;
    const P1 = [v[0] + r * Math.cos(a1), v[1] + r * Math.sin(a1)];
    const P2 = [v[0] + r * Math.cos(a1 + d), v[1] + r * Math.sin(a1 + d)];
    return `<path class="${cls} pop-suave" d="M ${Geo.pts([v])} L ${Geo.pts([P1])} A ${r} ${r} 0 ${Math.abs(d) > Math.PI ? 1 : 0} ${d > 0 ? 1 : 0} ${Geo.pts([P2])} Z"/>`;
  },
  /* dónde va el rótulo de un ángulo: sobre su bisectriz */
  enAngulo(v, p, q, r = 44, grande = false){
    const u = Geo.hacia(v, p, 1), w = Geo.hacia(v, q, 1);
    let b = [u[0] - v[0] + w[0] - v[0], u[1] - v[1] + w[1] - v[1]];
    const L = Math.hypot(b[0], b[1]) || 1;
    if (grande) b = [-b[0], -b[1]];
    return [v[0] + b[0] / L * r, v[1] + b[1] / L * r];
  },
  /* la escuadrita del ángulo recto en v */
  recto(v, p, q, s = 14){
    const u = Geo.hacia(v, p, s), w = Geo.hacia(v, q, s);
    const x = [u[0] + w[0] - v[0], u[1] + w[1] - v[1]];
    return `<polyline class="g-recto" points="${Geo.pts([u, x, w])}"/>`;
  },
  /* rayitas de lados iguales */
  marcas(p, q, k = 1){
    const m = Geo.medio(p, q), L = Geo.dist(p, q);
    const ux = (q[0] - p[0]) / L, uy = (q[1] - p[1]) / L;
    let s = '';
    for (let i = 0; i < k; i++){
      const o = (i - (k - 1) / 2) * 6;
      const c = [m[0] + ux * o, m[1] + uy * o];
      s += `<line class="g-marca" x1="${Geo.f(c[0] - uy * 7)}" y1="${Geo.f(c[1] + ux * 7)}" x2="${Geo.f(c[0] + uy * 7)}" y2="${Geo.f(c[1] - ux * 7)}"/>`;
    }
    return s;
  },
  /* el rótulo de un lado, afuera de la figura (centro: un punto de adentro) */
  enLado(p, q, centro, d = 16){
    const m = Geo.medio(p, q);
    const L = Geo.dist(p, q);
    let n = [-(q[1] - p[1]) / L, (q[0] - p[0]) / L];
    if ((centro[0] - m[0]) * n[0] + (centro[1] - m[1]) * n[1] > 0) n = [-n[0], -n[1]];
    return [m[0] + n[0] * d, m[1] + n[1] * d];
  },
};

/* ═══ un paso, para adelante (dir = 1) o para atrás (dir = −1) ═══ */
function paso(clave, dir){
  const ej = BLOQUES[clave];
  const k0 = avance[clave] || 0, k = k0 + dir;
  if (k < 0 || k > totalPasos(ej)) return;
  avance[clave] = k;
  const nP = ej.pasos.length, fija = ej.fija || 0;
  const zonaFija = document.getElementById('fija-' + clave);
  if (dir > 0 && k <= fija){
    const lam = nuevaLamina(laminaDe(ej, k));
    zonaFija.appendChild(lam);
    abreCaja(lam);
  }
  if (dir < 0 && k0 <= fija){
    const vivas = [...zonaFija.querySelectorAll(':scope > .lamina:not(.saliendo)')];
    const u = vivas[vivas.length - 1];
    if (u){ u.classList.add('saliendo'); cierraCaja(u, () => u.remove()); }
  }
  if (k > fija || k0 > fija){
    if (dir > 0 && k === nP + 2) agregaLamina(clave, laminaDe(ej, k));
    else if (dir < 0 && k0 === nP + 2) quitaUltimaLamina(clave);
    else cambiaTrabajo(clave, k > fija ? laminaDe(ej, k) : null);
  }
  pintaDerecha(clave, dir > 0);
  llevaAlaVista(document.querySelector(`[data-nav="${clave}"]`));
  actualizaNav(clave);
}
Pizarra.paso = paso;

document.addEventListener('click', ev => {
  const b = ev.target.closest('[data-accion]');
  if (!b || !b.dataset.bloque) return;
  if (b.dataset.accion === 'revelar') paso(b.dataset.bloque, 1);
  if (b.dataset.accion === 'atras') paso(b.dataset.bloque, -1);
});

/* después de poner en la página los bloques: cada uno en su estado 0 */
Pizarra.inicia = () => {
  Object.keys(BLOQUES).forEach(k => {
    if (!document.getElementById('trabajo-' + k)) return;
    pintaDerecha(k, false);
    actualizaNav(k);
  });
};

/* ═══════════════════════════════════════════════════════════════
   El armado de una unidad
   Pizarra.unidad({ TEMAS, DESAFIO, PREGUNTA_INICIAL, UNIDAD, LABS,
                    grado:'7mo', temasLibro:7 })
   La página tiene #temas, #nav y, en la introducción, #recorrido.
   Un tema es { n, corto, titulo, pag, ficha?, concepto, ejemplos,
   taller?, preguntas, notas }. Un puente (un bloque que no está en el
   libro) lleva puente:true, un id propio y entre:'el tema 3 y el 4'.
   Para una clase de práctica (el cursillo): DIAGNOSTICO:{ consigna, notas,
   items } va en #diagnostico-lugar; cada tema puede traer franjas y
   puerta:{ items } (la regla, en PUERTA_REGLA); el mapa de rutas va en
   #mapa-lugar; con ayudaAparte:true los ejemplos de cada tema salen del
   recorrido y van al final, como ayuda (ver «la práctica por franjas»).
   Un tema también puede ir sin concepto: teoria:[…] (diapositivas de
   teoría en el recorrido) y problemas:[ítems de opción múltiple], uno por
   diapositiva, con su clave en las Notas (el cursillo).
   ═══════════════════════════════════════════════════════════════ */
function caja(c){
  const cont = c.ec ? M(c.ec) : c.html ? c.html : `<span class="caja-txt">${c.txt}</span>`;
  return `<div class="caja"><span class="caja-rot">${c.rot}</span>${cont}</div>`;
}

/* ═══ las diapositivas de teoría ═══
   Una palabra nueva, un postulado, un teorema: una idea por diapositiva,
   grande, con su dibujo y una comparación. El cajón dice en qué parte de
   la caja de herramientas se guarda.
   { id, cajon, cod?, titulo, pregunta, enun?, html?, revela?:{ txt },
     mas?:[…], como?, figura?, verFigura?, fuente?, elementos?:[[id, nombre]] }
   elementos lleva a la entrada del libro de Euclides (omapa/elementos),
   que a su vez nombra esta diapositiva en su «En clase»: el vínculo va y vuelve.
   Van antes de un ejemplo (ej.antes), después de los ejemplos de un tema
   (t.despues) o al principio de la unidad (cfg.INICIO, en #teoria-inicio).
   chip, si está, cambia el nombre del cajón sin cambiarle el color: en una
   clase que no es de geometría, el cajón «lenguaje» se llama «Lenguaje». */
const CAJONES = { definicion:'Definición', postulado:'Postulado', nocion:'Noción común',
  teorema:'Teorema', construccion:'Construcción', estrategia:'Estrategia', lenguaje:'El lenguaje de la geometría' };
/* Lo que dice la diapositiva aparece por partes, como los pasos de un
   ejemplo. Al principio, solo el título y la pregunta: la piensan ellos.
   Con «Siguiente», el enunciado (y el dibujo con él, salvo que la pregunta
   lo necesite: verFigura), la caja, la respuesta (revela), cada línea más y
   la comparación. */
function teoria(td, cinta, attrs = ''){
  const t = s => sombrero(s);
  const partes = [
    ...(td.enun ? [`<p class="teoria-enun">${t(td.enun)}</p>`] : []),
    ...(td.html ? [].concat(td.html) : []),
    ...(td.revela ? [`<p class="teoria-respuesta">${t(td.revela.txt)}</p>`] : []),
    ...(td.mas || []).map(m => `<p class="teoria-mas">${t(m)}</p>`),
    ...(td.como ? [`<p class="teoria-como"><span>Una comparación</span>${t(td.como)}</p>`] : []),
  ];
  const fuente = (td.fuente ? `<p class="teoria-fuente">${td.fuente}</p>` : '') +
    (td.elementos ? `<p class="teoria-elementos">${td.elementos.map(([id, n]) =>
      `<a href="../../omapa/elementos/libro-1.html#${id}">En los Elementos de Euclides: ${n} →</a>`).join(' ')}</p>` : '');
  if (partes.length) partes[partes.length - 1] += fuente;
  return `
  <section class="teoria-diapo" id="d-${td.id}" data-cajon="${td.cajon}"${attrs}>
    ${cinta ? `<p class="cinta">${cinta}</p>` : ''}
    <p class="cajon-chip">${td.chip || CAJONES[td.cajon]}${td.cod ? ` <b>${td.cod}</b>` : ''}</p>
    <h3 class="teoria-tit">${td.titulo}</h3>
    <div class="teoria-cuerpo${td.figura ? ' con-figura' : ''}">
      <div class="teoria-txt">
        ${td.pregunta ? `<p class="teoria-pregunta">${t(td.pregunta)}</p>` : ''}
        ${partes.map((p, k) => `<div class="teoria-parte" data-parte="${k + 1}" hidden>${p}</div>`).join('')}
        ${partes.length ? `<div class="pasos-nav abajo teoria-nav" data-teoria="${td.id}" data-visto="0" data-total="${partes.length}">
          <button class="boton" type="button" data-accion="teoria-atras" disabled>← Anterior</button>
          <span class="pasos-cuenta">${partes.length} ${partes.length === 1 ? 'paso' : 'pasos'}</span>
          <button class="boton" type="button" data-accion="teoria-sigue">Siguiente →</button>
        </div>` : fuente}
      </div>
      ${td.figura ? `<div class="teoria-figura${td.verFigura || !partes.length ? '' : ' tapada" data-con-enun="1'}">${td.figura}</div>` : ''}
    </div>
  </section>`;
}
document.addEventListener('click', ev => {
  const b = ev.target.closest('[data-accion^="teoria-"]');
  if (!b) return;
  const nav = b.closest('.teoria-nav'), total = +nav.dataset.total;
  const visto = Math.max(0, Math.min(total, +nav.dataset.visto + (b.dataset.accion === 'teoria-sigue' ? 1 : -1)));
  nav.dataset.visto = visto;
  nav.parentNode.querySelectorAll('.teoria-parte').forEach(p => {
    const ver = +p.dataset.parte <= visto;
    p.classList.toggle('recien-parte', ver && p.hidden);
    p.hidden = !ver;
  });
  const fig = nav.closest('.teoria-diapo').querySelector('.teoria-figura[data-con-enun]');
  if (fig && fig.classList.contains('tapada') === (visto > 0)){
    fig.classList.toggle('recien-parte', visto > 0);
    fig.classList.toggle('tapada', visto === 0);
  }
  nav.querySelector('[data-accion="teoria-atras"]').disabled = visto === 0;
  nav.querySelector('[data-accion="teoria-sigue"]').disabled = visto === total;
  nav.querySelector('.pasos-cuenta').textContent = visto ? `paso ${visto} de ${total}` : `${total} ${total === 1 ? 'paso' : 'pasos'}`;
  llevaAlaVista(nav);
});

/* ═══ la práctica ═══
   Tres ejercicios para que los hagan ellos, los tres a la vista a la vez y
   sin pasos: cada uno con su botón «Ver respuesta». Van después de los
   ejemplos de un tema (t.practica) o después de un ejemplo (ej.practica):
     practica:[{ enun:'Pasar 2,35 km a metros.', resp:'2.350 m' }, …]
   La página agrega .practica-diapo a data-diapos. */
let nPractica = 0;
function practica(items, cinta){
  return `
  <section class="practica-diapo" id="pr-${++nPractica}">
    <p class="cinta">${cinta}</p>
    <h4 class="ej-titulo">Ahora ustedes</h4>
    <ol class="practica">${items.map(it => `
      <li><div class="prac-enun">${sombrero(it.enun)}</div>
        <button class="boton prac-ver" type="button" data-accion="prac-ver" aria-expanded="false">Ver respuesta</button>
        <div class="prac-resp" hidden>${sombrero(it.resp)}</div></li>`).join('')}
    </ol>
  </section>`;
}
document.addEventListener('click', ev => {
  const b = ev.target.closest('[data-accion="prac-ver"]');
  if (!b) return;
  const resp = b.nextElementSibling, ver = resp.hidden;
  resp.hidden = !ver;
  resp.classList.toggle('recien-parte', ver);
  b.setAttribute('aria-expanded', String(ver));
  b.textContent = ver ? 'Ocultar' : 'Ver respuesta';
});

/* El control remoto del proyector (assets/proyeccion.js) pregunta acá si
   la diapositiva tiene un paso más para dar antes de pasar a la siguiente:
   el ejemplo, la teoría o la próxima respuesta de la práctica. Devuelve
   true si lo dio. */
Pizarra.avanza = (diapo, dir) => {
  if (!diapo) return false;
  const toca = sel => {
    const b = diapo.querySelector(sel);
    if (!b || b.disabled) return false;
    b.click();
    return true;
  };
  if (diapo.querySelector('[data-nav]'))
    return toca(`[data-nav] [data-accion="${dir > 0 ? 'revelar' : 'atras'}"]`);
  if (diapo.querySelector('.teoria-nav'))
    return toca(`.teoria-nav [data-accion="${dir > 0 ? 'teoria-sigue' : 'teoria-atras'}"]`);
  const ver = [...diapo.querySelectorAll('[data-accion="prac-ver"]')];
  const b = dir > 0 ? ver.find(x => x.getAttribute('aria-expanded') === 'false')
                    : ver.filter(x => x.getAttribute('aria-expanded') === 'true').pop();
  if (!b) return false;
  b.click();
  return true;
};

/* ═══ la opción múltiple, como en el examen ═══
   Un ítem es { cod, enun, opciones:[{ t, ok:true }, { t, error:'…' }, …] }.
   En pantalla van el enunciado y las opciones con su letra; el error que
   produce cada opción incorrecta no se proyecta: con él se arma la clave de
   las Notas (claveDe), que así sale de los mismos datos. Se usa en el
   diagnóstico, en las puertas de cada tema y en los ítems nuevos de las
   franjas. Los alumnos responden en papel. */
const LETRAS = 'ABCDEFGH';
function opciones(it, conCod = true){
  return `
      <li class="mc${it.largo ? ' mc-largo' : ''}" id="mc-${it.cod}">
        <p class="mc-enun">${conCod ? `<b class="mc-cod">${it.cod}</b> ` : ''}${sombrero(it.enun)}</p>
        <ol class="mc-ops">${it.opciones.map((o, k) =>
          `<li${o.ok ? ' data-ok="1"' : ''}><b>${LETRAS[k]})</b> ${sombrero(o.t)}</li>`).join('')}</ol>
      </li>`;
}
function claveDe(items){
  return '<ul class="mc-clave">' + items.map(it => {
    const k = it.opciones.findIndex(o => o.ok);
    return `<li><b>${it.cod}</b>: la <b>${LETRAS[k]}</b> (${it.opciones[k].t}).<ul>${it.opciones.map((o, j) =>
      o.ok ? '' : `<li>${LETRAS[j]}) ${o.t}${o.error ? ': ' + o.error : ''}</li>`).join('')}</ul></li>`;
  }).join('') + '</ul>';
}
/* una hoja de ítems; con clave, lleva el botón «Ver clave», que marca las
   letras correctas en pantalla para que cada grupo se corrija. El control
   remoto no la muestra: se pide con el botón. */
function hojaMC(o){
  return `
  <section class="${o.clase} mc-hoja" id="${o.id}"${o.attrs || ''}>
    <p class="cinta">${o.cinta}</p>
    <h4 class="ej-titulo">${o.titulo}</h4>
    ${o.antes || ''}
    <ol class="mc-grilla">${o.items.map(it => opciones(it, !o.sinCod)).join('')}</ol>
    ${o.clave ? '<button class="boton mc-ver-btn" type="button" data-accion="mc-clave" aria-pressed="false">Ver clave</button>' : ''}
    ${o.despues || ''}
  </section>`;
}

/* ═══ la tabla de unidades ═══
   Las unidades de una magnitud en fila, de la más grande a la más chica,
   como la tabla del material: múltiplos, unidad y submúltiplos, con el
   nombre, el símbolo y lo que vale cada una (10^3 m se escribe con ^);
   debajo, el salto de cada una a la siguiente (× 10, o × 10² en superficie).
   Las filas extra (las unidades agrarias, el volumen, el agua) van alineadas
   con su columna:
     tablaUnidades({ cols:[{ nombre, sim, vale }, …], unidad:3, salto:'× 10',
                     extra:[{ rot:'agrarias', en:{ 1:'ha', 2:'a', 3:'ca' } }] })
   Con extraAparte:true la tabla sale sin las filas extra, y
   tablaUnidades({ …lo mismo, soloExtra:true }) da solo esas filas, con las
   mismas columnas: en otra parte de la teoría, debajo, quedan alineadas. */
function tablaUnidades(o){
  const n = o.cols.length, u = o.unidad;
  const pot = s => String(s ?? '').replace(/\^([−-]?\d+)/g, '<sup>$1</sup>');
  const caja = (cont, cls = '') => `<div class="tu-c ${cls}">${cont}</div>`;
  const rot = r => `<div class="tu-rot">${r || ''}</div>`;
  const fila = (r, celdas, cls) => rot(r) + celdas.map((c, i) =>
    caja(c, cls + (i === u ? ' tu-u' : '') + (c ? '' : ' tu-vacia'))).join('');
  const extras = (o.extra || []).map(e => fila(e.rot, o.cols.map((_, i) => pot(e.en[i])), 'tu-extra')).join('');
  const estilo = `style="--tu-n:${n}; --tu-rotw:${o.extra && o.extra.length ? '7.5em' : '0px'}"`;
  if (o.soloExtra) return `<div class="tu tu-solo-extra" ${estilo}>${extras}</div>`;
  const grupos = rot('') +
    (u > 0 ? `<div class="tu-g" style="grid-column:span ${u}">Múltiplos</div>` : '') +
    '<div class="tu-g tu-u">Unidad</div>' +
    (u < n - 1 ? `<div class="tu-g" style="grid-column:span ${n - 1 - u}">Submúltiplos</div>` : '');
  const saltos = rot('') + o.cols.map((_, i) => `<div class="tu-s">${i < n - 1 ?
    `<span class="tu-arco"></span><span class="tu-x">${o.salto}</span>` : ''}</div>`).join('');
  return `<div class="tu" ${estilo}>${grupos}${
    fila('', o.cols.map(c => `<b>${c.sim}</b><small>${c.nombre}</small>`), 'tu-sim')}${
    fila('', o.cols.map(c => pot(c.vale)), 'tu-vale')}${saltos}${o.extraAparte ? '' : extras}</div>`;
}
document.addEventListener('click', ev => {
  const b = ev.target.closest('[data-accion="mc-clave"]');
  if (!b) return;
  const ver = b.getAttribute('aria-pressed') !== 'true';
  b.closest('.mc-hoja').classList.toggle('mc-ver', ver);
  b.setAttribute('aria-pressed', String(ver));
  b.textContent = ver ? 'Ocultar clave' : 'Ver clave';
});

/* ═══ la práctica por franjas ═══
   Cada tema puede traer franjas:{ A:[…], B:[…], C:[…] } (A base, B tipo
   examen, C desafío). Un ejercicio del libro es { libro:'5.2', n:1 } (o
   libro:'cuest'): en pantalla va solo la referencia, porque lo tienen en
   papel. Un ítem nuevo es un ítem de opción múltiple, con su código.
   Los niveles son rutas por las franjas, y salen solas de las listas:
     Nivel 1: toda A y toda B;
     Nivel 2: la segunda mitad de A, toda B y la primera mitad de C;
     Nivel 3: los dos últimos de B, como control, y toda C. */
const FRANJAS = { A:'base', B:'tipo examen', C:'desafío' };
/* un ítem nuevo, en la grilla, lleva a su diapositiva */
const refLarga = it => it.cod ? `<a href="#mc-${it.cod}">Ítem ${it.cod}</a>` :
  (it.libro === 'cuest' ? `Cuestionario, ej. ${it.n}` : `Ejercitario ${it.libro}, ej. ${it.n}`);
const refCorta = it => it.cod || (it.libro === 'cuest' ? `Cuest. ${it.n}` : `${it.libro} ej. ${it.n}`);
function rutas(f){
  const A = f.A || [], B = f.B || [], C = f.C || [];
  return { 1:[...A, ...B],
           2:[...A.slice(Math.floor(A.length / 2)), ...B, ...C.slice(0, Math.ceil(C.length / 2))],
           3:[...B.slice(-2), ...C] };
}
const marcasNivel = (it, R) => `<span class="niveles">${[1, 2, 3].map(n =>
  R[n].includes(it) ? `<i class="nv nv${n}" title="Nivel ${n}">${n}</i>` : '').join('')}</span>`;
function columnasFranjas(f, R, ref){
  return Object.keys(FRANJAS).map(k => `
      <div class="franja franja-${k}"><h5><b>${k}</b> ${FRANJAS[k]}</h5>
        <ul>${(f[k] || []).map(it => `<li>${ref(it)}${marcasNivel(it, R)}</li>`).join('') ||
          '<li class="franja-vacia">ítems nuevos por definir</li>'}</ul></div>`).join('');
}

Pizarra.unidad = cfg => {
  const { TEMAS, DESAFIO, PREGUNTA_INICIAL, UNIDAD, LABS = {}, INICIO, DIAGNOSTICO, PUERTA_REGLA = '',
          ayudaAparte = false, grado, temasLibro = TEMAS.length } = cfg;
  const idT = t => t.id || String(t.n);
  const etiqueta = t => t.puente ? 'Puente' : `Tema ${t.n}`;
  const cintaT = t => `<b>${etiqueta(t)}</b> · ${t.corto} · caja de herramientas`;
  /* adónde lleva el nombre del tema: al concepto, o a su primera diapositiva */
  const ancla = t => t.concepto ? 't' + idT(t) : t.teoria && t.teoria.length ? 'd-' + t.teoria[0].id :
    t.problemas && t.problemas.length ? 'prob-' + t.problemas[0].cod : 't' + idT(t);
  /* adónde se vuelve desde la ayuda: la práctica, o el ejercicio del tema */
  const vuelta = t => t.franjas ? 'practica-' + idT(t) :
    t.problemas && t.problemas.length ? 'prob-' + t.problemas[t.problemas.length - 1].cod : ancla(t);
  /* los ejercicios del tema: uno por diapositiva, de opción múltiple, como en
     el examen; «Ver clave» marca la correcta. Si el tema tiene ejemplos
     resueltos aparte, el ejercicio lleva a ellos. Un ejercicio con
     tras:'<id de una teoría>' va justo después de esa diapositiva de teoría
     (teoría, ejercicio, teoría, ejercicio); los demás, al final del tema */
  const problemasDe = (t, tras = null) => (t.problemas || []).map((it, i, todos) => (it.tras || null) !== tras ? '' : hojaMC({
    clase:'problema-diapo', id:'prob-' + it.cod, clave:true, sinCod:true, items:[it],
    cinta:`<b>${etiqueta(t)}</b> · ${t.corto} · ejercicio${todos.length > 1 ? ` ${i + 1} de ${todos.length}` : ''}`,
    titulo:it.titulo || 'Ejercicio',
    despues:ayudaAparte && t.ejemplos && t.ejemplos.length ?
      `<p class="a-ayuda"><a href="#ayuda-${idT(t)}">Ejemplos resueltos del tema →</a></p>` : '' })).join('');

  /* los ejemplos resueltos de un tema; con ayudaAparte van al final, como
     ayuda que se abre cuando un grupo se traba, fuera del recorrido */
  const ejemplosDe = t => t.ejemplos.map((ej, i) => (ej.antes || []).map(td => teoria(td, cintaT(t))).join('') +
      bloque(`${idT(t)}-${i + 1}`, ej, {
        rotulo:`Ejemplo ${i + 1}.`,
        cinta:`<b>${etiqueta(t)}</b> · ${t.corto} · ${ayudaAparte ? 'ayuda, ' : ''}ejemplo ${i + 1} de ${t.ejemplos.length}` }) +
      (ej.practica ? practica(ej.practica, `<b>${etiqueta(t)}</b> · ${t.corto} · después del ejemplo ${i + 1}`) : '')).join('') +
    (t.practica ? practica(t.practica, `<b>${etiqueta(t)}</b> · ${t.corto} · para practicar`) : '') +
    (t.despues || []).map(td => teoria(td, cintaT(t))).join('');

  /* la práctica del tema: las tres franjas, las rutas y la puerta */
  const practicaDe = t => {
    if (!t.franjas) return '';
    const R = rutas(t.franjas), id = idT(t);
    /* los ítems nuevos de cada franja, de a 4 por diapositiva, en el orden
       de la ruta: A, B, la puerta, C */
    const hojasDe = k => {
      const its = (t.franjas[k] || []).filter(it => it.opciones), h = [];
      for (let i = 0; i < its.length; i += 4) h.push(hojaMC({
        clase:'franja-mc-diapo', id:`fr-${id}-${k}-${i / 4 + 1}`, clave:true,
        cinta:`<b>${etiqueta(t)}</b> · ${t.corto} · franja ${k}`,
        titulo:`Tema ${t.n}, franja ${k}: ${FRANJAS[k]}`, items:its.slice(i, i + 4) }));
      return h.join('');
    };
    return `
  <section class="franjas-diapo" id="practica-${id}">
    <p class="cinta"><b>${etiqueta(t)}</b> · ${t.corto} · práctica</p>
    <h4 class="ej-titulo">Práctica del tema ${t.n}</h4>
    <div class="franjas">${columnasFranjas(t.franjas, R, refLarga)}</div>
    <div class="rutas">${[1, 2, 3].map(n => `<p class="ruta"><i class="nv nv${n}">${n}</i> <b>Nivel ${n}:</b> ${
      R[n].map(refCorta).join(', ') || 'por definir'}</p>`).join('')}</div>
    ${ayudaAparte ? `<p class="a-ayuda"><a href="#ayuda-${id}">¿Se traban? Ayuda del tema ${t.n}: los ejemplos resueltos →</a></p>` : ''}
  </section>${hojasDe('A')}${hojasDe('B')}${t.puerta ? hojaMC({
      clase:'puerta-diapo', id:`puerta-${id}`, clave:true, items:t.puerta.items,
      cinta:`<b>${etiqueta(t)}</b> · ${t.corto} · puerta`, titulo:`La puerta del tema ${t.n}`,
      antes:`<p class="puerta-regla">${t.puerta.regla || PUERTA_REGLA}</p>` }) : ''}${hojasDe('C')}`;
  };

  const ayudas = [];
  document.getElementById('temas').innerHTML = raices(TEMAS.map(t => {
    const c = t.concepto;
    if (ayudaAparte && t.ejemplos && t.ejemplos.length) ayudas.push(`
<article class="tema ayuda" id="ayudas-${idT(t)}" data-tema="${idT(t)}" data-ayuda="${idT(t)}" data-vuelve="${vuelta(t)}">
  <section class="ayuda-cab" id="ayuda-${idT(t)}">
    <p class="cinta"><b>${etiqueta(t)}</b> · ${t.corto} · ayuda</p>
    <h3>Ayuda del tema ${t.n}: ${t.corto.toLowerCase()}</h3>
    <p>Los ejemplos resueltos, para cuando un grupo se traba. Al terminar, se vuelve ${t.franjas ? 'a la práctica' : 'al ejercicio'}.</p>
    <p class="a-ayuda"><a href="#${vuelta(t)}">← Volver ${t.franjas ? 'a la práctica' : 'al ejercicio'} del tema ${t.n}</a></p>
  </section>
  ${ejemplosDe(t)}
</article>`);
    return `
<article class="tema${t.puente ? ' puente' : ''}" id="tema${idT(t)}" data-tema="${idT(t)}">
  ${c ? `<section class="concepto" id="t${idT(t)}">
    <p class="cinta">${t.puente ? `<b>Puente entre ${t.entre}</b> · no está en el libro` : `<b>Tema ${t.n} de ${temasLibro}</b> · ${t.pag}`}</p>
    <div class="caso-cab">
      <div class="numero">${t.puente ? '→' : t.n}</div>
      <div class="caso-tit"><h3>${t.titulo}</h3></div>
    </div>
    ${c.forma ? `<div class="forma"><span class="rotulo">${c.formaRot}</span>${M(c.forma)}</div>` : ''}
    ${c.formaTxt ? `<div class="forma"><span class="rotulo">la idea</span><span class="forma-txt">${c.formaTxt}</span></div>` : ''}
    ${c.serie ? `<div class="serie">${c.serie.map(caja).join('')}</div>` : ''}
    ${c.figura ? `<div class="concepto-figura">${c.figura}</div>` : ''}
    <ul class="puntos">${c.puntos.map(p => `<li>${p}</li>`).join('')}</ul>
  </section>` : ''}
  ${(t.teoria || []).map(td => teoria(td, cintaT(t)) + problemasDe(t, td.id)).join('')}
  ${problemasDe(t)}

  ${ayudaAparte || !t.ejemplos ? '' : `<div class="ejemplos">${ejemplosDe(t)}</div>`}
  ${practicaDe(t)}

  ${t.taller ? [].concat(t.taller).map(lab => `<section class="taller-diapo">
    <p class="cinta"><b>${etiqueta(t)}</b> · ${t.corto} · taller</p>
    ${LABS[lab]}
  </section>`).join('') : ''}

  ${t.ficha ? `<p class="ficha-link">Para practicar:
    <a href="../../fichas/pdf/${grado}/Ficha_${String(t.ficha).padStart(2, '0')}.pdf">Ficha ${t.ficha}</a></p>` : ''}
</article>`;
  }).join('') + (DESAFIO ? bloque('desafio', DESAFIO, {
      cinta:'<b>Desafío final</b> · toda la unidad junta', clase:'desafio', id:'desafio',
      attrs:'data-tema="desafio"' }) : '') + (ayudas.length ? `<div class="ayudas">${ayudas.join('')}</div>` : ''));

  /* el diagnóstico, antes de la introducción: en hojas de 4 ítems, sin clave
     en pantalla (la clave y la regla de ubicación van en las Notas) */
  const lugarDiag = document.getElementById('diagnostico-lugar');
  if (DIAGNOSTICO && lugarDiag){
    const its = DIAGNOSTICO.items, n = DIAGNOSTICO.porHoja || 4, hojas = [];
    for (let i = 0; i < its.length; i += n) hojas.push(hojaMC({
      clase:'diagnostico-diapo', id:`diagnostico-${i / n + 1}`, attrs:' data-tema="unidad"', items:its.slice(i, i + n),
      clave:!!DIAGNOSTICO.clave,
      cinta:`<b>Diagnóstico</b> · ítems ${i + 1} a ${Math.min(i + n, its.length)} de ${its.length}`,
      titulo:i ? 'Diagnóstico (sigue)' : 'Diagnóstico', antes:i ? '' : `<p class="diag-consigna">${DIAGNOSTICO.consigna}</p>` }));
    lugarDiag.outerHTML = raices(hojas.join(''));
  }

  /* el mapa de rutas: los temas por las franjas, con qué hace cada nivel */
  const lugarMapa = document.getElementById('mapa-lugar');
  if (lugarMapa && TEMAS.some(t => t.franjas)){
    lugarMapa.outerHTML = raices(`
  <section class="mapa-diapo" id="mapa" data-tema="unidad">
    <p class="cinta"><b>El mapa</b> · qué hace cada nivel</p>
    <h4 class="ej-titulo">El mapa de la práctica</h4>
    <table class="mapa">
      <thead><tr><th>Tema</th>${Object.keys(FRANJAS).map(k => `<th><b>${k}</b> ${FRANJAS[k]}</th>`).join('')}</tr></thead>
      <tbody>${TEMAS.filter(t => t.franjas).map(t => {
        const R = rutas(t.franjas);
        return `<tr><th><a href="#practica-${idT(t)}">${t.n}. ${t.corto}</a></th>${Object.keys(FRANJAS).map(k =>
          `<td>${(t.franjas[k] || []).map(it => `<span class="mapa-it">${refCorta(it)}${marcasNivel(it, R)}</span>`).join('') ||
            '<span class="franja-vacia">por definir</span>'}</td>`).join('')}</tr>`;
      }).join('')}</tbody>
    </table>
    <p class="mapa-ley"><span><i class="nv nv1">1</i> Nivel 1: A y B</span>
      <span><i class="nv nv2">2</i> Nivel 2: el final de A, toda B y el principio de C</span>
      <span><i class="nv nv3">3</i> Nivel 3: dos de B como control, y toda C</span></p>
  </section>`);
  }

  /* la pregunta de arranque, en la introducción */
  /* si la página le hizo lugar (#arranque-lugar), va en su propia diapositiva */
  const recorrido = document.getElementById('recorrido');
  const lugar = document.getElementById('arranque-lugar');
  if (PREGUNTA_INICIAL){
    const html = bloque('inicial', { titulo:'Para arrancar', ...PREGUNTA_INICIAL },
      { clase:'arranque', id:'arranque', attrs:lugar ? 'data-tema="unidad"' : '' });
    if (lugar) lugar.outerHTML = html;
    else recorrido.insertAdjacentHTML('beforebegin', html);
  }
  const inicio = document.getElementById('teoria-inicio');
  if (INICIO && inicio){
    inicio.outerHTML = raices(INICIO.map(td =>
      teoria(td, '<b>Antes de empezar</b> · geometría a la manera de los griegos', ' data-tema="unidad"')).join(''));
  }

  /* el recorrido de la unidad y el navegador */
  recorrido.innerHTML = TEMAS.map(t =>
    `<a href="#${ancla(t)}"><span class="n">${etiqueta(t)}</span><span class="t">${t.corto}</span></a>`).join('');
  document.getElementById('nav').innerHTML =
    TEMAS.map(t => `<a class="chip" href="#${ancla(t)}">${t.puente ? String(t.n).replace('→', ' → ') : t.n + '.'} ${t.corto}</a>`).join('') +
    (DESAFIO ? '<a class="chip" href="#desafio">Desafío</a>' : '');

  /* las notas y el observador viven en los botones flotantes de assets/clase.js */
  window.CLASE = { secciones: [
    { id:'unidad', titulo:'La unidad', preguntas:UNIDAD.preguntas, notas:UNIDAD.notas + (DIAGNOSTICO ?
        `<h4>El diagnóstico</h4>${DIAGNOSTICO.notas || ''}<p><b>La clave</b>, con el error que lleva a cada opción incorrecta:</p>${claveDe(DIAGNOSTICO.items)}` : '') },
    ...TEMAS.map(t => ({ id:idT(t), titulo:t.puente ? `Puente · ${t.titulo.toLowerCase()}` : `Tema ${t.n} · ${t.corto}`,
                          preguntas:t.preguntas, notas:t.notas + (t.problemas ?
        `<h4>La clave ${t.problemas.length > 1 ? 'de los ejercicios' : 'del ejercicio'}</h4>${claveDe(t.problemas)}` : '') + (t.puerta ?
        `<h4>La clave de la puerta</h4>${claveDe(t.puerta.items)}` : '') + (t.franjas ? Object.keys(FRANJAS).map(k => {
          const its = (t.franjas[k] || []).filter(it => it.opciones);
          return its.length ? `<h4>La clave de la franja ${k}</h4>${claveDe(its)}` : '';
        }).join('') : '') })),
    ...(DESAFIO ? [{ id:'desafio', titulo:'Desafío final', notas:DESAFIO.notas, preguntas:DESAFIO.preguntas }] : []),
  ].map(s => ({ ...s, notas:raices(s.notas || ''),
                preguntas:(s.preguntas || []).map(q => ({ p:raices(q.p), r:raices(q.r) })) }))};

  Pizarra.inicia();
};
