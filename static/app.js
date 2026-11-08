// La API vive en el mismo servidor que sirve esta página (Flask).
// En local apunta a http://localhost:5000 y en producción a Render, sin cambiar código.
const API = '';

function getToken()    { return localStorage.getItem('token'); }
function setToken(t)   { localStorage.setItem('token', t); }
function removeToken() { localStorage.removeItem('token'); }

async function getJSON(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

// ── RIPPLE ──
document.addEventListener('click', function(e) {
  const btn = e.target.closest('.ripple');
  if (!btn) return;
  const circle = document.createElement('span');
  const rect   = btn.getBoundingClientRect();
  const size   = Math.max(rect.width, rect.height);
  circle.classList.add('ripple-effect');
  circle.style.width  = circle.style.height = size + 'px';
  circle.style.left   = e.clientX - rect.left - size/2 + 'px';
  circle.style.top    = e.clientY - rect.top  - size/2 + 'px';
  btn.appendChild(circle);
  setTimeout(() => circle.remove(), 600);
});

// ── SIDEBAR ──
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('active');
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('active');
}

// ── NAVEGACIÓN ──
const SECCIONES = ['iss', 'planetas', 'eclipses', 'conjunciones', 'lunas', 'oposiciones', 'cometas', 'telescopio', 'proximamente'];
const cargados  = {};

const CARGADORES = {
  iss:          cargarISS,
  planetas:     cargarPlanetas,
  eclipses:     cargarEclipses,
  conjunciones: cargarConjunciones,
  lunas:        cargarLunas,
  oposiciones:  cargarOposiciones,
  cometas:      cargarCometas,
  telescopio:   cargarImagenTelescopio,
};

function ocultarSecciones() {
  SECCIONES.forEach(s => document.getElementById(`sec-${s}`).classList.add('hidden'));
}

function irSeccion(seccion) {
  closeSidebar();
  if (!SECCIONES.includes(seccion)) seccion = 'proximamente';

  document.getElementById('inicio').classList.add('hidden');
  ocultarSecciones();
  document.getElementById(`sec-${seccion}`).classList.remove('hidden');
  window.scrollTo({ top: 0 });

  // La ISS se mueve: se recarga siempre. El resto se carga una sola vez.
  if (CARGADORES[seccion] && (seccion === 'iss' || !cargados[seccion])) {
    cargados[seccion] = true;
    CARGADORES[seccion]();
  }
}

function volverMenu() {
  closeSidebar();
  ocultarSecciones();
  document.getElementById('inicio').classList.remove('hidden');
  window.scrollTo({ top: 0 });
}

// ── AUTENTICACIÓN (opcional) ──
// La app es pública. La cuenta solo sirve para recibir alertas por correo.
function abrirLogin() {
  if (getToken()) { toggleSidebar(); return; }
  document.getElementById('login-panel').classList.remove('hidden');
}

function cerrarAuth() {
  document.getElementById('login-panel').classList.add('hidden');
  document.getElementById('registro-panel').classList.add('hidden');
}

function volverLogin() {
  document.getElementById('registro-panel').classList.add('hidden');
  document.getElementById('login-panel').classList.remove('hidden');
  document.getElementById('reg-error').textContent = '';
}

function irARegistro() {
  document.getElementById('login-panel').classList.add('hidden');
  document.getElementById('registro-panel').classList.remove('hidden');
}

