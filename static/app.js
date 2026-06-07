const API = 'https://astroalert-pgyw.onrender.com';

function getToken() { return localStorage.getItem('token'); }
function setToken(t) { localStorage.setItem('token', t); }
function removeToken() { localStorage.removeItem('token'); }

// NAVEGACIÓN
const secciones = ['iss', 'planetas', 'eclipses', 'conjunciones'];
const cargados  = {};

function ir(seccion) {
  secciones.forEach(s => {
    document.getElementById(`sec-${s}`).classList.add('hidden');
  });
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  document.getElementById(`sec-${seccion}`).classList.remove('hidden');
  event.target.classList.add('active');

  if (!cargados[seccion]) {
    cargados[seccion] = true;
    if (seccion === 'iss')          cargarISS();
    if (seccion === 'planetas')     cargarPlanetas();
    if (seccion === 'eclipses')     cargarEclipses();
    if (seccion === 'conjunciones') cargarConjunciones();
  }
}

// AUTH
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

async function registro() {
  const email    = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const error    = document.getElementById('auth-error');
  const res  = await fetch(`${API}/api/registro`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (!res.ok) { error.textContent = data.error; return; }
  error.style.color = '#34d399';
  error.textContent = 'Cuenta creada. Ahora inicia sesión.';
}

function cerrarSesion() {
  removeToken();
  document.getElementById('main-panel').classList.add('hidden');
  document.getElementById('login-panel').classList.remove('hidden');
}

function mostrarApp() {
  document.getElementById('login-panel').classList.add('hidden');
  document.getElementById('main-panel').classList.remove('hidden');
  cargarISS();
  cargados['iss'] = true;
}

// ISS
async function cargarISS() {
  try {
    const res  = await fetch(`${API}/api/iss`);
    const data = await res.json();
    const pos  = data.posicion;
    document.getElementById('iss-data').innerHTML = `
      <div class="card-value">A <strong>${data.distancia_desde_ciudad.toLocaleString()} km</strong> de Quito</div>
      <div class="card-sub">Lat ${pos.lat} · Lon ${pos.lon} · Alt ${pos.altitud} km</div>
      <div class="card-sub">Velocidad: ${pos.velocidad.toLocaleString()} km/h</div>
    `;
  } catch { document.getElementById('iss-data').textContent = 'Error al cargar'; }
}

// PLANETAS
async function cargarPlanetas() {
  try {
    const res  = await fetch(`${API}/api/planetas`);
    const data = await res.json();
    if (data.visibles_ahora && data.visibles_ahora.length > 0) {
      document.getElementById('planetas-data').innerHTML =
        data.visibles_ahora.map(p =>
          `<div class="card-value">${p.planeta} — ${p.altitud}° hacia el ${p.direccion}</div>`
        ).join('');
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana;
      document.getElementById('planetas-data').innerHTML = `
        <div class="card-value">Próxima ventana: <strong>${v.hora_local}</strong></div>
        <div class="card-sub">En ${v.en_horas}h · ${v.planetas.map(p => p.planeta).join(', ')}</div>
      `;
    }
  } catch { document.getElementById('planetas-data').textContent = 'Error al cargar'; }
}

// ECLIPSES
async function cargarEclipses() {
  try {
    const res  = await fetch(`${API}/api/eclipses`);
    const data = await res.json();
    const proximo = data.eclipses[0];
    const cr      = proximo.cuenta_regresiva;
    const visible = proximo.visible_quito ? '✓ visible desde Quito' : 'no visible desde Quito';
    const icono   = proximo.tipo === 'Solar' ? '☀️' : '🌑';
    document.getElementById('eclipses-data').innerHTML = `
      <div class="card-value">${icono} Eclipse ${proximo.tipo} ${proximo.subtipo}</div>
      <div class="card-value" style="font-size:22px;font-weight:700;color:#7dd3fc;margin:8px 0;">
        ${cr.dias}d ${cr.horas}h ${cr.mins}m
      </div>
      <div class="card-sub">${proximo.fecha_local} · ${visible}</div>
    `;
  } catch { document.getElementById('eclipses-data').textContent = 'Error al cargar'; }
}

// CONJUNCIONES
async function cargarConjunciones() {
  try {
    const res  = await fetch(`${API}/api/conjunciones`);
    const data = await res.json();
    if (!data.conjunciones.length) {
      document.getElementById('conjunciones-data').innerHTML =
        '<div class="card-sub">Ninguna conjunción notable en los próximos 90 días.</div>';
      return;
    }
    document.getElementById('conjunciones-data').innerHTML =
      data.conjunciones.map(c => `
        <div class="conj-item">
          <div class="card-value">✨ ${c.planeta1} + ${c.planeta2}</div>
          <div class="card-sub">Separación: ${c.separacion}° · ${c.fecha_local} · ${c.cuenta_regresiva.texto}</div>
        </div>
      `).join('');
  } catch { document.getElementById('conjunciones-data').textContent = 'Error al cargar'; }
}

// LUNAS
async function cargarLunas() {
  try {
    const res  = await fetch(`${API}/api/lunas`);
    const data = await res.json();
    document.getElementById('lunas-lista').innerHTML =
      data.lunas.map(l => `
        <button class="luna-btn" onclick="verLuna('${l.id}', this)">
          <img src="${l.imagen}" alt="${l.nombre}" onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/100px-FullMoon2010.jpg'">
          <div class="luna-btn-info">
            <div class="luna-btn-nombre">${l.nombre}</div>
            <div class="luna-btn-planeta">${l.planeta}</div>
          </div>
        </button>
      `).join('');
  } catch {
    document.getElementById('lunas-lista').textContent = 'Error al cargar';
  }
}

async function verLuna(id, btn) {
  document.querySelectorAll('.luna-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  const detalle = document.getElementById('luna-detalle');
  detalle.innerHTML = '<div class="card-sub" style="text-align:center;padding:20px">Cargando...</div>';

  try {
    const res  = await fetch(`${API}/api/lunas/${id}`);
    const l    = await res.json();
    const d    = l.datos;

    detalle.innerHTML = `
      <img class="luna-detalle-imagen" src="${l.imagen}" alt="${l.nombre}">

      <div class="luna-seccion">
        <div class="luna-seccion-titulo">📊 Datos</div>
        <div class="luna-dato"><span>Diámetro</span><span>${d.diametro_km.toLocaleString()} km</span></div>
        <div class="luna-dato"><span>Distancia</span><span>${d.distancia_km.toLocaleString()} km</span></div>
        <div class="luna-dato"><span>Período orbital</span><span>${d.periodo_orbital_dias} días</span></div>
        <div class="luna-dato"><span>Temp. máx</span><span>${d.temperatura_max}°C</span></div>
        <div class="luna-dato"><span>Temp. mín</span><span>${d.temperatura_min}°C</span></div>
        <div class="luna-dato"><span>Gravedad</span><span>${d.gravedad}</span></div>
        <div class="luna-dato"><span>Atmósfera</span><span>${d.atmosfera}</span></div>
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
    `;
  } catch {
    detalle.innerHTML = '<div class="card-sub">Error al cargar</div>';
  }
}

window.onload = () => {
  if (getToken()) mostrarApp();
};