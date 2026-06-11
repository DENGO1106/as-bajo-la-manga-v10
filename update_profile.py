import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update routing on load
# Change: if (state.players.length < 2) state.view = 'setup';
# To: if (!savedState) state.view = 'welcome'; else if (state.players.length < 2) state.view = 'welcome';
old_route = "        if (state.players.length < 2) state.view = 'setup';"
new_route = "        if (!savedState) state.view = 'welcome'; else if (state.players.length < 2) state.view = 'welcome';"
html = html.replace(old_route, new_route)

# 2. Update checkSession() logic
old_check = """        async function checkSession() {
            if (!supabaseClient) return;
            const { data: { session } } = await supabaseClient.auth.getSession();
            state.user = session ? session.user : null;
            
            supabaseClient.auth.onAuthStateChange((_event, session) => {
                state.user = session ? session.user : null;
                saveState();
                render();
            });
        }"""

new_check = """        async function checkSession() {
            if (!supabaseClient) return;
            const { data: { session } } = await supabaseClient.auth.getSession();
            state.user = session ? session.user : null;
            
            if (state.user) {
                const savedPlayers = state.user.user_metadata?.saved_players || [];
                if (savedPlayers.length >= 2 && state.players.length < 2) {
                    state.players = JSON.parse(JSON.stringify(savedPlayers));
                    state.view = 'menu';
                    saveState();
                }
            }
            
            supabaseClient.auth.onAuthStateChange((_event, session) => {
                state.user = session ? session.user : null;
                if (state.user && state.players.length < 2) {
                    const savedPlayers = state.user.user_metadata?.saved_players || [];
                    if (savedPlayers.length >= 2) {
                        state.players = JSON.parse(JSON.stringify(savedPlayers));
                        state.view = 'menu';
                    }
                }
                saveState();
                render();
            });
        }

        async function updateProfilePlayers(playersArray) {
            if (!supabaseClient || !state.user) return;
            const { data, error } = await supabaseClient.auth.updateUser({
                data: { saved_players: playersArray }
            });
            if (error) {
                showToast('❌ Error guardando: ' + error.message);
            } else {
                state.user = data.user;
                showToast('✅ Jugadores guardados en la nube');
                saveState();
                render();
            }
        }

        function addProfilePlayer() {
            const input = document.getElementById('profilePlayerInput');
            const name = input?.value.trim();
            if (!name) return showToast('✍️ Escribe un nombre');
            const saved = state.user?.user_metadata?.saved_players || [];
            if (saved.some(p => p.name.toLowerCase() === name.toLowerCase())) return showToast('⚠️ Ya existe');
            if (saved.length >= 20) return showToast('⚠️ Máximo 20 jugadores');
            saved.push({ name: name, score: 0 });
            updateProfilePlayers(saved);
        }

        function removeProfilePlayer(index) {
            const saved = state.user?.user_metadata?.saved_players || [];
            saved.splice(index, 1);
            updateProfilePlayers(saved);
        }

        function startWithProfilePlayers() {
            const saved = state.user?.user_metadata?.saved_players || [];
            if (saved.length < 2) return showToast('⚠️ Necesitas al menos 2 jugadores');
            state.players = JSON.parse(JSON.stringify(saved));
            state.view = 'menu';
            saveState();
            render();
        }"""
html = html.replace(old_check, new_check)

# 3. Insert new views (welcome, profile)
views_insert_idx = html.find('        const views = {\n            menu: () => `')
if views_insert_idx == -1:
    print("❌ No se encontro views = { menu:")
    sys.exit(1)

