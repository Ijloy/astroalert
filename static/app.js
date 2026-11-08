/* ═══════════════════════════════════════════════════════════════
   AstroAlert — frontend
   La API vive en el mismo servidor (Flask), por eso las rutas son relativas.
   Índice: utilidades · navegación · cuenta · inicio · secciones · arranque
   ═══════════════════════════════════════════════════════════════ */
'use strict';

const API = '';
const CIUDAD = 'Quito';

// ═════════════ UTILIDADES ═════════════
const $ = id => document.getElementById(id);

async function getJSON(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

/** Escapa texto antes de insertarlo como HTML. */
function esc(valor) {
  return String(valor ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/** Números con formato de Ecuador: 2.457 km, 18,4 UA. */
function num(n, decimales = 0) {
  return Number(n).toLocaleString('es-EC', { minimumFractionDigits: 0, maximumFractionDigits: decimales });
}

function horasTexto(minutos) {
  const h = Math.floor(minutos / 60), m = minutos % 60;
  return h ? `${h} h${m ? ` ${m} min` : ''}` : `${m} min`;
}

function cargandoHTML(lineas = 3) {
  return '<div aria-busy="true" aria-label="Cargando">' +
    '<span class="skeleton skeleton-linea larga"></span>' +
    Array.from({ length: lineas }, (_, i) => `<span class="skeleton skeleton-linea ${i % 2 ? 'corta' : ''}"></span>`).join('') +
    '</div>';
}

/** Estado de error con botón "Reintentar" (patrón de errores de docs/UX). */
function mostrarError(id, reintentar) {
  const cont = $(id);
  cont.innerHTML = `
    <div class="estado-error">
      <p>No pudimos obtener esta información ahora mismo. Inténtalo de nuevo en unos minutos.</p>
      <button class="btn btn-secundario btn-sm" type="button">Reintentar</button>
    </div>`;
  cont.querySelector('button').addEventListener('click', reintentar);
}

// Si una foto no carga (enlace roto, sin red), se muestra una luna ilustrada en su lugar.
const IMG_RESPALDO = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><radialGradient id="g" cx="35%" cy="35%">' +
  '<stop offset="0" stop-color="#9370DB"/><stop offset="1" stop-color="#2C1E5C"/></radialGradient></defs>' +
  '<rect width="100" height="100" fill="#120C26"/><circle cx="50" cy="50" r="34" fill="url(#g)"/></svg>');

function conRespaldo(contenedor) {
  contenedor.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', () => { img.src = IMG_RESPALDO; }, { once: true });
  });
}

async function imagenNasa(query, elementId) {
  try {
    const data  = await fetch(`https://images-api.nasa.gov/search?q=${encodeURIComponent(query)}&media_type=image`).then(r => r.json());
    const items = data.collection?.items || [];
    if (!items.length) return;
    const item = items[Math.floor(Math.random() * Math.min(items.length, 10))];
    const link = item.links?.find(l => l.rel === 'preview');
    if (link && $(elementId)) $(elementId).style.backgroundImage = `url('${link.href}')`;
  } catch { /* imagen decorativa: si falla, la tarjeta se ve igual */ }
}

// ═════════════ NAVEGACIÓN (URLs reales: /eclipses, /iss…) ═════════════
const VISTAS = {
  '/':             { id: 'inicio',       titulo: null },
  '/iss':          { id: 'iss',          titulo: 'ISS en vivo',              cargar: cargarISS, siempre: true },
  '/planetas':     { id: 'planetas',     titulo: 'Planetas visibles',        cargar: cargarPlanetas, siempre: true },
  '/eclipses':     { id: 'eclipses',     titulo: 'Eclipses',                 cargar: cargarEclipses },
  '/conjunciones': { id: 'conjunciones', titulo: 'Conjunciones planetarias', cargar: cargarConjunciones },
  '/oposiciones':  { id: 'oposiciones',  titulo: 'Oposiciones',              cargar: cargarOposiciones },
  '/cometas':      { id: 'cometas',      titulo: 'Cometas',                  cargar: cargarCometas },
  '/lunas':        { id: 'lunas',        titulo: 'Lunas del sistema solar',  cargar: cargarLunas },
  '/telescopio':   { id: 'telescopio',   titulo: 'Calculadora de telescopio', cargar: cargarImagenTelescopio },
  '/proximamente': { id: 'proximamente', titulo: 'En desarrollo' },
};
const cargadas = new Set();