async function login() {
  const email    = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const error    = document.getElementById('auth-error');
  error.style.color = '';
  error.textContent = '';
  try {
    const res  = await fetch(`${API}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) { error.textContent = data.error || 'No se pudo iniciar sesión'; return; }
    setToken(data.token);
    cerrarAuth();
    actualizarEstadoSesion();
  } catch {
    error.textContent = 'No pudimos conectar con el servidor. Inténtalo de nuevo.';
  }
}

async function registrarse() {
  const error = document.getElementById('reg-error');
  error.textContent = '';
  const email     = document.getElementById('reg-email').value.trim();
  const password  = document.getElementById('reg-password').value;
  const confirmar = document.getElementById('reg-confirmar').value;
  const username  = document.getElementById('reg-username').value.trim();

  if (!email || !password || !confirmar) { error.textContent = 'Email y contraseña requeridos'; return; }
  if (password !== confirmar)            { error.textContent = 'Las contraseñas no coinciden'; return; }
  if (password.length < 8)               { error.textContent = 'La contraseña debe tener al menos 8 caracteres'; return; }

  try {
    const res = await fetch(`${API}/api/registro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, confirmar_password: confirmar, username: username || null })
    });
    const data = await res.json();
    if (!res.ok) { error.textContent = data.error || 'No se pudo crear la cuenta'; return; }
    volverLogin();
    const ok = document.getElementById('auth-error');
    ok.style.color = '#34d399';
    ok.textContent = '¡Cuenta creada! Ahora inicia sesión.';
  } catch {
    error.textContent = 'No pudimos conectar con el servidor. Inténtalo de nuevo.';
  }
}

function cerrarSesion() {
  removeToken();
  closeSidebar();
  actualizarEstadoSesion();
}

function actualizarEstadoSesion() {
  const logueado = !!getToken();
  document.getElementById('btn-cuenta').textContent = logueado ? 'Mi cuenta' : 'Iniciar sesión';
  document.getElementById('sidebar-sesion').classList.toggle('hidden', !logueado);
}

// ── UTILIDADES ──
const fmt = n => Number(n).toLocaleString('es-EC');

function errorHTML(id) {
  document.getElementById(id).innerHTML =
    '<div class="card-sub">No pudimos obtener esta información ahora mismo. Inténtalo de nuevo en unos minutos.</div>';
}

async function imagenNasa(query, elementId) {
  try {
    const data  = await fetch(`https://images-api.nasa.gov/search?q=${encodeURIComponent(query)}&media_type=image`).then(r => r.json());
    const items = data.collection?.items || [];
    if (!items.length) return;
    const item = items[Math.floor(Math.random() * Math.min(items.length, 10))];
    const link = item.links?.find(l => l.rel === 'preview');
    const el   = document.getElementById(elementId);
    if (link && el) el.style.backgroundImage = `url('${link.href}')`;
  } catch { /* la imagen es decorativa: si falla, la tarjeta se ve igual */ }
}

// ══════════════════════════════════════════
//  INICIO
// ══════════════════════════════════════════
async function cargarInicio() {
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
    document.getElementById('hero-iss-alt').textContent  = `${fmt(Math.round(data.posicion.altitud))} km`;
    document.getElementById('hero-iss-dist').textContent = `${fmt(Math.round(data.distancia_desde_ciudad))} km`;
  } catch {
    document.getElementById('hero-iss-sub').textContent = 'Sin conexión con el rastreador';
  }
}

function llenarDestacado(prefijo, { titulo, fecha, cuenta, tag }) {
  document.getElementById(`dest-${prefijo}-titulo`).textContent = titulo;
  document.getElementById(`dest-${prefijo}-fecha`).textContent  = fecha || '';
  document.getElementById(`dest-${prefijo}-cuenta`).textContent = cuenta || '';
  document.getElementById(`dest-${prefijo}-tag`).textContent    = tag || '';
}

async function cargarDestacadoEclipse() {
  try {
    const { eclipses } = await getJSON('/api/eclipses');
    const e = eclipses[0];
    if (!e) return llenarDestacado('eclipse', { titulo: 'Sin eclipses próximos' });
    llenarDestacado('eclipse', {
      titulo: `Eclipse ${e.tipo.toLowerCase()} ${e.subtipo.toLowerCase()}`,
      fecha:  e.fecha_local,
      cuenta: e.cuenta_regresiva.texto,
      tag:    e.visible_quito ? '✓ Visible desde Quito' : 'No visible desde Quito',
    });
  } catch { llenarDestacado('eclipse', { titulo: 'No disponible' }); }
}

