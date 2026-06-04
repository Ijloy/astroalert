const API = 'https://astroalert-pgyw.onrender.com';

function getToken() { return localStorage.getItem('token'); }
function setToken(t) { localStorage.setItem('token', t); }
function removeToken() { localStorage.removeItem('token'); }

async function login() {
  const email    = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const error    = document.getElementById('auth-error');

  const res = await fetch(`${API}/api/login`, {
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

  const res = await fetch(`${API}/api/registro`, {
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
  cargarDatos();
}

async function cargarDatos() {
  const token = getToken();
  const headers = { 'Authorization': `Bearer ${token}` };

  // ISS
  try {
    const res  = await fetch(`${API}/api/iss`);
    const data = await res.json();
    const pos  = data.posicion;
    document.getElementById('iss-data').innerHTML = `
      <div class="card-value">A <strong>${data.distancia_desde_ciudad.toLocaleString()} km</strong> de Quito</div>
      <div class="card-sub">Lat ${pos.lat} · Lon ${pos.lon} · Alt ${pos.altitud} km</div>
      <div class="card-sub">Velocidad: ${pos.velocidad.toLocaleString()} km/h</div>
    `;
  } catch {
    document.getElementById('iss-data').textContent = 'Error al cargar';
  }

  // Planetas
  try {
    const res  = await fetch(`${API}/api/planetas`);
    const data = await res.json();

    if (data.visibles_ahora && data.visibles_ahora.length > 0) {
      const lista = data.visibles_ahora.map(p =>
        `<div class="card-value">${p.planeta} — ${p.altitud}° hacia el ${p.direccion}</div>`
      ).join('');
      document.getElementById('planetas-data').innerHTML = lista;
    } else if (data.proxima_ventana) {
      const v = data.proxima_ventana;
      document.getElementById('planetas-data').innerHTML = `
        <div class="card-value">Próxima ventana: <strong>${v.hora_local}</strong></div>
        <div class="card-sub">En ${v.en_horas}h · ${v.planetas.map(p => p.planeta).join(', ')}</div>
      `;
    }
  } catch {
    document.getElementById('planetas-data').textContent = 'Error al cargar';
  }
}

// Al cargar la página, ver si hay sesión activa
window.onload = () => {
  if (getToken()) mostrarApp();
};