function mostrarVista(ruta, { enfocar = true } = {}) {
  const vista = VISTAS[ruta] || VISTAS['/'];
  document.querySelectorAll('.vista').forEach(v => { v.hidden = v.id !== `vista-${vista.id}`; });

  document.querySelectorAll('.sidebar-item[href]').forEach(a => {
    if (a.getAttribute('href') === ruta) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });

  document.title = vista.titulo ? `${vista.titulo} · AstroAlert` : 'AstroAlert — Eventos astronómicos visibles desde Quito';
  cerrarSidebar();
  window.scrollTo({ top: 0 });

  if (vista.cargar && (vista.siempre || !cargadas.has(vista.id))) {
    cargadas.add(vista.id);
    vista.cargar();
  }
  // Para lectores de pantalla: llevar el foco al título de la nueva vista
  if (enfocar) {
    const h1 = document.querySelector(`#vista-${vista.id} h1`);
    (h1 || $('contenido')).focus({ preventScroll: true });
  }
}

function navegar(ruta) {
  if (ruta !== location.pathname) history.pushState({}, '', ruta);
  mostrarVista(ruta);
}

document.addEventListener('click', e => {
  const enlace = e.target.closest('a[data-link]');
  if (!enlace || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
  e.preventDefault();
  navegar(enlace.getAttribute('href'));
});
window.addEventListener('popstate', () => mostrarVista(location.pathname));

// ── Menú lateral ──
function abrirSidebar() {
  $('sidebar').classList.add('abierto');
  $('sidebar-overlay').classList.add('activo');
  $('btn-menu').setAttribute('aria-expanded', 'true');
  $('sidebar').querySelector('a, button')?.focus();
}
function cerrarSidebar() {
  if (!$('sidebar').classList.contains('abierto')) return;
  $('sidebar').classList.remove('abierto');
  $('sidebar-overlay').classList.remove('activo');
  $('btn-menu').setAttribute('aria-expanded', 'false');
}
const sidebarFijo = () => window.matchMedia('(min-width: 1200px)').matches;

$('btn-menu').addEventListener('click', () => ($('sidebar').classList.contains('abierto') ? cerrarSidebar() : abrirSidebar()));
$('sidebar-overlay').addEventListener('click', cerrarSidebar);

// ═════════════ CUENTA (opcional: solo para alertas) ═════════════
const getToken    = () => localStorage.getItem('token');
const setToken    = t => localStorage.setItem('token', t);
const removeToken = () => localStorage.removeItem('token');
let focoAntesDeDialogo = null;

function abrirDialogo(id) {
  cerrarDialogos(false);
  focoAntesDeDialogo = focoAntesDeDialogo || document.activeElement;
  $(id).hidden = false;
  $(id).querySelector('input')?.focus();
}
function cerrarDialogos(devolverFoco = true) {
  ['login-panel', 'registro-panel'].forEach(id => { $(id).hidden = true; });
  if (devolverFoco && focoAntesDeDialogo) { focoAntesDeDialogo.focus(); focoAntesDeDialogo = null; }
}

document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (!$('login-panel').hidden || !$('registro-panel').hidden) cerrarDialogos();
  else cerrarSidebar();
});
document.querySelectorAll('[data-cerrar-auth]').forEach(b => b.addEventListener('click', () => cerrarDialogos()));
document.querySelectorAll('.auth-overlay').forEach(o => o.addEventListener('click', e => { if (e.target === o) cerrarDialogos(); }));
$('btn-ir-registro').addEventListener('click', () => abrirDialogo('registro-panel'));
$('btn-ir-login').addEventListener('click', () => abrirDialogo('login-panel'));

$('btn-cuenta').addEventListener('click', () => {
  if (!getToken()) return abrirDialogo('login-panel');
  if (!sidebarFijo()) abrirSidebar();
  $('toggle-alertas').focus();
});

function mensaje(id, texto, ok = false) {
  $(id).textContent = texto;
  $(id).classList.toggle('ok', ok);
}

async function enviarConBoton(form, accion) {
  const boton = form.querySelector('button[type="submit"]');
  boton.disabled = true;
  try { await accion(); } finally { boton.disabled = false; }
}

