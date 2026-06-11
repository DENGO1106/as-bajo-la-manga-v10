import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# PATCH 1: Add valid view guard + smarter routing at load time
# ============================================================
old_route = "        // Sin jugadores → setup siempre\n        if (state.players.length < 2) state.view = 'setup';"
new_route = """        // Limpiar vistas obsoletas que ya no existen
        const validViews = ['welcome','menu','setup','auth','profile','onlineRoom',
            'toxic','poker','sinexcusas','sinexcusasSetup','quienEsMas','quienEsMasGame',
            'bomba','retoCadena','dilemaRey','mimicaExpress','ultimaCarta','biblioteca'];
        if (!validViews.includes(state.view)) state.view = 'welcome';
        // Ruteo inicial inteligente
        if (!savedState) {
            state.view = 'welcome';
        } else if (state.players.length < 2) {
            state.view = 'welcome';
        }"""
html = html.replace(old_route, new_route)
if old_route in open('INICIAR.html', encoding='utf-8').read():
    print("❌ PATCH 1 falló")
else:
    print("✅ PATCH 1 OK")

# ============================================================
# PATCH 2: Add render fallback for unknown views
# ============================================================
old_render = """            if (views[state.view]) {
                container.innerHTML = views[state.view]();
            }"""
new_render = """            if (views[state.view]) {
                container.innerHTML = views[state.view]();
            } else {
                console.warn('Vista desconocida:', state.view, '→ welcome');
                state.view = 'welcome';
                container.innerHTML = views.welcome();
            }"""
html = html.replace(old_render, new_render)

# ============================================================
# PATCH 3: Add inactivity timers + update saveState to track last_activity
# ============================================================
old_save = """        function saveState() {
            localStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
        }"""
new_save = """        let _inactivityWarningTimer = null;
        let _inactivityExpireTimer = null;
        const ROOM_INACTIVITY_MS = 20 * 60 * 1000; // 20 minutos
        const ROOM_WARNING_MS   = 15 * 60 * 1000; // aviso a los 15 min

        function resetInactivityTimers() {
            clearTimeout(_inactivityWarningTimer);
            clearTimeout(_inactivityExpireTimer);
            _inactivityWarningTimer = setTimeout(() => {
                if (state.roomCode) showToast('⚠️ La sala expira en 5 minutos por inactividad');
            }, ROOM_WARNING_MS);
            _inactivityExpireTimer = setTimeout(() => {
                if (state.roomCode) {
                    showToast('⏱️ Sala cerrada por inactividad');
                    abandonarSala();
                }
            }, ROOM_INACTIVITY_MS);
        }

        function saveState(isRemote = false) {
            if (state.user) {
                localStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
                sessionStorage.removeItem('as_bajo_la_manga_state');
            } else {
                sessionStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
                localStorage.removeItem('as_bajo_la_manga_state');
            }
            if (state.roomCode && !isRemote && supabaseClient) {
                const stateToSync = { ...state };
                delete stateToSync.user;
                try:
                    const res = await casUpdateRoom(state.roomCode, { game_state: stateToSync });
                    if (res && res.error) console.error('Supabase sync error:', res.error);
                } catch (e) { console.warn('saveState supabase error', e); }
                resetInactivityTimers();
            }
        }"""
html = html.replace(old_save, new_save)

