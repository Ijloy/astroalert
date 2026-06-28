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
const secciones = ['iss', 'planetas', 'eclipses', 'conjunciones', 'lunas', 'oposiciones', 'telescopio', 'proximamente'];
const cargados  = {};

function irSeccion(seccion) {
      document.querySelectorAll('.nav-revista-item').forEach(b => b.classList.remove('active'));
      const navBtn = Array.from(document.querySelectorAll('.nav-revista-item'))
        .find(b => b.getAttribute('onclick')?.includes(`'${seccion}'`));
      if (navBtn) navBtn.classList.add('active');
  closeSidebar();

  // Ocultar carrusel y grid cuando se abre una sección
  const seccEnContenido = ['iss','planetas','eclipses','conjunciones','lunas', 'oposiciones', 'telescopio'];
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
    if (seccion === 'telescopio') cargarImagenTelescopio();
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

async function calcularTelescopio() {
  const apertura  = document.getElementById('tel-apertura').value;
  const focal     = document.getElementById('tel-focal').value;
  const ocular    = document.getElementById('tel-ocular').value;
  const afov      = document.getElementById('tel-afov').value || 52;

  if (!apertura || !focal || !ocular) {
    alert('Ingresa apertura, focal del telescopio y focal del ocular');
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
    const r    = data.resultados;

    document.getElementById('tel-mag').textContent    = r.magnificacion + 'x';
    document.getElementById('tel-campo').textContent  = r.campo_visual + '°';
    document.getElementById('tel-pupila').textContent = r.pupila_salida + 'mm';
    document.getElementById('tel-limite').textContent = r.limite_magnitud;
    document.getElementById('tel-min').textContent    = r.mag_minima_util + 'x';
    document.getElementById('tel-max').textContent    = r.mag_maxima_util + 'x';

    document.getElementById('tel-objetos').textContent =
      data.objetos_recomendados.join(' · ');

    const advBox = document.getElementById('tel-advertencias-box');
    if (data.advertencias.length > 0) {
      document.getElementById('tel-advertencias').innerHTML =
        data.advertencias.map(a => `<div class="curiosidad" style="border-color:rgba(251,113,133,0.4)">${a}</div>`).join('');
      advBox.classList.remove('hidden');
    } else {
      advBox.classList.add('hidden');
    }

    document.getElementById('telescopio-resultado').classList.remove('hidden');
  } catch(e) {
    console.error(e);
    alert('Error al calcular');
  }
}


// ── FONDO ESPACIAL ──
const ICONOS_ESPACIO = [
  // Estrella simple
  `<svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 2l1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z"/></svg>`,
  // Planeta con anillo
  `<svg viewBox="0 0 24 24" width="28" height="28"><circle cx="12" cy="12" r="5"/><ellipse cx="12" cy="12" rx="11" ry="3"/></svg>`,
  // Cometa
  `<svg viewBox="0 0 24 24" width="26" height="26"><circle cx="17" cy="7" r="3"/><path d="M14 10 L4 20 M12 8 L2 18 M16 12 L6 22"/></svg>`,
  // Luna creciente
  `<svg viewBox="0 0 24 24" width="18" height="18"><path d="M15 4a8 8 0 100 16 8 8 0 01-8-8 8 8 0 018-8z"/></svg>`,
  // Cohete
  `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 2c2 2 3 5 3 9s-1 7-3 9c-2-2-3-5-3-9s1-7 3-9z"/><path d="M9 14l-3 3v3l3-1M15 14l3 3v3l-3-1"/></svg>`,
  // Cruz pequeña (estrella diminuta)
  `<svg viewBox="0 0 24 24" width="10" height="10"><path d="M12 4v16M4 12h16"/></svg>`,
  // Sol
  `<svg viewBox="0 0 24 24" width="24" height="24"><circle cx="12" cy="12" r="5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/></svg>`,
  // Satélite
  `<svg viewBox="0 0 24 24" width="24" height="24"><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 11H4M15 11h5M9 13H4M15 13h5"/><path d="M5 5l3 3M19 5l-3 3"/></svg>`,
];

function generarFondoEspacial() {
  const bg = document.getElementById('space-bg');
  if (!bg) return;
  const cantidad = 22;
  let html = '';
  for (let i = 0; i < cantidad; i++) {
    const icono = ICONOS_ESPACIO[Math.floor(Math.random() * ICONOS_ESPACIO.length)];
    const top   = Math.random() * 100;
    const left  = Math.random() * 100;
    const rot   = Math.random() * 360;
    html += `<div style="position:absolute;top:${top}%;left:${left}%;transform:rotate(${rot}deg)">${icono}</div>`;
  }
  bg.innerHTML = html;
}

generarFondoEspacial();


async function cargarImagenesCards() {
  for (const [cardId, query] of Object.entries(QUERIES_NASA_CARDS)) {
    try {
      const res  = await fetch(`https://images-api.nasa.gov/search?q=${encodeURIComponent(query)}&media_type=image`);
      const data = await res.json();
      const items = data.collection?.items || [];
      if (items.length > 0) {
        // Elegir una imagen aleatoria entre los primeros 10 resultados
        const max   = Math.min(items.length, 10);
        const item  = items[Math.floor(Math.random() * max)];
        const link  = item.links?.find(l => l.rel === 'preview');
        if (link) {
          const card = document.getElementById(cardId);
          if (card) {
            const bg = card.querySelector('.grid-card-bg');
            bg.style.backgroundImage = `url('${link.href}')`;
          }
        }
      }
    } catch(e) { console.error('Error imagen', cardId, e); }
  }
}


async function cargarImagenTelescopio() {
  try {
    const queries = ['telescope night sky stars observatory', 'astronomer telescope stargazing night'];
    const query   = queries[Math.floor(Math.random() * queries.length)];
    const res     = await fetch(`https://images-api.nasa.gov/search?q=${encodeURIComponent(query)}&media_type=image`);
    const data    = await res.json();
    const items   = data.collection?.items || [];
    if (items.length > 0) {
      const item = items[Math.floor(Math.random() * Math.min(items.length, 10))];
      const link = item.links?.find(l => l.rel === 'preview');
      if (link) document.getElementById('telescopio-bg-img').style.backgroundImage = `url('${link.href}')`;
    }
  } catch(e) { console.error(e); }
}

// ── INIT ──
window.onload = () => {
  if (getToken()) mostrarApp();
};