$('form-login').addEventListener('submit', e => {
  e.preventDefault();
  enviarConBoton(e.target, async () => {
    mensaje('auth-error', '');
    try {
      const res = await fetch(`${API}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: $('email').value.trim(), password: $('password').value }),
      });
      const data = await res.json();
      if (!res.ok) return mensaje('auth-error', data.error || 'No se pudo iniciar sesión');
      setToken(data.token);
      e.target.reset();
      cerrarDialogos();
      actualizarEstadoSesion();
    } catch {
      mensaje('auth-error', 'No pudimos conectar con el servidor. Inténtalo de nuevo.');
    }
  });
});

$('form-registro').addEventListener('submit', e => {
  e.preventDefault();
  enviarConBoton(e.target, async () => {
    mensaje('reg-error', '');
    const email = $('reg-email').value.trim(), password = $('reg-password').value, confirmar = $('reg-confirmar').value;
    if (!email || !password)    return mensaje('reg-error', 'Email y contraseña son requeridos');
    if (password.length < 8)    return mensaje('reg-error', 'La contraseña debe tener al menos 8 caracteres');
    if (password !== confirmar) return mensaje('reg-error', 'Las contraseñas no coinciden');
    try {
      const res = await fetch(`${API}/api/registro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email, password, confirmar_password: confirmar,
          username: $('reg-username').value.trim() || null,
          recibir_alertas: $('reg-alertas').checked,
        }),
      });
      const data = await res.json();
      if (!res.ok) return mensaje('reg-error', data.error || 'No se pudo crear la cuenta');
      e.target.reset();
      abrirDialogo('login-panel');
      $('email').value = email;
      $('password').focus();
      mensaje('auth-error', '¡Cuenta creada! Ahora inicia sesión.', true);
    } catch {
      mensaje('reg-error', 'No pudimos conectar con el servidor. Inténtalo de nuevo.');
    }
  });
});

async function fetchConToken(path, opciones = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opciones,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
  });
  if (res.status === 401 || res.status === 422) {   // token vencido o inválido
    removeToken();
    actualizarEstadoSesion();
    throw new Error('sesión expirada');
  }
  return res;
}

function actualizarEstadoSesion() {
  const logueado = !!getToken();
  $('btn-cuenta').textContent = logueado ? 'Mi cuenta' : 'Iniciar sesión';
  $('sidebar-sesion').hidden = !logueado;
  if (logueado) cargarPerfil();
}

async function cargarPerfil() {
  try {
    const perfil = await (await fetchConToken('/api/perfil')).json();
    $('cuenta-email').textContent = perfil.email;
    $('toggle-alertas').checked = !!perfil.recibir_alertas;
  } catch { /* sesión expirada: ya se cerró */ }
}

$('toggle-alertas').addEventListener('change', async e => {
  const activar = e.target.checked;
  try {
    const res = await fetchConToken('/api/perfil/alertas', { method: 'PATCH', body: JSON.stringify({ recibir_alertas: activar }) });
    if (!res.ok) throw new Error();
  } catch {
    e.target.checked = !activar;   // revertir si falló
  }
});

$('btn-cerrar-sesion').addEventListener('click', () => {
  removeToken();
  cerrarSidebar();
  actualizarEstadoSesion();
  $('btn-cuenta').focus();
});

// ═════════════ INICIO ═════════════
function cargarInicio() {
  imagenNasa('milky way night sky', 'hero-bg');
  imagenNasa('solar eclipse', 'dest-eclipse-img');
  imagenNasa('jupiter saturn conjunction', 'dest-conjuncion-img');
  imagenNasa('mars planet', 'dest-oposicion-img');
  imagenNasa('comet tail', 'dest-cometa-img');
  imagenNasa('telescope observatory night', 'herramienta-tel-img');

  actualizarHeroISS();
  setInterval(actualizarHeroISS, 30000);

  cargarDestacadoEclipse();
  cargarDestacadoConjuncion();
  cargarDestacadoOposicion();
  cargarDestacadoCometa();
  cargarPlanetasInicio();
  cargarImagenDia();
}

async function actualizarHeroISS() {
  try {
    const data = await getJSON('/api/iss');
    $('hero-iss-alt').textContent  = `${num(data.posicion.altitud)} km`;
    $('hero-iss-dist').textContent = `${num(data.distancia_desde_ciudad)} km`;
    $('hero-iss-sub').textContent  = 'Estación Espacial Internacional';
  } catch {
    $('hero-iss-sub').textContent = 'Sin conexión con el rastreador ahora mismo';
  }
}

