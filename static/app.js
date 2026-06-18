const API = 'https://astroalert-pgyw.onrender.com';

function getToken()    { return localStorage.getItem('token'); }
function setToken(t)   { localStorage.setItem('token', t); }
function removeToken() { localStorage.removeItem('token'); }

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

function expandirSub(id) {
  const sub   = document.getElementById(id);
  const arrow = document.getElementById('arrow-' + id);
  sub.classList.toggle('hidden');
  arrow.classList.toggle('rotado');
}

// ── NAVEGACIÓN ──
const secciones = ['iss', 'planetas', 'eclipses', 'conjunciones', 'lunas', 'oposiciones', 'proximamente'];
const cargados  = {};

function irSeccion(seccion) {
  closeSidebar();

  // Ocultar carrusel y grid cuando se abre una sección
  const seccEnContenido = ['iss','planetas','eclipses','conjunciones','lunas', 'oposiciones'];
  const tieneContenido  = seccEnContenido.includes(seccion);

  document.querySelector('.carrusel-wrapper').style.display = tieneContenido ? 'none' : 'block';
  document.querySelector('.cards-grid').style.display       = tieneContenido ? 'none' : 'grid';

  secciones.forEach(s => document.getElementById(`sec-${s}`) && document.getElementById(`sec-${s}`).classList.add('hidden'));

  const secEl = document.getElementById(`sec-${seccion}`) || document.getElementById('sec-proximamente');
  if (secEl) secEl.classList.remove('hidden');

  if (!cargados[seccion]) {
    cargados[seccion] = true;
    if (seccion === 'iss')          cargarISS();
    if (seccion === 'planetas')     cargarPlanetas();
    if (seccion === 'eclipses')     cargarEclipses();
    if (seccion === 'conjunciones') cargarConjunciones();
    if (seccion === 'lunas')        cargarLunas();
    if (seccion === 'oposiciones')  cargarOposiciones();
}
}

function volverMenu() {
  secciones.forEach(s => {
    const el = document.getElementById(`sec-${s}`);
    if (el) el.classList.add('hidden');
  });
  document.getElementById('luna-detalle').innerHTML = `
    <div class="card-sub" style="text-align:center;padding:20px">Selecciona una luna</div>
  `;
  document.getElementById('lunas-lista').innerHTML = '';
  Object.keys(cargados).forEach(k => delete cargados[k]);
  document.querySelector('.carrusel-wrapper').style.display = 'block';
  document.querySelector('.cards-grid').style.display = 'grid';
}

