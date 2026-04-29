// ─── State ────────────────────────────────────────────────────────────────────
let currentContext = {};
let refreshTimer   = null;

// ─── AQI Helpers ─────────────────────────────────────────────────────────────
const AQI_CONFIG = {
  Good:         { color: '#00C853', bg: '#f0fff4', msg: 'Air quality is great. Safe to go outside!' },
  Satisfactory: { color: '#64DD17', bg: '#f4ffe0', msg: 'Air quality is acceptable. Enjoy your day.' },
  Moderate:     { color: '#FFD600', bg: '#fffde7', msg: 'Sensitive groups should limit outdoor activity.' },
  Poor:         { color: '#FF6D00', bg: '#fff3e0', msg: 'Avoid prolonged outdoor exposure.' },
  'Very Poor':  { color: '#DD2C00', bg: '#fce4ec', msg: 'Stay indoors if possible. Wear a mask outside.' },
  Severe:       { color: '#6200EA', bg: '#f3e5f5', msg: 'Hazardous! Avoid all outdoor activity.' },
};

function getConfig(category) {
  return AQI_CONFIG[category] || { color: '#6b7280', bg: '#f4f6f9', msg: '' };
}

// ─── Location ─────────────────────────────────────────────────────────────────
function requestLocation() {
  show('loadingScreen');
  hide('errorScreen');
  hide('dashboard');

  if (!navigator.geolocation) {
    showError();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    pos => loadData(pos.coords.latitude, pos.coords.longitude),
    ()  => showError()
  );
}

function showError() {
  hide('loadingScreen');
  show('errorScreen');
}

// ─── Data Loading ─────────────────────────────────────────────────────────────
async function loadData(lat, lon) {
  try {
    const [aqiRes, forecastRes] = await Promise.all([
      fetch('/api/aqi',      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lat, lon }) }),
      fetch('/api/forecast', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lat, lon }) }),
    ]);

    const aqiData      = await aqiRes.json();
    const forecastData = await forecastRes.json();

    renderAQI(aqiData);
    renderForecast(forecastData.forecasts);
    updateTimestamp();

    // Save context for AI chat
    currentContext = {
      city:        aqiData.city,
      aqi:         aqiData.aqi,
      category:    aqiData.category,
      pm25:        aqiData.pollutants.pm25,
      pm10:        aqiData.pollutants.pm10,
      no2:         aqiData.pollutants.no2,
      o3:          aqiData.pollutants.o3,
      temperature: aqiData.weather.temperature,
      humidity:    aqiData.weather.humidity,
      wind_speed:  aqiData.weather.wind_speed,
    };

    hide('loadingScreen');
    show('dashboard');

    // Auto-refresh every 10 minutes
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => loadData(lat, lon), 10 * 60 * 1000);

  } catch (err) {
    console.error('Failed to load AQI data:', err);
    hide('loadingScreen');
    show('dashboard');
  }
}

// ─── Render AQI ───────────────────────────────────────────────────────────────
function renderAQI(data) {
  const cfg = getConfig(data.category);

  // Hero card
  document.getElementById('aqiNumber').textContent  = data.aqi;
  document.getElementById('aqiNumber').style.color  = cfg.color;
  document.getElementById('aqiBadge').textContent   = data.category;
  document.getElementById('aqiBadge').style.background = cfg.color;
  document.getElementById('aqiMessage').textContent = cfg.msg;
  document.getElementById('aqiCard').style.background = cfg.bg;

  // Location
  document.getElementById('cityName').textContent = data.city;

  // Weather
  document.getElementById('temperature').textContent  = data.weather.temperature;
  document.getElementById('humidity').textContent     = data.weather.humidity;
  document.getElementById('windSpeed').textContent    = data.weather.wind_speed;
  document.getElementById('weatherDesc').textContent  = data.weather.description;

  // Pollutants
  document.getElementById('pm25').textContent = data.pollutants.pm25;
  document.getElementById('pm10').textContent = data.pollutants.pm10;
  document.getElementById('no2').textContent  = data.pollutants.no2;
  document.getElementById('o3').textContent   = data.pollutants.o3;
  document.getElementById('co').textContent   = data.pollutants.co;
  document.getElementById('so2').textContent  = data.pollutants.so2;
}

// ─── Render Forecast ──────────────────────────────────────────────────────────
function renderForecast(forecasts) {
  const ids = { 1: 'f1hr', 3: 'f3hr', 6: 'f6hr', 24: 'f24hr' };

  forecasts.forEach(f => {
    const id  = ids[f.hours];
    const cfg = getConfig(f.category);
    if (!id) return;

    document.getElementById(id).textContent              = f.aqi;
    document.getElementById(id).style.color              = cfg.color;
    document.getElementById(id + 'Cat').textContent      = f.category;
    document.getElementById(id + 'Cat').style.background = cfg.color;

    const card = document.getElementById(id).closest('.forecast-card');
    if (card) card.classList.remove('skeleton');
  });
}

// ─── Timestamp ────────────────────────────────────────────────────────────────
function updateTimestamp() {
  const now = new Date();
  document.getElementById('lastUpdated').textContent =
    `Updated ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
}

// ─── Chat ─────────────────────────────────────────────────────────────────────
function toggleChat() {
  const panel = document.getElementById('chatPanel');
  panel.classList.toggle('hidden');
  if (!panel.classList.contains('hidden')) {
    document.getElementById('chatInput').focus();
  }
}

async function sendMessage() {
  const input   = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  appendMessage(message, 'user');

  const loadingEl = appendMessage('Thinking...', 'ai loading');

  try {
    const res  = await fetch('/api/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message, context: currentContext }),
    });
    const data = await res.json();
    loadingEl.textContent    = data.response;
    loadingEl.className      = 'chat-msg ai';
  } catch {
    loadingEl.textContent = 'Sorry, something went wrong. Please try again.';
    loadingEl.className   = 'chat-msg ai';
  }
}

function appendMessage(text, type) {
  const messages = document.getElementById('chatMessages');
  const el       = document.createElement('div');
  el.className   = `chat-msg ${type}`;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
  return el;
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

// ─── Init ─────────────────────────────────────────────────────────────────────
window.addEventListener('load', requestLocation);