function llenarDestacado(prefijo, { titulo, fecha = '', cuenta = '', tag = '', visible = false }) {
  const t = $(`dest-${prefijo}-titulo`);
  t.textContent = titulo;
  t.classList.remove('skeleton');
  $(`dest-${prefijo}-fecha`).textContent  = fecha;
  $(`dest-${prefijo}-cuenta`).textContent = cuenta;
  $(`dest-${prefijo}-tag`).textContent    = tag;
  $(`dest-${prefijo}-tag`).classList.toggle('si', visible);
}

async function cargarDestacadoEclipse() {
  try {
    const { eclipses } = await getJSON('/api/eclipses');
    const e = eclipses.find(x => x.visible_local) || eclipses[0];
    if (!e) return llenarDestacado('eclipse', { titulo: 'Sin eclipses próximos' });
    const tipo = e.tipo === 'Solar' && e.local ? e.local.tipo : e.subtipo;
    llenarDestacado('eclipse', {
      titulo:  `Eclipse ${e.tipo.toLowerCase()} ${tipo.toLowerCase()}`,
      fecha:   e.fecha_local,
      cuenta:  e.cuenta_regresiva.texto,
      tag:     e.visible_local ? `✓ Visible desde ${CIUDAD}` : `No visible desde ${CIUDAD}`,
      visible: e.visible_local,
    });
  } catch { llenarDestacado('eclipse', { titulo: 'No disponible por ahora' }); }
}

async function cargarDestacadoConjuncion() {
  try {
    const { conjunciones } = await getJSON('/api/conjunciones');
    const c = conjunciones.find(x => x.observable) || conjunciones[0];
    if (!c) return llenarDestacado('conjuncion', { titulo: 'Ninguna en los próximos meses' });
    llenarDestacado('conjuncion', {
      titulo:  `${c.planeta1} y ${c.planeta2}`,
      fecha:   c.fecha_local,
      cuenta:  c.cuenta_regresiva.texto,
      tag:     `Separación: ${num(c.separacion, 1)}°`,
      visible: c.observable,
    });
  } catch { llenarDestacado('conjuncion', { titulo: 'No disponible por ahora' }); }
}

async function cargarDestacadoOposicion() {
  try {
    const { oposiciones } = await getJSON('/api/oposiciones');
    const o = oposiciones[0];
    if (!o) return llenarDestacado('oposicion', { titulo: 'Ninguna próxima' });
    llenarDestacado('oposicion', {
      titulo:  `Oposición de ${o.planeta}`,
      fecha:   o.fecha_local,
      cuenta:  o.cuenta_regresiva.texto,
      tag:     `Magnitud ${num(o.magnitud, 1)} · ${o.simple_vista ? 'a simple vista' : 'con binoculares'}`,
      visible: o.simple_vista,
    });
  } catch { llenarDestacado('oposicion', { titulo: 'No disponible por ahora' }); }
}

async function cargarDestacadoCometa() {
  try {
    const { cometas } = await getJSON('/api/cometas');
    const c = cometas[0];
    if (!c) return llenarDestacado('cometa', { titulo: 'Sin cometas destacados' });
    llenarDestacado('cometa', {
      titulo: c.nombre,
      fecha:  `Perihelio: ${c.fecha_perihelio}`,
      cuenta: c.tiempo,
      tag:    c.visible_simple_vista ? 'Llegó a verse a simple vista' : (c.visible_binoculares ? 'Con binoculares' : 'Solo con telescopio'),
    });
  } catch { llenarDestacado('cometa', { titulo: 'No disponible por ahora' }); }
}

// Colores reales aproximados de cada planeta (precisión antes que paleta)
const COLORES_PLANETA = {
  Mercurio: 'radial-gradient(circle at 35% 35%, #d6d3d1, #78716c)',
  Venus:    'radial-gradient(circle at 35% 35%, #fef3c7, #d97706)',
  Marte:    'radial-gradient(circle at 35% 35%, #fca5a5, #b91c1c)',
  Júpiter:  'radial-gradient(circle at 35% 35%, #fde68a, #a16207)',
  Saturno:  'radial-gradient(circle at 35% 35%, #fef9c3, #ca8a04)',
};