async function cargarDestacadoConjuncion() {
  try {
    const { conjunciones } = await getJSON('/api/conjunciones');
    const c = [...conjunciones].sort((a, b) => a.timestamp - b.timestamp)[0];
    if (!c) return llenarDestacado('conjuncion', { titulo: 'Ninguna en los próximos 90 días' });
    llenarDestacado('conjuncion', {
      titulo: `${c.planeta1} y ${c.planeta2}`,
      fecha:  c.fecha_local,
      cuenta: c.cuenta_regresiva.texto,
      tag:    `Separación: ${c.separacion}°`,
    });
  } catch { llenarDestacado('conjuncion', { titulo: 'No disponible' }); }
}

async function cargarDestacadoOposicion() {
  try {
    const { oposiciones } = await getJSON('/api/oposiciones');
    const o = oposiciones[0];
    if (!o) return llenarDestacado('oposicion', { titulo: 'Ninguna este año' });
    llenarDestacado('oposicion', {
      titulo: `Oposición de ${o.planeta}`,
      fecha:  o.fecha_local,
      cuenta: o.cuenta_regresiva.texto,
      tag:    `A ${o.distancia_ua} UA de la Tierra`,
    });
  } catch { llenarDestacado('oposicion', { titulo: 'No disponible' }); }
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
      tag:    c.visible_simple_vista ? 'Llegó a verse a simple vista' : (c.visible_binoculares ? 'Con binoculares' : 'Con telescopio'),
    });
  } catch { llenarDestacado('cometa', { titulo: 'No disponible' }); }
}

const COLORES_PLANETA = {
  Mercurio: 'radial-gradient(circle at 35% 35%, #d6d3d1, #78716c)',
  Venus:    'radial-gradient(circle at 35% 35%, #fef3c7, #d97706)',
  Marte:    'radial-gradient(circle at 35% 35%, #fca5a5, #b91c1c)',
  Jupiter:  'radial-gradient(circle at 35% 35%, #fde68a, #a16207)',
  Júpiter:  'radial-gradient(circle at 35% 35%, #fde68a, #a16207)',
  Saturno:  'radial-gradient(circle at 35% 35%, #fef9c3, #ca8a04)',
};

function planetaMini(p, estado) {
  return `
    <div class="planeta-mini">
      <div class="planeta-mini-icono" style="background:${COLORES_PLANETA[p.planeta] || '#334155'}"></div>
      <div class="planeta-mini-nombre">${p.planeta}</div>
      <div class="planeta-mini-estado">${estado}</div>
    </div>`;
}

async function cargarPlanetasInicio() {
  const grid = document.getElementById('planetas-visibles-grid');
  const sub  = document.getElementById('planetas-visibles-sub');
  try {
    const data = await getJSON('/api/planetas');
    if (data.visibles_ahora && data.planetas?.length) {
      sub.textContent = 'Sobre el horizonte ahora mismo';
      grid.innerHTML  = data.planetas.map(p => planetaMini(p, `${p.altitud}° · ${p.direccion}`)).join('');
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana;
      sub.textContent = `Ninguno ahora. Próxima ventana a las ${v.hora_local} (en ${v.en_horas} h)`;
      grid.innerHTML  = v.planetas.map(p => planetaMini(p, `${p.altitud}° · ${p.direccion}`)).join('');
    } else {
      sub.textContent = 'Ningún planeta visible en las próximas horas.';
      grid.innerHTML  = '';
    }
  } catch {
    grid.innerHTML = '<div class="card-sub">No disponible por ahora.</div>';
  }
}

let urlImagenDia = 'https://apod.nasa.gov/apod/astropix.html';

async function cargarImagenDia() {
  try {
    const data = await getJSON('/api/imagen-dia');
    if (data.url) document.getElementById('imagen-dia-img').style.backgroundImage = `url('${data.url}')`;
    if (data.titulo) document.getElementById('imagen-dia-titulo').textContent = data.titulo;
    if (data.pagina) urlImagenDia = data.pagina;
  } catch {
    imagenNasa('nebula', 'imagen-dia-img');
  }
}

function abrirImagenDia() {
  window.open(urlImagenDia, '_blank', 'noopener');
}