new_views = """        const views = {
            welcome: () => `
                <div class="space-y-8 animate-fade-in py-8 flex flex-col items-center justify-center min-h-[70vh]">
                    <div class="text-center space-y-4">
                        <div style="font-size:4rem;" class="mb-4">🃏</div>
                        <h1 class="text-4xl font-black gradient-gold uppercase tracking-tighter">As Bajo La Manga</h1>
                        <p class="text-slate-400 text-lg">Elige cómo quieres entrar al juego</p>
                    </div>

                    <div class="w-full max-w-sm space-y-4">
                        <button onclick="changeView('auth')" class="w-full p-4 rounded-2xl font-black text-slate-950 text-lg shadow-xl touch-feedback ripple" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                            🔐 Iniciar con Cuenta
                        </button>
                        
                        <div class="relative flex items-center py-2">
                            <div class="flex-grow border-t border-slate-700"></div>
                            <span class="flex-shrink-0 mx-4 text-slate-500 text-sm font-bold uppercase">o</span>
                            <div class="flex-grow border-t border-slate-700"></div>
                        </div>

                        <button onclick="changeView('setup')" class="w-full glass p-4 rounded-2xl font-bold text-white border border-white/10 touch-feedback ripple">
                            👤 Jugar como Invitado
                        </button>
                    </div>
                </div>
            `,

            profile: () => `
                <div class="space-y-6 animate-fade-in py-4">
                    <div class="text-center space-y-2">
                        <div style="font-size:3rem;">👤</div>
                        <h2 class="text-3xl font-black gradient-gold uppercase">Mi Perfil</h2>
                        <p class="text-slate-400 text-sm font-bold text-amber-400">@${state.user?.email?.split('@')[0] || 'usuario'}</p>
                    </div>

                    <div class="glass p-6 rounded-3xl border border-white/10 space-y-4">
                        <h3 class="font-bold text-lg text-white mb-2">Mis Jugadores Frecuentes</h3>
                        
                        <div class="flex gap-2 mb-4">
                            <input type="text" id="profilePlayerInput"
                                   placeholder="Nombre del jugador"
                                   class="flex-1 bg-slate-800 px-4 py-3 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                                   onkeypress="if(event.key==='Enter') addProfilePlayer()" />
                            <button onclick="addProfilePlayer()" class="bg-gradient-to-r from-amber-500 to-orange-600 px-4 py-3 rounded-xl font-bold touch-feedback ripple">➕</button>
                        </div>

                        <div class="space-y-2 max-h-[300px] overflow-y-auto">
                            ${(state.user?.user_metadata?.saved_players || []).length === 0
                                ? '<div class="text-center text-slate-500 py-4">No tienes jugadores guardados</div>'
                                : (state.user?.user_metadata?.saved_players || []).map((p, i) => `
                                <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                                    <div class="flex items-center gap-3">
                                        <span class="text-xl">${['🔵','🟢','🟡','🔴','🟣','🟠'][i % 6]}</span>
                                        <span class="font-bold">${p.name}</span>
                                    </div>
                                    <button onclick="removeProfilePlayer(${i})" class="text-red-500 hover:text-red-400 px-3 py-1 rounded-lg touch-feedback">✕</button>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <div class="space-y-3">
                        <button onclick="startWithProfilePlayers()" class="w-full p-4 rounded-2xl font-black text-slate-950 touch-feedback ripple ${((state.user?.user_metadata?.saved_players || []).length >= 2) ? '' : 'opacity-50 pointer-events-none'}" style="background:linear-gradient(135deg,#10b981,#059669);">
                            ▶️ Jugar con estos jugadores
                        </button>

                        <button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-white touch-feedback">
                            Volver al Menú
                        </button>

                        <button onclick="signOutSupabase()" class="w-full glass bg-red-500/10 text-red-400 border border-red-500/30 p-4 rounded-2xl font-bold touch-feedback ripple mt-4">
                            Cerrar Sesión
                        </button>
                    </div>
                </div>
            `,
            menu: () => `"""
html = html.replace('        const views = {\n            menu: () => `', new_views)

# 4. Modify Menu Profile Button
old_menu_btn = """                    <!-- Auth Button -->
                    <button onclick="changeView('auth')" class="absolute top-4 right-4 glass p-2 rounded-xl text-xl touch-feedback border z-50 ${state.user ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/20 text-amber-400'}">
                        ${state.user ? '🔓' : '🔐'}
                    </button>"""

new_menu_btn = """                    <!-- Profile Button -->
                    <button onclick="changeView(state.user ? 'profile' : 'welcome')" class="absolute top-4 right-4 glass p-2 rounded-xl text-xl touch-feedback border z-50 ${state.user ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10' : 'border-amber-500/20 text-amber-400'}">
                        ${state.user ? '👤' : '🔐'}
                    </button>"""
html = html.replace(old_menu_btn, new_menu_btn)

# 5. Modify Auth view "Volver" button
# Change: <button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">← Volver al Menú</button>
# To: <button onclick="changeView('welcome')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">← Volver</button>
html = html.replace("""<button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">← Volver al Menú</button>""", """<button onclick="changeView('welcome')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">← Volver</button>""")

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ INICIAR.html actualizado con vistas de Perfil y Welcome")