function planetaMini(p) {
  return `
    <span class="planeta-mini">
      <span class="planeta-icono" style="background:${COLORES_PLANETA[p.planeta] || '#334155'}" aria-hidden="true"></span>
      <span class="planeta-nombre">${esc(p.planeta)}</span>
      <span class="planeta-estado">${num(p.altitud)}° · ${esc(p.direccion)}</span>
    </span>`;
}

async function cargarPlanetasInicio() {
  try {
    const data = await getJSON('/api/planetas');
    if (data.visibles_ahora && data.planetas?.length) {
      $('planetas-visibles-sub').textContent = 'Sobre el horizonte ahora mismo';
      $('planetas-visibles-grid').innerHTML  = data.planetas.map(planetaMini).join('');
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana;
      const motivo = data.cielo?.condicion === 'noche' ? 'Ninguno sobre el horizonte' : `Ahora es de ${data.cielo?.condicion || 'día'}`;
      $('planetas-visibles-sub').textContent = `${motivo}. Se verán desde las ${v.hora_local} (en ${horasTexto(v.en_minutos)})`;
      $('planetas-visibles-grid').innerHTML  = v.planetas.map(planetaMini).join('');
    } else {
      $('planetas-visibles-sub').textContent = 'Ningún planeta visible en las próximas horas.';
      $('planetas-visibles-grid').innerHTML  = '';
    }
  } catch {
    $('planetas-visibles-sub').textContent = 'No disponible por ahora.';
    $('planetas-visibles-grid').innerHTML  = '';
  }
}

async function cargarImagenDia() {
  try {
    const data = await getJSON('/api/imagen-dia');
    if (data.url)    $('imagen-dia-img').style.backgroundImage = `url('${data.url}')`;
    if (data.titulo) $('imagen-dia-titulo').textContent = data.titulo;
    if (data.pagina) $('card-imagen-dia').href = data.pagina;
  } catch {
    imagenNasa('nebula', 'imagen-dia-img');
  }
}

// ═════════════ SECCIONES ═════════════
async function cargarISS() {
  const id = 'iss-data';
  if (!$(id).children.length) $(id).innerHTML = cargandoHTML(2);
  try {
    const data = await getJSON('/api/iss');
    const pos  = data.posicion;
    $(id).innerHTML = `
      <div class="evento">
        <span class="dato-etiqueta">Distancia a ${esc(data.ciudad)} (sobre la superficie)</span>
        <span class="dato-grande">${num(data.distancia_desde_ciudad)} km</span>
        <div class="evento-datos">
          <span>Latitud <strong>${num(pos.lat, 2)}°</strong></span>
          <span>Longitud <strong>${num(pos.lon, 2)}°</strong></span>
          <span>Altitud <strong>${num(pos.altitud)} km</strong></span>
          <span>Velocidad <strong>${num(pos.velocidad)} km/h</strong></span>
        </div>
        <p class="evento-nota">Se actualiza cada vez que entras a esta sección.</p>
      </div>`;
  } catch { mostrarError(id, cargarISS); }
}

async function cargarPlanetas() {
  const id = 'planetas-data';
  if (!$(id).children.length) $(id).innerHTML = cargandoHTML();
  try {
    const data = await getJSON('/api/planetas');
    const fila = p => `
      <div class="evento">
        <div class="evento-fila">
          <span class="evento-titulo">${esc(p.planeta)}</span>
          <span class="estado estado-si">${num(p.altitud, 1)}° · ${esc(p.direccion)}</span>
        </div>
        <span class="evento-meta">Magnitud ${p.magnitud === null ? '—' : num(p.magnitud, 1)} · cuanto más bajo el número, más brillante</span>
      </div>`;
    if (data.visibles_ahora && data.planetas?.length) {
      $(id).innerHTML = data.planetas.map(fila).join('');
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana, cielo = data.cielo || {};
      const motivo = cielo.condicion === 'noche'
        ? 'Ahora no hay planetas sobre el horizonte.'
        : `Ahora es de ${cielo.condicion} en ${CIUDAD} (Sol a ${num(cielo.altura_sol, 1)}°): los planetas no se pueden ver.`;
      $(id).innerHTML = `
        <div class="evento">
          <p class="evento-nota">${motivo}</p>
          <span class="evento-titulo">Próxima ventana: ${esc(v.hora_local)} <span class="texto-sub">(en ${horasTexto(v.en_minutos)})</span></span>
        </div>` + v.planetas.map(fila).join('');
    } else {
      $(id).innerHTML = '<p class="texto-sub">No hay planetas visibles en las próximas horas. El cielo sigue su curso.</p>';
    }
  } catch { mostrarError(id, cargarPlanetas); }
}