// ══════════════════════════════════════════
//  SECCIONES
// ══════════════════════════════════════════
async function cargarISS() {
  try {
    const data = await getJSON('/api/iss');
    const pos  = data.posicion;
    document.getElementById('iss-data').innerHTML = `
      <div class="card-value">A <strong>${fmt(data.distancia_desde_ciudad)} km</strong> de ${data.ciudad}</div>
      <div class="card-sub">Lat ${pos.lat} · Lon ${pos.lon} · Altitud ${pos.altitud} km</div>
      <div class="card-sub">Velocidad: ${fmt(pos.velocidad)} km/h</div>`;
  } catch { errorHTML('iss-data'); }
}

async function cargarPlanetas() {
  try {
    const data = await getJSON('/api/planetas');
    let html;
    if (data.visibles_ahora && data.planetas?.length) {
      html = data.planetas.map(p =>
        `<div class="conj-item"><div class="card-value">${p.planeta} — ${p.altitud}° de altura hacia el ${p.direccion}</div></div>`
      ).join('');
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana;
      html = `<div class="card-value">Próxima ventana: <strong>${v.hora_local}</strong></div>
              <div class="card-sub">En ${v.en_horas} h · ${v.planetas.map(p => p.planeta).join(', ')}</div>`;
    } else {
      html = '<div class="card-sub">No hay planetas visibles en las próximas horas. El cielo sigue su curso.</div>';
    }
    document.getElementById('planetas-data').innerHTML = html;
  } catch { errorHTML('planetas-data'); }
}

async function cargarEclipses() {
  try {
    const { eclipses } = await getJSON('/api/eclipses');
    if (!eclipses.length) {
      document.getElementById('eclipses-data').innerHTML = '<div class="card-sub">No hay eclipses en los próximos meses.</div>';
      return;
    }
    document.getElementById('eclipses-data').innerHTML = eclipses.map(e => {
      const cr  = e.cuenta_regresiva;
      const vis = e.visible_quito ? '✓ visible desde Quito' : 'no visible desde Quito';
      const ico = e.tipo === 'Solar' ? '☀️' : '🌑';
      return `
        <div class="conj-item">
          <div class="card-value">${ico} Eclipse ${e.tipo.toLowerCase()} ${e.subtipo.toLowerCase()}</div>
          <div class="cuenta-grande">${cr.dias}d ${cr.horas}h ${cr.mins}m</div>
          <div class="card-sub">${e.fecha_local} · ${vis}</div>
        </div>`;
    }).join('');
  } catch { errorHTML('eclipses-data'); }
}

async function cargarConjunciones() {
  try {
    const { conjunciones } = await getJSON('/api/conjunciones');
    const lista = [...conjunciones].sort((a, b) => a.timestamp - b.timestamp);
    document.getElementById('conjunciones-data').innerHTML = !lista.length
      ? '<div class="card-sub">Ninguna conjunción notable en los próximos 90 días.</div>'
      : lista.map(c => `
          <div class="conj-item">
            <div class="card-value">✨ ${c.planeta1} y ${c.planeta2}</div>
            <div class="card-sub">Separación: ${c.separacion}° · ${c.fecha_local} · ${c.cuenta_regresiva.texto}</div>
          </div>`).join('');
  } catch { errorHTML('conjunciones-data'); }
}

async function cargarOposiciones() {
  try {
    const { oposiciones } = await getJSON('/api/oposiciones');
    document.getElementById('oposiciones-data').innerHTML = !oposiciones.length
      ? '<div class="card-sub">No hay oposiciones en los próximos 12 meses.</div>'
      : oposiciones.map(o => `
          <div class="conj-item">
            <div class="opos-row">
              <div>
                <div class="card-value">🔴 ${o.planeta}</div>
                <div class="card-sub">${o.fecha_local}</div>
              </div>
              <div class="opos-badge">${o.cuenta_regresiva.texto}</div>
            </div>
            <div class="opos-datos">
              <span>Distancia: <strong>${o.distancia_ua} UA</strong></span>
              <span>Elongación: <strong>${o.elongacion}°</strong></span>
            </div>
            <div class="card-sub texto-italico">${o.descripcion}</div>
          </div>`).join('');
  } catch { errorHTML('oposiciones-data'); }
}

