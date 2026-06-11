import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update saveState()
old_save = """        function saveState() {
            if (state.user) {
                localStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
                sessionStorage.removeItem('as_bajo_la_manga_state');
            } else {
                sessionStorage.setItem('as_bajo_la_manga_state', JSON.stringify(state));
                localStorage.removeItem('as_bajo_la_manga_state');
            }
        }"""
new_save = """        function saveState(isRemote = false) {
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
                try {
                    const res = await casUpdateRoom(state.roomCode, { game_state: stateToSync });
                    if (res && res.error) console.error('Supabase sync error:', res.error);
                } catch (e) { console.warn('saveState supabase error', e); }
            }
        }"""
html = html.replace(old_save, new_save)

# Replace any old calls to saveState() that might need updating? No, saveState() with no args means isRemote=false which triggers broadcast. Perfect!

# 2. Update Sala Functions
old_sala_funcs = re.search(r'        async function crearSala\(\) \{.*?(?=        // ========================================)', html, flags=re.DOTALL)
if old_sala_funcs:
    new_sala_funcs = """        async function crearSala() {
            if (!supabaseClient) return showToast('⚠️ Sin conexión a internet');
            const code = Math.floor(100000 + Math.random() * 900000).toString();
            state.roomCode = code;
            saveState(); // triggers local save
            
            const expiresAt = new Date();
            expiresAt.setHours(expiresAt.getHours() + 12);
            
            const stateToSync = { ...state };
            delete stateToSync.user;

            const { error } = await supabaseClient.from('rooms').insert({
                code: code,
                game_state: stateToSync,
                expires_at: expiresAt.toISOString()
            });
            
            if (error) return showToast('❌ Error al crear sala');
            
            conectarSala(code);
            showToast('✅ Sala Global Creada');
            render();
        }

        function conectarSala(code) {
            if (realtimeChannel) {
                supabaseClient.removeChannel(realtimeChannel);
            }
            
            realtimeChannel = supabaseClient.channel('room_' + code)
                .on('postgres_changes', {
                    event: 'UPDATE',
                    schema: 'public',
                    table: 'rooms',
                    filter: `code=eq.${code}`
                }, (payload) => {
                    const remoteState = payload.new.game_state;
                    if (remoteState) {
                        const localUser = state.user;
                        state = { ...remoteState, user: localUser };
                        saveState(true); // Don't broadcast back
                        render();
                    }
                })
                .subscribe();
        }

        async function unirseSala() {
            const input = document.getElementById('room-code-input');
            const code = input?.value.trim();
            if (!code) return showToast('✍️ Escribe un código');
            if (!supabaseClient) return showToast('⚠️ Sin conexión');
            
            const { data, error } = await supabaseClient.from('rooms').select('game_state').eq('code', code).single();
            if (error || !data) return showToast('❌ Sala no encontrada');
            
            state.roomCode = code;
            const localUser = state.user;
            state = { ...data.game_state, user: localUser };
            saveState(true);
            conectarSala(code);
            showToast('✅ Conectado a la sala');
            render();
        }

        function abandonarSala() {
            if (realtimeChannel) {
                supabaseClient.removeChannel(realtimeChannel);
                realtimeChannel = null;
            }
            state.roomCode = null;
            saveState();
            render();
        }

"""
    html = html.replace(old_sala_funcs.group(0), new_sala_funcs)
else:
    print("❌ old_sala_funcs no encontrado")


# 3. Add Multijugador button to Menu
menu_btn = """                    <!-- Modo Multijugador Global -->
                    <button onclick="changeView('onlineRoom')" class="w-full glass p-6 rounded-3xl flex items-center gap-4 btn-hover card-shadow group border-emerald-500/20 ripple touch-feedback mt-4 relative overflow-hidden">
                        ${state.roomCode ? '<div class="absolute inset-0 bg-emerald-500/10 animate-pulse"></div>' : ''}
                        <div class="bg-emerald-500/20 p-4 rounded-2xl group-hover:bg-emerald-500/30 transition-colors z-10">
                            <span class="text-2xl">${state.roomCode ? '🟢' : '🌐'}</span>
                        </div>
                        <div class="text-left z-10">
                            <h2 class="text-lg font-bold ${state.roomCode ? 'text-emerald-400' : 'text-emerald-500'}">SALA MULTIJUGADOR</h2>
                            <p class="text-slate-400 text-sm">${state.roomCode ? 'Conectado a sala: ' + state.roomCode : 'Sincroniza pantallas en vivo'}</p>
                        </div>
                    </button>
                    
                    <!-- Juegos de Cartas -->"""
html = html.replace('                    <!-- Juegos de Cartas -->', menu_btn)