async function cargarEclipses() {
  const id = 'eclipses-data';
  $(id).innerHTML = cargandoHTML(4);
  try {
    const { eclipses } = await getJSON('/api/eclipses');
    if (!eclipses.length) {
      $(id).innerHTML = '<p class="texto-sub">No hay eclipses en los próximos meses.</p>';
      return;
    }
    $(id).innerHTML = eclipses.map(e => {
      const cr  = e.cuenta_regresiva;
      const ico = e.tipo === 'Solar' ? '☀️' : '🌑';
      const horario = e.tipo === 'Solar' && e.local
        ? `<div class="evento-datos">
             <span>Empieza <strong>${esc(e.local.inicio)}</strong></span>
             <span>Máximo <strong>${esc(e.local.maximo)}</strong></span>
             <span>Termina <strong>${esc(e.local.fin)}</strong></span>
             <span>Sol cubierto <strong>${num(e.local.magnitud * 100)}%</strong> (diámetro)</span>
           </div>`
        : '';
      return `
        <article class="evento ${e.visible_local ? '' : 'evento-atenuado'}">
          <div class="evento-fila">
            <h2 class="evento-titulo"><span aria-hidden="true">${ico}</span> Eclipse ${e.tipo.toLowerCase()} ${e.subtipo.toLowerCase()}</h2>
            <span class="estado ${e.visible_local ? 'estado-si' : 'estado-no'}">${e.visible_local ? '✓ Visible desde ' + CIUDAD : 'No visible desde ' + CIUDAD}</span>
          </div>
          <span class="cuenta-grande">${cr.dias}d ${cr.horas}h ${cr.mins}m</span>
          <span class="evento-meta">${esc(e.fecha_local)} (hora de ${CIUDAD})</span>
          ${horario}
          <p class="evento-nota">${esc(e.descripcion)}</p>
        </article>`;
    }).join('');
  } catch { mostrarError(id, cargarEclipses); }
}

async function cargarConjunciones() {
  const id = 'conjunciones-data';
  $(id).innerHTML = cargandoHTML();
  try {
    const { conjunciones } = await getJSON('/api/conjunciones');
    $(id).innerHTML = !conjunciones.length
      ? '<p class="texto-sub">Ninguna conjunción notable en los próximos 4 meses. El cielo sigue su curso.</p>'
      : conjunciones.map(c => `
          <article class="evento ${c.observable ? '' : 'evento-atenuado'}">
            <div class="evento-fila">
              <h2 class="evento-titulo">${esc(c.planeta1)} y ${esc(c.planeta2)}</h2>
              <span class="estado ${c.observable ? 'estado-si' : 'estado-info'}">${c.observable ? 'Observable' : 'Muy cerca del Sol'}</span>
            </div>
            <div class="evento-datos">
              <span>Separación <strong>${num(c.separacion, 2)}°</strong></span>
              <span>Fecha <strong>${esc(c.fecha_local)}</strong></span>
              <span><strong>${esc(c.cuenta_regresiva.texto)}</strong></span>
            </div>
            <p class="evento-nota">${esc(c.nota)}</p>
          </article>`).join('');
  } catch { mostrarError(id, cargarConjunciones); }
}

async function cargarOposiciones() {
  const id = 'oposiciones-data';
  $(id).innerHTML = cargandoHTML();
  try {
    const { oposiciones } = await getJSON('/api/oposiciones');
    $(id).innerHTML = !oposiciones.length
      ? '<p class="texto-sub">No hay oposiciones próximas.</p>'
      : oposiciones.map(o => `
          <article class="evento">
            <div class="evento-fila">
              <h2 class="evento-titulo">${esc(o.planeta)}</h2>
              <span class="estado ${o.simple_vista ? 'estado-si' : 'estado-no'}">${esc(o.cuenta_regresiva.texto)}</span>
            </div>
            <div class="evento-datos">
              <span>Fecha <strong>${esc(o.fecha_local)}</strong></span>
              <span>Distancia <strong>${num(o.distancia_ua, 2)} UA</strong></span>
              <span>Magnitud <strong>${num(o.magnitud, 1)}</strong></span>
            </div>
            <p class="evento-nota">${esc(o.descripcion)}</p>
          </article>`).join('');
  } catch { mostrarError(id, cargarOposiciones); }
}