async function cargarCometas() {
  try {
    const { cometas } = await getJSON('/api/cometas');
    document.getElementById('cometas-data').innerHTML = !cometas.length
      ? '<div class="card-sub">No hay cometas destacados en este momento.</div>'
      : cometas.map(c => {
          const vis = c.visible_simple_vista ? '👁 simple vista' : (c.visible_binoculares ? '🔭 binoculares' : '📡 telescopio');
          return `
            <div class="conj-item">
              <div class="opos-row">
                <div class="card-value">☄️ ${c.nombre}</div>
                <div class="opos-badge">${c.estado}</div>
              </div>
              <div class="card-sub">Perihelio: ${c.fecha_perihelio} · ${c.tiempo} · Magnitud máx. ${c.magnitud_pico} (${vis})</div>
              <div class="card-sub texto-italico">${c.descripcion}</div>
            </div>`;
        }).join('');
  } catch { errorHTML('cometas-data'); }
}

async function cargarLunas() {
  try {
    const { lunas } = await getJSON('/api/lunas');
    document.getElementById('lunas-lista').innerHTML = lunas.map(l => `
      <button class="luna-btn ripple" onclick="verLuna('${l.id}', this)">
        <img src="${l.imagen}" alt="${l.nombre}" loading="lazy">
        <div class="luna-btn-info">
          <div class="luna-btn-nombre">${l.nombre}</div>
          <div class="luna-btn-planeta">${l.planeta}</div>
        </div>
      </button>`).join('');
  } catch { errorHTML('lunas-lista'); }
}

async function verLuna(id, btn) {
  document.querySelectorAll('.luna-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const detalle = document.getElementById('luna-detalle');
  detalle.innerHTML = '<div class="card-sub" style="text-align:center;padding:20px">Cargando...</div>';
  try {
    const l = await getJSON(`/api/lunas/${id}`);
    const d = l.datos;
    detalle.innerHTML = `
      <div class="luna-top-row">
        <div class="luna-img-cuadrado"><img src="${l.imagen}" alt="${l.nombre}"></div>
        <div class="luna-datos-cuadrado">
          <div class="luna-seccion-titulo" style="margin-bottom:10px">📊 Datos</div>
          <div class="luna-dato"><span>Diámetro</span><span>${fmt(d.diametro_km)} km</span></div>
          <div class="luna-dato"><span>Distancia</span><span>${fmt(d.distancia_km)} km</span></div>
          <div class="luna-dato"><span>Período</span><span>${d.periodo_orbital_dias} días</span></div>
          <div class="luna-dato"><span>Temp. máx</span><span>${d.temperatura_max}°C</span></div>
          <div class="luna-dato"><span>Temp. mín</span><span>${d.temperatura_min}°C</span></div>
          <div class="luna-dato"><span>Gravedad</span><span>${d.gravedad}</span></div>
          <div class="luna-dato"><span>Atmósfera</span><span>${d.atmosfera}</span></div>
        </div>
      </div>
      <div class="luna-seccion">
        <div class="luna-seccion-titulo">📖 Historia</div>
        <div class="luna-seccion-texto">${l.historia}</div>
      </div>
      <div class="luna-seccion">
        <div class="luna-seccion-titulo">✨ Curiosidades</div>
        ${l.curiosidades.map(c => `<div class="curiosidad">${c}</div>`).join('')}
      </div>
      <div class="luna-seccion">
        <div class="luna-seccion-titulo">🚀 Exploración</div>
        <div class="luna-seccion-texto">${l.exploracion}</div>
      </div>`;
  } catch {
    detalle.innerHTML = '<div class="card-sub">No pudimos cargar esta luna. Inténtalo de nuevo.</div>';
  }
}

async function calcularTelescopio() {
  const apertura = document.getElementById('tel-apertura').value;
  const focal    = document.getElementById('tel-focal').value;
  const ocular   = document.getElementById('tel-ocular').value;
  const afov     = document.getElementById('tel-afov').value || 52;
  const error    = document.getElementById('tel-error');
  error.textContent = '';

  if (!apertura || !focal || !ocular) {
    error.textContent = 'Ingresa la apertura, la focal del telescopio y la focal del ocular.';
    return;
  }

  try {
    const res  = await fetch(`${API}/api/telescopio`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apertura_mm:         parseFloat(apertura),
        focal_telescopio_mm: parseFloat(focal),
        focal_ocular_mm:     parseFloat(ocular),
        afov:                parseFloat(afov)
      })
    });
    const data = await res.json();
    if (!res.ok) { error.textContent = data.error || 'No se pudo calcular'; return; }
    const r = data.resultados;

    document.getElementById('tel-mag').textContent    = r.magnificacion + 'x';
    document.getElementById('tel-campo').textContent  = r.campo_visual + '°';
    document.getElementById('tel-pupila').textContent = r.pupila_salida + ' mm';
    document.getElementById('tel-limite').textContent = r.limite_magnitud;
    document.getElementById('tel-min').textContent    = r.mag_minima_util + 'x';
    document.getElementById('tel-max').textContent    = r.mag_maxima_util + 'x';
    document.getElementById('tel-objetos').textContent = data.objetos_recomendados.join(' · ');

    const advBox = document.getElementById('tel-advertencias-box');
    if (data.advertencias.length > 0) {
      document.getElementById('tel-advertencias').innerHTML =
        data.advertencias.map(a => `<div class="curiosidad" style="border-color:rgba(219,112,147,0.45)">${a}</div>`).join('');
      advBox.classList.remove('hidden');
    } else {
      advBox.classList.add('hidden');
    }
    document.getElementById('telescopio-resultado').classList.remove('hidden');
  } catch {
    error.textContent = 'No pudimos conectar con el servidor. Inténtalo de nuevo.';
  }
}