# ============================================================
# PATCH 4: Add onlineRoom + welcome views before the existing views
# ============================================================
old_views_start = "        const views = {\n            menu: () => `"
new_views_start = """        const views = {
            onlineRoom: () => `
                <div class="space-y-6 animate-fade-in py-4">
                    <div class="text-center space-y-2">
                        <div style="font-size:3rem;">🌐</div>
                        <h2 class="text-3xl font-black gradient-gold uppercase">Multijugador</h2>
                        <p class="text-slate-400 text-sm">Sincroniza todos los juegos en vivo</p>
                    </div>
                    \${state.roomCode ? \`
                    <div class="glass p-6 rounded-3xl border border-emerald-500/20 text-center space-y-4">
                        <p class="text-emerald-400 font-bold uppercase tracking-widest text-xs">Conectado a Sala</p>
                        <div class="room-code-display text-5xl font-black tracking-[0.2em] text-emerald-400">\${state.roomCode}</div>
                        <p class="text-slate-400 text-sm">Todos los juegos se sincronizan en vivo.</p>
                        <div class="grid grid-cols-2 gap-3 mt-4">
                            <button onclick="changeView('menu')" class="bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-3 rounded-xl font-bold touch-feedback text-white">Jugar Ahora</button>
                            <button onclick="abandonarSala()" class="bg-red-500/10 text-red-400 border border-red-500/30 px-4 py-3 rounded-xl font-bold touch-feedback">Desconectar</button>
                        </div>
                    </div>
                    \` : \`
                    <div class="glass p-6 rounded-3xl border border-white/10 space-y-6">
                        <button onclick="crearSala()" class="w-full p-4 rounded-2xl font-black text-slate-950 text-lg uppercase shadow-xl touch-feedback" style="background:linear-gradient(135deg,#10b981,#059669);">Crear Nueva Sala</button>
                        <div class="relative flex items-center py-2">
                            <div class="flex-grow border-t border-slate-700"></div>
                            <span class="flex-shrink-0 mx-4 text-slate-500 text-sm font-bold uppercase">o únete a una</span>
                            <div class="flex-grow border-t border-slate-700"></div>
                        </div>
                        <div class="flex gap-2">
                            <input type="text" id="room-code-input" placeholder="Código de 6 dígitos"
                                   class="flex-1 bg-slate-800 px-4 py-3 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-center font-mono tracking-widest text-lg" maxlength="6">
                            <button onclick="unirseSala()" class="glass bg-white/5 border border-white/10 px-6 py-3 rounded-xl font-bold touch-feedback text-emerald-400">Entrar</button>
                        </div>
                    </div>
                    \`}
                    <button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-white touch-feedback mt-6">Volver al Menú</button>
                </div>
            `,
            welcome: () => `
                <div class="space-y-8 animate-fade-in py-8 flex flex-col items-center justify-center min-h-[70vh]">
                    <div class="text-center space-y-4">
                        <div style="font-size:4rem;" class="mb-4">🃏</div>
                        <h1 class="text-4xl font-black gradient-gold uppercase tracking-tighter">As Bajo La Manga</h1>
                        <p class="text-slate-400 text-lg">Elige cómo quieres entrar al juego</p>
                    </div>
                    <div class="w-full max-w-sm space-y-4">
                        <button onclick="changeView('auth')" class="w-full p-4 rounded-2xl font-black text-slate-950 text-lg shadow-xl touch-feedback" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                            🔐 Iniciar con Cuenta
                        </button>
                        <div class="relative flex items-center py-2">
                            <div class="flex-grow border-t border-slate-700"></div>
                            <span class="flex-shrink-0 mx-4 text-slate-500 text-sm font-bold uppercase">o</span>
                            <div class="flex-grow border-t border-slate-700"></div>
                        </div>
                        <button onclick="changeView('setup')" class="w-full glass p-4 rounded-2xl font-bold text-white border border-white/10 touch-feedback">
                            👤 Jugar como Invitado
                        </button>
                    </div>
                </div>
            `,
            menu: () => `"""
html = html.replace(old_views_start, new_views_start)

# ============================================================
# PATCH 5: Add Sala Global button to menu
# ============================================================
old_menu_section = "                    <!-- Juegos de Cartas -->"
new_menu_section = """                    <!-- Modo Multijugador Global -->
                    <button onclick="changeView('onlineRoom')" class="w-full glass p-6 rounded-3xl flex items-center gap-4 btn-hover card-shadow group border-emerald-500/20 ripple touch-feedback mt-4 relative overflow-hidden">
                        <div class="bg-emerald-500/20 p-4 rounded-2xl group-hover:bg-emerald-500/30 transition-colors">
                            <span class="text-2xl">\${state.roomCode ? '🟢' : '🌐'}</span>
                        </div>
                        <div class="text-left">
                            <h2 class="text-lg font-bold \${state.roomCode ? 'text-emerald-400' : 'text-emerald-500'}">SALA MULTIJUGADOR</h2>
                            <p class="text-slate-400 text-sm">\${state.roomCode ? 'Conectado: ' + state.roomCode : 'Sincroniza pantallas en vivo'}</p>
                        </div>
                    </button>

                    <!-- Juegos de Cartas -->"""
html = html.replace(old_menu_section, new_menu_section)