async function cargarCometas() {
  const id = 'cometas-data';
  $(id).innerHTML = cargandoHTML();
  try {
    const { cometas } = await getJSON('/api/cometas');
    if (!cometas.length) {
      $(id).innerHTML = '<p class="texto-sub">No hay cometas destacados en este momento.</p>';
      return;
    }
    $(id).innerHTML = `<p class="evento-meta">Datos verificados al ${esc(cometas[0].actualizado)}</p>` + cometas.map(c => {
      const vis = c.visible_simple_vista ? 'simple vista' : (c.visible_binoculares ? 'binoculares' : 'telescopio');
      const mag = c.magnitud_pico === null ? 'sin dato fiable' : `${num(c.magnitud_pico, 1)} (${vis})`;
      return `
        <article class="evento">
          <div class="evento-fila">
            <h2 class="evento-titulo">${esc(c.nombre)}</h2>
            <span class="estado estado-no">${esc(c.estado)}</span>
          </div>
          <div class="evento-datos">
            <span>Perihelio <strong>${esc(c.fecha_perihelio)}</strong></span>
            <span><strong>${esc(c.tiempo)}</strong></span>
            <span>Magnitud máx. <strong>${mag}</strong></span>
          </div>
          <p class="evento-nota">${esc(c.descripcion)}</p>
          <a href="${esc(c.fuente)}" target="_blank" rel="noopener" class="enlace">Fuente ↗</a>
        </article>`;
    }).join('');
  } catch { mostrarError(id, cargarCometas); }
}

async function cargarLunas() {
  const id = 'lunas-lista';
  $(id).innerHTML = cargandoHTML(5);
  try {
    const { lunas } = await getJSON('/api/lunas');
    $(id).innerHTML = lunas.map(l => `
      <button class="luna-btn" type="button" data-luna="${esc(l.id)}" aria-pressed="false" aria-controls="luna-detalle">
        <img src="${esc(l.imagen)}" alt="" loading="lazy">
        <span>
          <span class="luna-btn-nombre">${esc(l.nombre)}</span>
          <span class="luna-btn-planeta">${esc(l.planeta)}</span>
        </span>
      </button>`).join('');
    $(id).querySelectorAll('.luna-btn').forEach(b => b.addEventListener('click', () => verLuna(b)));
    conRespaldo($(id));
  } catch { mostrarError(id, cargarLunas); }
}

async function verLuna(boton) {
  document.querySelectorAll('.luna-btn').forEach(b => b.setAttribute('aria-pressed', String(b === boton)));
  const detalle = $('luna-detalle');
  detalle.innerHTML = cargandoHTML(4);
  try {
    const l = await getJSON(`/api/lunas/${encodeURIComponent(boton.dataset.luna)}`);
    const d = l.datos;
    const filas = [
      ['Diámetro', `${num(d.diametro_km)} km`], ['Distancia a su planeta', `${num(d.distancia_km)} km`],
      ['Período orbital', `${num(d.periodo_orbital_dias, 2)} días`], ['Temp. máxima', `${d.temperatura_max} °C`],
      ['Temp. mínima', `${d.temperatura_min} °C`], ['Gravedad', d.gravedad], ['Atmósfera', d.atmosfera],
    ];
    detalle.innerHTML = `
      <div class="luna-cabecera">
        <img src="${esc(l.imagen)}" alt="Fotografía de ${esc(l.nombre)}, luna de ${esc(l.planeta)}">
        <div>
          <h2 class="luna-titulo">${esc(l.nombre)} <span class="texto-sub">· ${esc(l.planeta)}</span></h2>
          <table class="tabla-datos"><tbody>
            ${filas.map(([k, v]) => `<tr><th scope="row">${k}</th><td>${esc(v)}</td></tr>`).join('')}
          </tbody></table>
        </div>
      </div>
      <div class="sub-panel"><h3 class="sub-panel-titulo">📖 Historia</h3><p class="texto-cuerpo">${esc(l.historia)}</p></div>
      <div class="sub-panel"><h3 class="sub-panel-titulo">✨ Curiosidades</h3>${l.curiosidades.map(c => `<p class="curiosidad">${esc(c)}</p>`).join('')}</div>
      <div class="sub-panel"><h3 class="sub-panel-titulo">🚀 Exploración</h3><p class="texto-cuerpo">${esc(l.exploracion)}</p></div>`;
    conRespaldo(detalle);
  } catch {
    mostrarError('luna-detalle', () => verLuna(boton));
  }
}