function cargarImagenTelescopio() {
  imagenNasa('telescope night sky stars observatory', 'telescopio-bg-img');
}

// ── FONDO ESPACIAL ──
const ICONOS_ESPACIO = [
  `<svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 2l1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z"/></svg>`,
  `<svg viewBox="0 0 24 24" width="28" height="28"><circle cx="12" cy="12" r="5"/><ellipse cx="12" cy="12" rx="11" ry="3"/></svg>`,
  `<svg viewBox="0 0 24 24" width="26" height="26"><circle cx="17" cy="7" r="3"/><path d="M14 10 L4 20 M12 8 L2 18 M16 12 L6 22"/></svg>`,
  `<svg viewBox="0 0 24 24" width="18" height="18"><path d="M15 4a8 8 0 100 16 8 8 0 01-8-8 8 8 0 018-8z"/></svg>`,
  `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 2c2 2 3 5 3 9s-1 7-3 9c-2-2-3-5-3-9s1-7 3-9z"/><path d="M9 14l-3 3v3l3-1M15 14l3 3v3l-3-1"/></svg>`,
  `<svg viewBox="0 0 24 24" width="10" height="10"><path d="M12 4v16M4 12h16"/></svg>`,
  `<svg viewBox="0 0 24 24" width="24" height="24"><circle cx="12" cy="12" r="5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/></svg>`,
  `<svg viewBox="0 0 24 24" width="24" height="24"><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 11H4M15 11h5M9 13H4M15 13h5"/><path d="M5 5l3 3M19 5l-3 3"/></svg>`,
];

function generarFondoEspacial() {
  const bg = document.getElementById('space-bg');
  if (!bg) return;
  let html = '';
  for (let i = 0; i < 22; i++) {
    const icono = ICONOS_ESPACIO[Math.floor(Math.random() * ICONOS_ESPACIO.length)];
    html += `<div style="position:absolute;top:${Math.random()*100}%;left:${Math.random()*100}%;transform:rotate(${Math.random()*360}deg)">${icono}</div>`;
  }
  bg.innerHTML = html;
}

// ── INIT ──
generarFondoEspacial();
actualizarEstadoSesion();
cargarInicio();