// ── AUTH ──
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
  const email    = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const error    = document.getElementById('auth-error');
  const res  = await fetch(`${API}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (!res.ok) { error.textContent = data.error; return; }
  setToken(data.token);
  mostrarApp();
}

async function registrarse() {
  const error = document.getElementById('reg-error');
  error.textContent = '';
  const email     = document.getElementById('reg-email').value.trim();
  const password  = document.getElementById('reg-password').value;
  const confirmar = document.getElementById('reg-confirmar').value;
  const username  = document.getElementById('reg-username').value.trim();
  const dia       = document.getElementById('reg-dia').value.padStart(2,'0');
  const mes       = document.getElementById('reg-mes').value.padStart(2,'0');
  const anio      = document.getElementById('reg-anio').value;
  const codigo    = document.getElementById('reg-codigo').value;
  const telefono  = document.getElementById('reg-telefono').value.trim();

  if (!email || !password || !confirmar) { error.textContent = 'Email y contraseña requeridos'; return; }
  if (password !== confirmar)            { error.textContent = 'Las contraseñas no coinciden'; return; }
  if (password.length < 6)              { error.textContent = 'Mínimo 6 caracteres'; return; }

  let fecha_nacimiento = null;
  if (dia && mes && anio) {
    const fechaStr = `${anio}-${mes}-${dia}`;
    const fecha    = new Date(fechaStr);
    if (isNaN(fecha.getTime()) || fecha.getMonth() + 1 !== parseInt(mes)) {
      error.textContent = 'Fecha inválida'; return;
    }
    fecha_nacimiento = fechaStr;
  }

  if (telefono && !/^\d{7,15}$/.test(telefono)) { error.textContent = 'Teléfono inválido'; return; }

  const res = await fetch(`${API}/api/registro`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, confirmar_password: confirmar, username, fecha_nacimiento, telefono_codigo: codigo, telefono_numero: telefono })
  });
  const data = await res.json();
  if (!res.ok) { error.textContent = data.error; return; }
  volverLogin();
  document.getElementById('auth-error').style.color = '#34d399';
  document.getElementById('auth-error').textContent = '¡Cuenta creada! Ahora inicia sesión.';
}

function cerrarSesion() {
  removeToken();
  closeSidebar();
  document.getElementById('main-panel').classList.add('hidden');
  document.getElementById('login-panel').classList.remove('hidden');
}

function mostrarApp() {
  document.getElementById('login-panel').classList.add('hidden');
  document.getElementById('registro-panel').classList.add('hidden');
  const transicion = document.getElementById('transicion-panel');
  transicion.classList.remove('hidden');
  setTimeout(() => {
    transicion.classList.add('hidden');
    document.getElementById('main-panel').classList.remove('hidden');
    iniciarCarrusel();
  }, 2000);
}

// ── CARRUSEL ──
function iniciarCarrusel() {
  const carrusel = document.getElementById('carrusel');
  const dots     = document.getElementById('carrusel-dots');
  const items    = carrusel.querySelectorAll('.carrusel-item');
  let actual     = 0;

  dots.innerHTML = '';
  items.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.className = 'dot' + (i === 0 ? ' active' : '');
    dot.onclick = () => irSlide(i);
    dots.appendChild(dot);
  });

  function irSlide(i) {
    actual = i;
    carrusel.scrollTo({ left: carrusel.offsetWidth * i, behavior: 'smooth' });
    dots.querySelectorAll('.dot').forEach((d, idx) => d.classList.toggle('active', idx === i));
  }

  // Auto-scroll cada 4 segundos
  setInterval(() => irSlide((actual + 1) % items.length), 8000);

  carrusel.addEventListener('scroll', () => {
    const i = Math.round(carrusel.scrollLeft / carrusel.offsetWidth);
    if (i !== actual) {
      actual = i;
      dots.querySelectorAll('.dot').forEach((d, idx) => d.classList.toggle('active', idx === i));
    }
  });
}

// ── DATOS ──
async function cargarISS() {
  try {
    const res  = await fetch(`${API}/api/iss`);
    const data = await res.json();
    const pos  = data.posicion;
    document.getElementById('iss-data').innerHTML = `
      <div class="card-value">A <strong>${data.distancia_desde_ciudad.toLocaleString()} km</strong> de Quito</div>
      <div class="card-sub">Lat ${pos.lat} · Lon ${pos.lon} · Alt ${pos.altitud} km</div>
      <div class="card-sub">Velocidad: ${pos.velocidad.toLocaleString()} km/h</div>
      <button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:16px">← Volver</button>
    `;
  } catch { document.getElementById('iss-data').textContent = 'Error al cargar'; }
}

async function cargarPlanetas() {
  try {
    const res  = await fetch(`${API}/api/planetas`);
    const data = await res.json();
    let html = '';
    if (data.visibles_ahora && data.planetas && data.planetas.length > 0) {
      html = data.planetas.map(p =>
        `<div class="card-value">${p.planeta} — ${p.altitud}° hacia el ${p.direccion}</div>`
      ).join('');
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana;
      html = `<div class="card-value">Próxima ventana: <strong>${v.hora_local}</strong></div>
              <div class="card-sub">En ${v.en_horas}h · ${v.planetas.map(p => p.planeta).join(', ')}</div>`;
    } else {
      html = '<div class="card-sub">No hay planetas visibles ahora mismo.</div>';
    }
    document.getElementById('planetas-data').innerHTML = html +
      `<button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:16px">← Volver</button>`;
  } catch (e) {
    document.getElementById('planetas-data').textContent = 'Error al cargar';
    console.error(e);
  }
}


async function cargarEclipses() {
  try {
    const res  = await fetch(`${API}/api/eclipses`);
    const data = await res.json();
    const html = data.eclipses.map(e => {
      const cr  = e.cuenta_regresiva;
      const vis = e.visible_quito ? '✓ visible desde Quito' : 'no visible desde Quito';
      const ico = e.tipo === 'Solar' ? '☀️' : '🌑';
      return `
        <div class="conj-item">
          <div class="card-value">${ico} Eclipse ${e.tipo} ${e.subtipo}</div>
          <div class="card-value" style="font-size:18px;font-weight:700;color:#7dd3fc;margin:4px 0;">
            ${cr.dias}d ${cr.horas}h ${cr.mins}m
          </div>
          <div class="card-sub">${e.fecha_local} · ${vis}</div>
        </div>`;
    }).join('');
    document.getElementById('eclipses-data').innerHTML = html +
      `<button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:16px">← Volver</button>`;
  } catch(e) {
    document.getElementById('eclipses-data').textContent = 'Error al cargar';
  }
}