$('form-telescopio').addEventListener('submit', e => {
  e.preventDefault();
  enviarConBoton(e.target, calcularTelescopio);
});

async function calcularTelescopio() {
  const campos = ['tel-apertura', 'tel-focal', 'tel-ocular'];
  campos.forEach(c => $(c).removeAttribute('aria-invalid'));
  const vacios = campos.filter(c => !$(c).value);
  if (vacios.length) {
    vacios.forEach(c => $(c).setAttribute('aria-invalid', 'true'));
    $(vacios[0]).focus();
    return mensaje('tel-error', 'Ingresa la apertura, la focal del telescopio y la focal del ocular.');
  }
  mensaje('tel-error', '');
  try {
    const res = await fetch(`${API}/api/telescopio`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apertura_mm:         parseFloat($('tel-apertura').value),
        focal_telescopio_mm: parseFloat($('tel-focal').value),
        focal_ocular_mm:     parseFloat($('tel-ocular').value),
        afov:                parseFloat($('tel-afov').value || 52),
      }),
    });
    const data = await res.json();
    if (!res.ok) return mensaje('tel-error', data.error || 'No se pudo calcular');
    const r = data.resultados;
    $('tel-mag').textContent    = `${num(r.magnificacion, 1)}x`;
    $('tel-campo').textContent  = `${num(r.campo_visual, 2)}°`;
    $('tel-pupila').textContent = `${num(r.pupila_salida, 1)} mm`;
    $('tel-limite').textContent = num(r.limite_magnitud, 1);
    $('tel-min').textContent    = `${r.mag_minima_util}x`;
    $('tel-max').textContent    = `${r.mag_maxima_util}x`;
    $('tel-objetos').textContent = data.objetos_recomendados.join(' · ');
    $('tel-advertencias').innerHTML = data.advertencias.map(a => `<p class="curiosidad">${esc(a)}</p>`).join('');
    $('tel-advertencias-box').hidden = !data.advertencias.length;
    $('telescopio-resultado').hidden = false;
  } catch {
    mensaje('tel-error', 'No pudimos conectar con el servidor. Inténtalo de nuevo.');
  }
}

function cargarImagenTelescopio() {
  imagenNasa('telescope night sky stars observatory', 'telescopio-bg-img');
}

// ═════════════ FONDO ESPACIAL (decorativo) ═════════════
const ICONOS_ESPACIO = [
  '<svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 2l1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z"/></svg>',
  '<svg viewBox="0 0 24 24" width="28" height="28"><circle cx="12" cy="12" r="5"/><ellipse cx="12" cy="12" rx="11" ry="3"/></svg>',
  '<svg viewBox="0 0 24 24" width="26" height="26"><circle cx="17" cy="7" r="3"/><path d="M14 10 L4 20 M12 8 L2 18 M16 12 L6 22"/></svg>',
  '<svg viewBox="0 0 24 24" width="18" height="18"><path d="M15 4a8 8 0 100 16 8 8 0 01-8-8 8 8 0 018-8z"/></svg>',
  '<svg viewBox="0 0 24 24" width="10" height="10"><path d="M12 4v16M4 12h16"/></svg>',
  '<svg viewBox="0 0 24 24" width="24" height="24"><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 11H4M15 11h5M9 13H4M15 13h5"/><path d="M5 5l3 3M19 5l-3 3"/></svg>',
];

function generarFondoEspacial() {
  $('space-bg').innerHTML = Array.from({ length: 18 }, () => {
    const icono = ICONOS_ESPACIO[Math.floor(Math.random() * ICONOS_ESPACIO.length)];
    return `<div style="position:absolute;top:${Math.random() * 100}%;left:${Math.random() * 100}%;transform:rotate(${Math.random() * 360}deg)">${icono}</div>`;
  }).join('');
}

// ═════════════ ARRANQUE ═════════════
generarFondoEspacial();
actualizarEstadoSesion();
mostrarVista(location.pathname, { enfocar: false });
cargarInicio();