# ============================================================
# PATCH 6: Update profile button in menu to point to profile
# ============================================================
old_auth_btn = """                    <!-- Auth Button -->
                    <button onclick="changeView('auth')" class="absolute top-4 right-4 glass p-2 rounded-xl text-xl touch-feedback border z-50 \${state.user ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/20 text-amber-400'}">
                        \${state.user ? '🔓' : '🔐'}
                    </button>"""
new_auth_btn = """                    <!-- Profile Button -->
                    <button onclick="changeView(state.user ? 'profile' : 'welcome')" class="absolute top-4 right-4 glass p-2 rounded-xl text-xl touch-feedback border z-50 \${state.user ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10' : 'border-amber-500/20 text-amber-400'}">
                        \${state.user ? '👤' : '🔐'}
                    </button>"""
html = html.replace(old_auth_btn, new_auth_btn)

# ============================================================
# PATCH 7: Add sala functions before SUPABASE AUTH section
# ============================================================
old_auth_section = "        // ========================================\n        // SUPABASE AUTH\n        // ========================================"
new_auth_section = """        // ========================================
        // SALAS GLOBALES — MULTIJUGADOR
        // ========================================
        async function crearSala() {
            if (!supabaseClient) return showToast('⚠️ Sin conexión a internet');
            const code = Math.floor(100000 + Math.random() * 900000).toString();
            state.roomCode = code;
            const now = new Date();
            const expiresAt = new Date(now.getTime() + ROOM_INACTIVITY_MS);
            const stateToSync = { ...state };
            delete stateToSync.user;
            const { error } = await supabaseClient.from('rooms').insert({
                code, game_state: stateToSync,
                expires_at: expiresAt.toISOString(),
                last_activity: now.toISOString()
            });
            if (error) { state.roomCode = null; return showToast('❌ Error al crear sala: ' + error.message); }
            saveState(true);
            conectarSala(code);
            resetInactivityTimers();
            showToast('✅ Sala creada: ' + code);
            render();
        }

        function conectarSala(code) {
            if (realtimeChannel) { supabaseClient.removeChannel(realtimeChannel); realtimeChannel = null; }
            realtimeChannel = supabaseClient.channel('room_' + code)
                .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'rooms', filter: \`code=eq.\${code}\` }, (payload) => {
                    const remoteState = payload.new.game_state;
                    if (remoteState) {
                        const localUser = state.user;
                        state = { ...remoteState, user: localUser };
                        saveState(true);
                        render();
                    }
                })
                .subscribe();
        }

        async function unirseSala() {
            const input = document.getElementById('room-code-input');
            const code = input?.value.trim();
            if (!code || code.length !== 6) return showToast('✍️ Código de 6 dígitos');
            if (!supabaseClient) return showToast('⚠️ Sin conexión');
            const { data, error } = await supabaseClient.from('rooms').select('game_state, last_activity').eq('code', code).single();
            if (error || !data) return showToast('❌ Sala no encontrada');
            if (data.last_activity) {
                const diffMs = Date.now() - new Date(data.last_activity).getTime();
                if (diffMs > ROOM_INACTIVITY_MS) {
                    await supabaseClient.from('rooms').delete().eq('code', code);
                    return showToast('⏱️ Sala expirada por inactividad');
                }
            }
            const localUser = state.user;
            state = { ...data.game_state, user: localUser };
            state.roomCode = code;
            saveState(true);
            conectarSala(code);
            resetInactivityTimers();
            showToast('✅ Conectado a sala ' + code);
            render();
        }

        function abandonarSala() {
            clearTimeout(_inactivityWarningTimer);
            clearTimeout(_inactivityExpireTimer);
            if (realtimeChannel && supabaseClient) { supabaseClient.removeChannel(realtimeChannel); realtimeChannel = null; }
            state.roomCode = null;
            saveState();
            showToast('🔌 Desconectado de la sala');
            render();
        }

        // ========================================
        // SUPABASE AUTH
        // ========================================"""
html = html.replace(old_auth_section, new_auth_section)

# ============================================================
# PATCH 8: Update init at bottom of second script
# ============================================================
old_init_bottom = "        // Initialize Supabase now that consts are defined\n        initSupabase();\n        checkSession();"
new_init_bottom = """        // Initialize Supabase now that consts are defined
        initSupabase();
        checkSession();
        if (state.roomCode) { conectarSala(state.roomCode); }"""
html = html.replace(old_init_bottom, new_init_bottom)

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ Todos los patches aplicados correctamente sobre la version funcional")