async function cargarConjunciones() {
  try {
    const res  = await fetch(`${API}/api/conjunciones`);
    const data = await res.json();
    let html = !data.conjunciones.length
      ? '<div class="card-sub">Ninguna conjunción notable en los próximos 90 días.</div>'
      : data.conjunciones.map(c => `
          <div class="conj-item">
            <div class="card-value">✨ ${c.planeta1} + ${c.planeta2}</div>
            <div class="card-sub">Separación: ${c.separacion}° · ${c.fecha_local} · ${c.cuenta_regresiva.texto}</div>
          </div>`).join('');
    document.getElementById('conjunciones-data').innerHTML = html + `<button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:16px">← Volver</button>`;
  } catch { document.getElementById('conjunciones-data').textContent = 'Error al cargar'; }
}

async function cargarLunas() {
  try {
    const res  = await fetch(`${API}/api/lunas`);
    const data = await res.json();
    document.getElementById('lunas-lista').innerHTML =
      data.lunas.map(l => `
        <button class="luna-btn ripple" onclick="verLuna('${l.id}', this)">
          <img id="img-${l.id}" src="" alt="${l.nombre}"
            style="width:40px;height:40px;border-radius:50%;object-fit:cover;flex-shrink:0;background:rgba(125,211,252,0.1)">
          <div class="luna-btn-info">
            <div class="luna-btn-nombre">${l.nombre}</div>
            <div class="luna-btn-planeta">${l.planeta}</div>
          </div>
        </button>`).join('') +
      `<button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:8px">← Volver</button>`;

    // Cargar imágenes de NASA en paralelo
    data.lunas.forEach(async l => {
      try {
        const r   = await fetch(`${API}/api/lunas/${l.id}/imagen`);
        const img = await r.json();
        const el  = document.getElementById(`img-${l.id}`);
        if (el && img.imagen) el.src = img.imagen;
      } catch {}
    });

  } catch { document.getElementById('lunas-lista').textContent = 'Error al cargar'; }
}

async function verLuna(id, btn) {
  document.querySelectorAll('.luna-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const detalle = document.getElementById('luna-detalle');
  detalle.innerHTML = '<div class="card-sub" style="text-align:center;padding:20px">Cargando...</div>';
  try {
    const [resLuna, resImg] = await Promise.all([
      fetch(`${API}/api/lunas/${id}`),
      fetch(`${API}/api/lunas/${id}/imagen`)
    ]);
    const l      = await resLuna.json();
    const imgData = await resImg.json();
    const imgUrl  = imgData.imagen || '';
    const d       = l.datos;

    detalle.innerHTML = `
      <div class="luna-top-row">
        <div class="luna-img-cuadrado">
          <img src="${imgUrl}" alt="${l.nombre}">
        </div>
        <div class="luna-datos-cuadrado">
          <div class="luna-seccion-titulo" style="margin-bottom:10px">📊 DATOS</div>
          <div class="luna-dato"><span>Diámetro</span><span>${d.diametro_km.toLocaleString()} km</span></div>
          <div class="luna-dato"><span>Distancia</span><span>${d.distancia_km.toLocaleString()} km</span></div>
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
      </div>
      <button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:8px">← Volver al menú</button>
    `;
  } catch(e) {
    detalle.innerHTML = '<div class="card-sub">Error al cargar</div>';
    console.error(e);
  }
}


async function cargarOposiciones() {
  try {
    const res  = await fetch(`${API}/api/oposiciones`);
    const data = await res.json();
    const html = data.oposiciones.map(o => `
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
        <div class="card-sub" style="margin-top:6px;font-family:'Inter',sans-serif;font-style:italic">
          ${o.descripcion}
        </div>
      </div>
    `).join('');
    document.getElementById('oposiciones-data').innerHTML = html +
      `<button class="btn-volver ripple" onclick="volverMenu()" style="margin-top:16px">← Volver</button>`;
  } catch(e) {
    document.getElementById('oposiciones-data').textContent = 'Error al cargar';
  }
}

// ── INIT ──
window.onload = () => {
  if (getToken()) mostrarApp();
};