# 4. Remove Room UI from ultimaCarta
room_ui_pattern = r'                    <!-- Sala Online -->.*?</div>\s*</div>\s*(?=            `)'
# wait, it's easier to find exactly
old_room_ui = """                    <!-- Sala Online -->
                    <div id="room-section" class="glass p-6 rounded-3xl border border-white/5 space-y-4">
                        <h3 class="font-bold text-lg">Modo Online</h3>
                        
                        ${state.roomCode ? `
                        <div class="text-center space-y-2">
                            <p class="text-slate-400 text-sm">Código de Sala</p>
                            <div class="room-code-display">${state.roomCode}</div>
                            <button onclick="abandonarSala()" class="text-red-400 text-sm font-bold touch-feedback mt-2">Abandonar Sala</button>
                        </div>
                        ` : `
                        <button onclick="crearSala()" class="w-full bg-slate-800 p-3 rounded-xl font-bold touch-feedback ripple border border-white/10 hover:border-amber-500/50">Crear Nueva Sala</button>
                        <div class="flex gap-2">
                            <input type="text" id="room-code-input" placeholder="Código de Sala" class="flex-1 bg-slate-800 px-4 py-2 rounded-xl text-white focus:outline-none focus:ring-1 focus:ring-amber-500">
                            <button onclick="unirseSala()" class="bg-amber-500/20 text-amber-400 px-4 py-2 rounded-xl font-bold touch-feedback ripple">Unirse</button>
                        </div>
                        `}
                    </div>"""
html = html.replace(old_room_ui, "")


# 5. Add onlineRoom view
views_insert_idx = html.find('        const views = {\n            welcome: () => `')
if views_insert_idx != -1:
    onlineRoom_view = """        const views = {
            onlineRoom: () => `
                <div class="space-y-6 animate-fade-in py-4">
                    <div class="text-center space-y-2">
                        <div style="font-size:3rem;">🌐</div>
                        <h2 class="text-3xl font-black gradient-gold uppercase">Multijugador</h2>
                        <p class="text-slate-400 text-sm">Sincroniza todos los juegos en vivo</p>
                    </div>

                    ${state.roomCode ? `
                    <div class="glass p-6 rounded-3xl border border-emerald-500/20 text-center space-y-4 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                        <p class="text-emerald-400 font-bold uppercase tracking-widest text-xs">Conectado a Sala</p>
                        <div class="room-code-display text-5xl font-black tracking-[0.2em] text-emerald-400 drop-shadow-md">
                            ${state.roomCode}
                        </div>
                        <p class="text-slate-400 text-sm">Cualquier juego que abras se sincronizará con todos los de esta sala al instante.</p>
                        
                        <div class="grid grid-cols-2 gap-3 mt-4">
                            <button onclick="changeView('menu')" class="bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-3 rounded-xl font-bold touch-feedback ripple text-white">
                                Jugar Ahora
                            </button>
                            <button onclick="abandonarSala()" class="bg-red-500/10 text-red-400 border border-red-500/30 px-4 py-3 rounded-xl font-bold touch-feedback ripple">
                                Desconectar
                            </button>
                        </div>
                    </div>
                    ` : `
                    <div class="glass p-6 rounded-3xl border border-white/10 space-y-6">
                        <button onclick="crearSala()" class="w-full p-4 rounded-2xl font-black text-slate-950 text-lg uppercase shadow-xl touch-feedback ripple" style="background:linear-gradient(135deg,#10b981,#059669);">
                            Crear Nueva Sala
                        </button>
                        
                        <div class="relative flex items-center py-2">
                            <div class="flex-grow border-t border-slate-700"></div>
                            <span class="flex-shrink-0 mx-4 text-slate-500 text-sm font-bold uppercase">o únete a una</span>
                            <div class="flex-grow border-t border-slate-700"></div>
                        </div>

                        <div class="flex gap-2">
                            <input type="text" id="room-code-input" placeholder="Código de 6 dígitos" 
                                   class="flex-1 bg-slate-800 px-4 py-3 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-center font-mono tracking-widest text-lg"
                                   maxlength="6">
                            <button onclick="unirseSala()" class="glass bg-white/5 border border-white/10 px-6 py-3 rounded-xl font-bold touch-feedback ripple hover:bg-white/10 text-emerald-400">
                                Entrar
                            </button>
                        </div>
                    </div>
                    `}
                    
                    <button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-white touch-feedback mt-6">
                        Volver al Menú
                    </button>
                </div>
            `,
            welcome: () => `"""
    html = html.replace('        const views = {\n            welcome: () => `', onlineRoom_view)

# 6. Make sure to reconnect to room on page load if state.roomCode exists!
# In the script bottom load initialization:
load_logic = """        // Initialize Supabase now that consts are defined
        initSupabase();
        checkSession();"""

new_load_logic = """        // Initialize Supabase now that consts are defined
        initSupabase();
        checkSession();
        if (state.roomCode) {
            conectarSala(state.roomCode);
        }"""
html = html.replace(load_logic, new_load_logic)


with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ INICIAR.html modificado: Salas Globales sincronizadas")
