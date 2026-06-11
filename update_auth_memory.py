import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update State Loading Logic
old_load_logic = """        // Initialize state from localStorage
        const savedState = localStorage.getItem('as_bajo_la_manga_state');
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                // Restaurar estado EXCEPTO datos de jugadores (se resetean siempre)
                const baseState = { ...state };
                state = {
                    ...baseState,
                    ...parsed,
                    players: [],              // ✅ SIEMPRE vacío al recargar
                    currentPlayerIndex: 0,    // ✅ SIEMPRE 0
                    gameStarted: false        // ✅ SIEMPRE false
                };"""

new_load_logic = """        // Initialize state from storage (hybrid)
        const savedSession = sessionStorage.getItem('as_bajo_la_manga_state');
        const savedLocal = localStorage.getItem('as_bajo_la_manga_state');
        const savedState = savedLocal || savedSession;
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                const baseState = { ...state };
                state = {
                    ...baseState,
                    ...parsed
                };"""
html = html.replace(old_load_logic, new_load_logic)

# 2. Update saveState Logic
old_save_logic = """        function saveState() {
            localStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
        }"""
new_save_logic = """        function saveState() {
            if (state.user) {
                localStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
                sessionStorage.removeItem('as_bajo_la_manga_state');
            } else {
                sessionStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
                localStorage.removeItem('as_bajo_la_manga_state');
            }
        }"""
html = html.replace(old_save_logic, new_save_logic)

# 3. Update Auth UI
html = html.replace('<p class="text-slate-300 text-sm">${state.user.email}</p>', '<p class="text-slate-300 text-sm font-bold text-amber-400">@${state.user.email.split("@")[0]}</p>')
html = html.replace('id="auth-email" type="email" placeholder="Correo electrónico"', 'id="auth-username" type="text" placeholder="Nombre de usuario" autocomplete="off"')

# 4. Update Auth JS Functions
old_signin = """        async function signInWithSupabase() {
            if (!supabaseClient) { showToast('⚠️ Sin conexión a Supabase'); return; }
            const email = document.getElementById('auth-email').value.trim();
            const password = document.getElementById('auth-password').value.trim();
            if (!email || !password) { showToast('⚠️ Llená todos los campos'); return; }
            
            const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });"""

new_signin = """        async function signInWithSupabase() {
            if (!supabaseClient) { showToast('⚠️ Sin conexión a Supabase'); return; }
            const usernameRaw = document.getElementById('auth-username').value.trim();
            const username = usernameRaw.toLowerCase().replace(/\s+/g, '');
            const email = username + '@asbajolamanga.com';
            const password = document.getElementById('auth-password').value.trim();
            if (!username || !password) { showToast('⚠️ Llená todos los campos'); return; }
            
            const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });"""
html = html.replace(old_signin, new_signin)

old_signup = """        async function signUpWithSupabase() {
            if (!supabaseClient) { showToast('⚠️ Sin conexión a Supabase'); return; }
            const email = document.getElementById('auth-email').value.trim();
            const password = document.getElementById('auth-password').value.trim();
            if (!email || !password) { showToast('⚠️ Llená todos los campos'); return; }
            
            const { data, error } = await supabaseClient.auth.signUp({ email, password });"""

new_signup = """        async function signUpWithSupabase() {
            if (!supabaseClient) { showToast('⚠️ Sin conexión a Supabase'); return; }
            const usernameRaw = document.getElementById('auth-username').value.trim();
            const username = usernameRaw.toLowerCase().replace(/\s+/g, '');
            const email = username + '@asbajolamanga.com';
            const password = document.getElementById('auth-password').value.trim();
            if (!username || !password) { showToast('⚠️ Llená todos los campos'); return; }
            
            const { data, error } = await supabaseClient.auth.signUp({ email, password });"""
html = html.replace(old_signup, new_signup)

old_signout = """        async function signOutSupabase() {
            if (!supabaseClient) return;
            await supabaseClient.auth.signOut();
            showToast('👋 Sesión cerrada');
            changeView('menu');
        }"""

new_signout = """        async function signOutSupabase() {
            if (!supabaseClient) return;
            await supabaseClient.auth.signOut();
            localStorage.removeItem('as_bajo_la_manga_state');
            sessionStorage.removeItem('as_bajo_la_manga_state');
            showToast('👋 Sesión cerrada, reiniciando...');
            setTimeout(() => window.location.reload(), 1000);
        }"""
html = html.replace(old_signout, new_signout)

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ INICIAR.html modificado: Auth por Username y Memoria persistente/temporal implementada")
