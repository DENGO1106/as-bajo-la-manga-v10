import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', encoding='utf-8') as f:
    html = f.read()

# 1. CSS
CSS_INJECT = """
        /* SUPABASE REALTIME CSS */
        .pulse-border { animation: pulseBorder 2s infinite; }
        @keyframes pulseBorder {
            0% { border-color: rgba(245,158,11,0.2); }
            50% { border-color: rgba(245,158,11,0.8); }
            100% { border-color: rgba(245,158,11,0.2); }
        }
        .room-code-display {
            font-family: monospace;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: 0.2em;
            color: #fbbf24;
            text-shadow: 0 0 20px rgba(245,158,11,0.4);
        }
        /* ADMIN LOCKSCREEN */
        #admin-lockscreen {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.98);
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            z-index: 99999; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            transition: opacity 0.5s ease;
        }
        #admin-lockscreen.unlocking { opacity: 0; pointer-events: none; }
        .lock-shake { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }
        @keyframes shake {
            10%, 90% { transform: translate3d(-1px, 0, 0); }
            20%, 80% { transform: translate3d(2px, 0, 0); }
            30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
            40%, 60% { transform: translate3d(4px, 0, 0); }
        }
        .pin-dot {
            width: 16px; height: 16px; border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.2);
            transition: all 0.2s;
        }
        .pin-dot.filled { background: #fbbf24; border-color: #fbbf24; box-shadow: 0 0 10px rgba(245,158,11,0.5); }
        .card-suit-red { color: #ef4444; }
        .card-suit-black { color: #f8fafc; }
        .step-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.2); transition: all 0.3s; }
        .step-dot.active { background: #fbbf24; transform: scale(1.5); }
        .step-dot.done { background: #10b981; }
        .card-reveal { animation: reveal 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) both; }
        @keyframes reveal {
            0% { transform: rotateY(90deg) scale(0.8); opacity: 0; }
            100% { transform: rotateY(0deg) scale(1); opacity: 1; }
        }
"""
idx_css = html.find('        /* Prevent pull-to-refresh')
if idx_css != -1:
    html = html[:idx_css] + CSS_INJECT + html[idx_css:]
    print("✅ CSS insertado")

# 1.5 ESTADO INICIAL
STATE_INJECT = """
            // Supabase / Ultima Carta
            roomState: null,
            ultimaCarta: null,
"""
idx_state = html.find('            // Otros\\n            swipeDirection: null')
if idx_state != -1:
    html = html[:idx_state] + STATE_INJECT + html[idx_state:]
    print("✅ Estado inicial insertado")
else:
    print("❌ No se encontró el estado inicial")

# 1.6 CAS helper injection for generated JS
CAS_HELPER = """
        // --- casUpdateRoom helper (injected by build_game) ---
        async function casUpdateRoom(code, payloadOrBuilder, knownLastActivity = null) {
            if (!window.supabaseClient) return { error: 'no supabase' };
            try {
                let payload = payloadOrBuilder;
                if (typeof payloadOrBuilder === 'function') {
                    const rowRes = await window.supabaseClient.from('rooms').select('game_state, last_activity').eq('code', code).single();
                    const row = rowRes.data || {};
                    payload = payloadOrBuilder(row);
                    if (payload === null) return { skipped: true };
                }
                const newLast = new Date().toISOString();
                payload.last_activity = newLast;
                let res;
                if (knownLastActivity) {
                    res = await window.supabaseClient.from('rooms').update(payload).eq('code', code).eq('last_activity', knownLastActivity);
                    if (res.error) {
                        console.warn('casUpdateRoom CAS failed, fallback', res.error);
                        res = await window.supabaseClient.from('rooms').update(payload).eq('code', code);
                    }
                } else {
                    const rowRes = await window.supabaseClient.from('rooms').select('last_activity').eq('code', code).single();
                    const last = rowRes.data ? rowRes.data.last_activity : null;
                    if (last) {
                        res = await window.supabaseClient.from('rooms').update(payload).eq('code', code).eq('last_activity', last);
                        if (res.error) {
                            console.warn('casUpdateRoom CAS failed, fallback', res.error);
                            res = await window.supabaseClient.from('rooms').update(payload).eq('code', code);
                        }
                    } else {
                        res = await window.supabaseClient.from('rooms').update(payload).eq('code', code);
                    }
                }
                return res;
            } catch (e) {
                console.warn('casUpdateRoom error', e);
                return { error: e };
            }
        }
"""
idx_helpers = html.find('        // --- Multiplayer helpers ---')
if idx_helpers != -1:
    html = html[:idx_helpers] + CAS_HELPER + html[idx_helpers:]
    print("✅ CAS helper insertado")
else:
    print("❌ No se encontró el lugar para insertar CAS helper")

# 2. SDK SUPABASE
SDK_INJECT = """    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
"""
idx_sdk = html.find('<script src="https://cdn.tailwindcss.com"></script>')
if idx_sdk != -1:
    html = html[:idx_sdk] + SDK_INJECT + html[idx_sdk:]
    print("✅ SDK insertado")

# 3. ADMIN GATE HTML
LOCKSCREEN_HTML = """
    <!-- ========================================== -->
    <!-- ADMIN LOCKSCREEN (GATE DE ACCESO)          -->
    <!-- ========================================== -->
    <div id="admin-lockscreen">
        <div class="text-center space-y-6 w-full max-w-sm px-6">
            <div class="w-24 h-24 bg-slate-800 rounded-3xl mx-auto flex items-center justify-center border border-white/5 shadow-2xl mb-8">
                <span style="font-size: 3rem;">🔒</span>
            </div>
            
            <div id="admin-numpad" class="space-y-6 hidden">
                <div class="flex justify-center gap-3 mb-8">
                    <div id="pd0" class="pin-dot"></div><div id="pd1" class="pin-dot"></div>
                    <div id="pd2" class="pin-dot"></div><div id="pd3" class="pin-dot"></div>
                    <div id="pd4" class="pin-dot"></div><div id="pd5" class="pin-dot"></div>
                    <div id="pd6" class="pin-dot"></div><div id="pd7" class="pin-dot"></div>
                </div>
                <div class="grid grid-cols-3 gap-4">
                    <!-- Numbers 1-9 -->
                    <button onclick="adminPinInput('1')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">1</button>
                    <button onclick="adminPinInput('2')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">2</button>
                    <button onclick="adminPinInput('3')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">3</button>
                    <button onclick="adminPinInput('4')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">4</button>
                    <button onclick="adminPinInput('5')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">5</button>
                    <button onclick="adminPinInput('6')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">6</button>
                    <button onclick="adminPinInput('7')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">7</button>
                    <button onclick="adminPinInput('8')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">8</button>
                    <button onclick="adminPinInput('9')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">9</button>
                    <!-- Bottom row -->
                    <button onclick="adminPinClear()" class="h-16 rounded-2xl bg-red-500/10 text-xl font-bold text-red-400 border border-red-500/20 active:bg-red-500/30">⌫</button>
                    <button onclick="adminPinInput('0')" class="h-16 rounded-2xl bg-slate-800/50 text-2xl font-bold text-white border border-white/5 active:bg-slate-700">0</button>
                    <button onclick="adminPinSubmit()" class="h-16 rounded-2xl bg-amber-500/10 text-xl font-bold text-amber-400 border border-amber-500/20 active:bg-amber-500/30">OK</button>
                </div>
            </div>

            <div id="admin-textpad" class="space-y-4">
                <input id="admin-text-input" type="password" placeholder="Contraseña de acceso" 
                       class="w-full bg-slate-800 px-6 py-4 rounded-2xl text-center text-white text-lg tracking-widest focus:outline-none focus:ring-2 focus:ring-amber-500 border border-white/10"
                       onkeydown="if(event.key === 'Enter') adminTextSubmit()">
                <button onclick="adminTextSubmit()" class="w-full p-4 rounded-2xl font-black text-slate-950 text-lg uppercase shadow-xl" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                    Desbloquear
                </button>
            </div>

            <p id="admin-error-msg" class="text-red-400 font-bold h-6 text-sm"></p>
            <p class="text-xs text-slate-500 font-medium">As Bajo La Manga — Acceso Restringido</p>
        </div>
    </div>
"""
idx_body = html.find('<body class="min-h-screen flex flex-col">')
if idx_body != -1:
    idx_body += len('<body class="min-h-screen flex flex-col">')
    html = html[:idx_body] + '\n' + LOCKSCREEN_HTML + html[idx_body:]
    print("✅ Lockscreen insertado")

# 4. BOTON ULTIMA CARTA (MENU)
BTN_INJECT = """
                    <!-- La Ultima Carta -->
                    <button onclick="changeView('ultimaCarta')" class="game-card group touch-feedback relative overflow-hidden glass rounded-3xl p-6 border-amber-500/20">
                        <div class="absolute -right-4 -top-4 text-6xl opacity-10 group-hover:rotate-12 transition-transform duration-500">🃏</div>
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-4xl filter drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]">🃏</span>
                            <span class="bg-amber-500/20 text-amber-400 text-[10px] font-black px-3 py-1 rounded-full border border-amber-500/30 uppercase tracking-widest shadow-[0_0_10px_rgba(245,158,11,0.3)]">
                                VIP
                            </span>
                        </div>
                        <div class="text-left relative z-10">
                            <h2 class="text-2xl font-black text-white mb-2 uppercase tracking-tight group-hover:text-amber-400 transition-colors">La Última Carta</h2>
                            <p class="text-slate-400 text-sm font-medium leading-relaxed">El clásico juego de apuestas, ahora online y presencial.</p>
                        </div>
                    </button>
"""
idx_bib = html.find('                    <!-- Biblioteca -->')
if idx_bib != -1:
    html = html[:idx_bib] + BTN_INJECT + '\n' + html[idx_bib:]
    print("✅ Boton menu insertado")

# 5. VISTAS
VIEWS_INJECT = """
            ultimaCarta: () => {
                // Lobby de configuración inicial
                if (!state.ultimaCarta || !state.ultimaCarta.active) {
                    const players = state.players || [];
                    return `
                    <div class="space-y-6 animate-fade-in py-4">
                        <div class="text-center space-y-2">
                            <div style="font-size:4rem;" class="filter drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">🃏</div>
                            <h2 class="text-3xl font-black gradient-gold uppercase">La Última Carta</h2>
                            <p class="text-slate-400 text-sm">Torneo de apuestas y riesgo</p>
                        </div>

                        ${players.length < 2 ? `
                        <div class="glass p-4 rounded-2xl border border-red-500/20 text-center">
                            <p class="text-red-400 text-sm">⚠️ Necesitás al menos 2 jugadores</p>
                            <button onclick="changeView('setup')" class="mt-3 bg-red-500/20 text-red-300 px-4 py-2 rounded-xl text-sm font-bold border border-red-500/30 touch-feedback">➕ Agregar jugadores</button>
                        </div>
                        ` : ''}

                        <!-- Modos de juego -->
                        ${players.length >= 2 ? `
                        <div class="space-y-3">
                            <button onclick="initUltimaCartaLocal()" class="w-full p-5 rounded-3xl font-black text-slate-950 text-lg uppercase card-shadow touch-feedback ripple" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                                🎮 Jugar en Este Dispositivo
                            </button>
                            <button onclick="changeView('roomLobby')" class="w-full glass p-4 rounded-2xl font-bold text-amber-400 border border-amber-500/20 touch-feedback ripple flex items-center justify-center gap-2">
                                📡 Crear / Unirse a Sala Online
                            </button>
                        </div>
                        ` : ''}

                        <button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">← Volver al Menú</button>
                    </div>`;
                }

                // Juego activo
                const uc = state.ultimaCarta;
                const phase = uc.phase;
                const player = uc.players[uc.currentPlayerIndex];
                const stepNames = ['¿Par o Impar?','¿Mayor o Menor?','¿Rojo o Negro?','¿Palo?'];
                const stepPoints = [1, 2, 3, 4];

                // Marcador compacto
                const scoreBoard = `
                    <div class="glass p-3 rounded-2xl border border-white/5 mb-4">
                        <div class="flex gap-2 overflow-x-auto pb-1">
                            ${uc.players.map((pl,i) => `
                                <div class="flex-shrink-0 text-center px-3 py-2 rounded-xl ${i === uc.currentPlayerIndex ? 'bg-amber-500/20 border border-amber-500/40' : 'bg-slate-800/50'}">
                                    <p class="text-[10px] text-slate-400">${pl.name.substring(0,8)}</p>
                                    <p class="font-black text-lg ${pl.score >= 0 ? 'text-emerald-400' : 'text-red-400'}">${pl.score >= 0 ? '+' : ''}${pl.score}</p>
                                    <p class="text-[9px] text-slate-500">R${Math.min(pl.turnsPlayed + 1, 3)}/3</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>`;

                if (phase === 'cobarde') {
                    return `
                    <div class="space-y-5 animate-fade-in py-4">
                        ${scoreBoard}
                        <div class="text-center space-y-1">
                            <p class="text-xs text-amber-400 font-bold uppercase tracking-widest">Turno ${uc.currentRound}/${uc.totalRounds}</p>
                            <h2 class="text-2xl font-black uppercase">${player.name}</h2>
                        </div>
                        <div class="glass p-8 rounded-3xl text-center space-y-6 border border-amber-500/20">
                            <div style="font-size:3.5rem;">⚠️</div>
                            <div>
                                <h3 class="text-xl font-black text-amber-400 uppercase">Regla del Cobarde</h3>
                                <p class="text-slate-400 mt-2 text-sm">Podés declarar "No juego" antes de que el Dealer tire la primera carta.</p>
                                <p class="text-slate-300 mt-1 text-sm">Si no jugás: <span class="text-red-400 font-bold">1 trago</span> pero mantenés tu puntaje.</p>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <button onclick="ucCobarde()" class="glass p-4 rounded-2xl font-black text-red-400 border border-red-500/30 touch-feedback ripple">
                                🏳️ No juego<br><span class="text-xs text-slate-400 font-normal">1 trago</span>
                            </button>
                            <button onclick="ucStartEscalera()" class="p-4 rounded-2xl font-black text-slate-950 touch-feedback ripple" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                                ▶️ Jugar<br><span class="text-xs font-normal">Arriesgar</span>
                            </button>
                        </div>
                    </div>`;
                }

                if (phase === 'escalera') {
                    const step = uc.currentStep; // 0-3
                    const card = uc.drawnCards[step];
                    const prevCard = step > 0 ? uc.drawnCards[step - 1] : null;
                    const isRed = card && ['♥', '♦'].includes(card.suit);

                    if (!card) return `<div class="text-center py-8"><p>Error: carta no disponible</p></div>`;

                    // Indicadores de pasos
                    const stepDots = Array.from({length:4}, (_,i) => {
                        let cls = 'step-dot';
                        if (i < step) cls += ' done';
                        else if (i === step) cls += ' active';
                        return `<div class="${cls}"></div>`;
                    }).join('');

                    const cardDisplay = uc.revealed ? `
                        <div class="card-reveal flex flex-col items-center justify-center gap-2">
                            <span class="text-7xl font-black ${isRed ? 'card-suit-red' : 'card-suit-black'}">${card.rank}</span>
                            <span class="text-5xl ${isRed ? 'card-suit-red' : 'card-suit-black'}">${card.suit}</span>
                            ${step === 0 ? `<span class="text-sm text-slate-400 mt-1">${card.value % 2 === 0 ? 'Par ✓' : 'Impar ✓'}</span>` : ''}
                        </div>
                    ` : `
                        <div class="flex flex-col items-center gap-2 opacity-60">
                            <span class="text-7xl">🂠</span>
                            <span class="text-slate-400 text-sm">Carta boca abajo</span>
                        </div>
                    `;

                    // Botones según el paso y estado
                    let actionButtons = '';
                    if (!uc.revealed) {
                        if (step === 0) { // Par/Impar
                            actionButtons = `
                            <div class="grid grid-cols-2 gap-3">
                                <button onclick="ucGuess('par')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple text-lg">Par<br><span class="text-xs font-normal text-slate-400">2,4,6,8,10,Q</span></button>
                                <button onclick="ucGuess('impar')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple text-lg">Impar<br><span class="text-xs font-normal text-slate-400">3,5,7,9,J,K</span></button>
                            </div>`;
                        } else if (step === 1) { // Mayor/Menor
                            actionButtons = `
                            <div class="space-y-2">
                                <p class="text-center text-xs text-slate-400">Carta anterior: <span class="font-bold text-white">${prevCard.rank}${prevCard.suit}</span> (${prevCard.value})</p>
                                <div class="grid grid-cols-2 gap-3">
                                    <button onclick="ucGuess('mayor')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple text-lg">Mayor ↑<br><span class="text-xs font-normal text-slate-400">&gt; ${prevCard.value}</span></button>
                                    <button onclick="ucGuess('menor')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple text-lg">Menor ↓<br><span class="text-xs font-normal text-slate-400">&lt; ${prevCard.value}</span></button>
                                </div>
                            </div>`;
                        } else if (step === 2) { // Rojo/Negro
                            actionButtons = `
                            <div class="grid grid-cols-2 gap-3">
                                <button onclick="ucGuess('rojo')" class="glass p-4 rounded-2xl font-black text-red-400 border border-red-500/30 touch-feedback ripple text-lg">🔴 Rojo<br><span class="text-xs font-normal text-slate-400">♥ ♦</span></button>
                                <button onclick="ucGuess('negro')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple text-lg">⚫ Negro<br><span class="text-xs font-normal text-slate-400">♠ ♣</span></button>
                            </div>`;
                        } else if (step === 3) { // Palo
                            actionButtons = `
                            <div class="grid grid-cols-2 gap-3">
                                <button onclick="ucGuess('♠')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple">♠ Pica</button>
                                <button onclick="ucGuess('♥')" class="glass p-4 rounded-2xl font-black text-red-400 border border-red-500/20 touch-feedback ripple">♥ Corazón</button>
                                <button onclick="ucGuess('♦')" class="glass p-4 rounded-2xl font-black text-red-400 border border-red-500/20 touch-feedback ripple">♦ Diamante</button>
                                <button onclick="ucGuess('♣')" class="glass p-4 rounded-2xl font-black text-white border border-white/20 touch-feedback ripple">♣ Trébol</button>
                            </div>`;
                        }
                    } else if (uc.lastGuessCorrect) {
                        // Adivinó correctamente
                        actionButtons = step < 3 ? `
                        <div class="space-y-3">
                            <div class="bg-emerald-500/20 border border-emerald-500/40 rounded-2xl p-4 text-center">
                                <p class="text-emerald-400 font-black text-lg">✅ ¡Correcto! +${stepPoints[step]} pto${stepPoints[step]>1?'s':''}</p>
                                <p class="text-slate-400 text-xs mt-1">Tragos acumulados: ${uc.currentDrinks}</p>
                            </div>
                            <div class="grid grid-cols-2 gap-3">
                                <button onclick="ucPlantarse()" class="glass p-4 rounded-2xl font-bold text-slate-300 border border-white/10 touch-feedback ripple">
                                    🛑 Plantarse<br><span class="text-xs font-normal text-slate-400">Guardar puntos</span>
                                </button>
                                <button onclick="ucContinuar()" class="p-4 rounded-2xl font-black text-slate-950 touch-feedback ripple" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                                    ▶️ Continuar<br><span class="text-xs font-normal">+${stepPoints[step+1]} pts</span>
                                </button>
                            </div>
                        </div>` : `
                        <div class="space-y-3">
                            <div class="bg-emerald-500/20 border border-emerald-500/40 rounded-2xl p-4 text-center">
                                <p class="text-emerald-400 font-black text-xl">🏆 ¡Escalera Completa!</p>
                                <p class="text-slate-300 mt-1">+${uc.currentPoints} puntos ganados</p>
                                <p class="text-slate-400 text-xs">Tragos: ${uc.currentDrinks}</p>
                            </div>
                            <button onclick="ucFinalizarTurno(true)" class="w-full p-5 rounded-2xl font-black text-slate-950 text-lg touch-feedback ripple" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                                Finalizar Turno ✓
                            </button>
                        </div>`;
                    } else {
                        // Falló
                        actionButtons = step < 3 ? `
                        <div class="space-y-3">
                            <div class="bg-red-500/20 border border-red-500/40 rounded-2xl p-4 text-center">
                                <p class="text-red-400 font-black text-lg">❌ ¡Incorrecto! +1 trago</p>
                                <p class="text-slate-400 text-xs mt-1">Tragos acumulados: ${uc.currentDrinks}</p>
                            </div>
                            <div class="grid grid-cols-2 gap-3">
                                <button onclick="ucAceptarDerrota()" class="glass p-4 rounded-2xl font-bold text-red-400 border border-red-500/30 touch-feedback ripple">
                                    🍺 Aceptar<br><span class="text-xs font-normal text-slate-400">${uc.currentDrinks} trago${uc.currentDrinks!==1?'s':''}</span>
                                </button>
                                <button onclick="ucRevancha()" class="p-4 rounded-2xl font-black text-slate-950 touch-feedback ripple" style="background:linear-gradient(135deg,#ef4444,#dc2626);">
                                    ⚔️ Revancha<br><span class="text-xs font-normal">Carta ${step+2}</span>
                                </button>
                            </div>
                        </div>` : `
                        <div class="space-y-3">
                            <div class="bg-red-500/20 border border-red-500/40 rounded-2xl p-4 text-center">
                                <p class="text-red-400 font-black">❌ Carta 4 fallada — sin revancha</p>
                                <p class="text-slate-300 mt-1">Tragos: ${uc.currentDrinks}</p>
                            </div>
                            <button onclick="ucAceptarDerrota()" class="w-full bg-red-600 p-4 rounded-2xl font-black text-white text-lg touch-feedback ripple">
                                🍺 Aceptar derrota
                            </button>
                        </div>`;
                    }

                    return `
                    <div class="space-y-4 animate-fade-in py-4">
                        ${scoreBoard}
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-xs text-amber-400 font-bold uppercase tracking-widest">Carta ${step+1}/4 — ${stepNames[step]}</p>
                                <h2 class="text-xl font-black uppercase">${player.name}</h2>
                            </div>
                            <div class="flex gap-1">${stepDots}</div>
                        </div>
                        <div class="glass p-8 rounded-3xl flex flex-col items-center justify-center min-h-[200px] border border-amber-500/20 relative overflow-hidden">
                            <div class="absolute -top-8 -right-8 text-8xl opacity-5">🃏</div>
                            <div class="text-center">${cardDisplay}</div>
                            ${uc.revealed && uc.currentPoints > 0 ? `<div class="mt-4 bg-amber-500/10 px-4 py-2 rounded-xl border border-amber-500/20"><p class="text-amber-400 font-bold text-sm">Total turno: +${uc.currentPoints} pts</p></div>` : ''}
                        </div>
                        ${actionButtons}
                    </div>`;
                }

                if (phase === 'revancha') {
                    const card = uc.revanchaCard;
                    const isRed = card && ['♥', '♦'].includes(card.suit);
                    return `
                    <div class="space-y-4 animate-fade-in py-4">
                        ${scoreBoard}
                        <div class="text-center space-y-1">
                            <p class="text-xs text-red-400 font-bold uppercase tracking-widest">⚔️ REVANCHA — Carta ${uc.currentStep+2}</p>
                            <h2 class="text-xl font-black uppercase">${player.name}</h2>
                        </div>
                        <div class="glass p-8 rounded-3xl border border-red-500/40 text-center space-y-2">
                            <p class="text-slate-400 text-xs">Si ganás: cancela trago + <span class="text-emerald-400 font-bold">+${stepPoints[uc.currentStep-1] || 1} pts</span></p>
                            <p class="text-slate-400 text-xs">Si perdés: <span class="text-red-400 font-bold">2 tragos + -${stepPoints[uc.currentStep-1] || 1} pts</span></p>
                            ${card ? `
                            <div class="card-reveal flex flex-col items-center gap-2 mt-4">
                                <span class="text-7xl font-black ${isRed ? 'card-suit-red' : 'card-suit-black'}">${card.rank}</span>
                                <span class="text-5xl ${isRed ? 'card-suit-red' : 'card-suit-black'}">${card.suit}</span>
                            </div>
                            ` : `<div class="text-6xl mt-4">🂠</div>`}
                        </div>
                        ${!card ? `
                        <div class="grid grid-cols-2 gap-3">
                            <button onclick="ucGuessRevancha('mayor')" class="glass p-4 rounded-2xl font-black touch-feedback">Mayor ↑</button>
                            <button onclick="ucGuessRevancha('menor')" class="glass p-4 rounded-2xl font-black touch-feedback">Menor ↓</button>
                        </div>` : `
                        <button onclick="ucFinalizarTurno(${uc.lastRevanchaCorrect})" class="w-full p-4 rounded-2xl font-black text-slate-950 touch-feedback" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                            Continuar →
                        </button>`}
                    </div>`;
                }

                if (phase === 'final') {
                    const sorted = [...uc.players].sort((a,b) => b.score - a.score);
                    const winner = sorted[0];
                    const loser = sorted[sorted.length-1];
                    const isTie = sorted.filter(p => p.score === winner.score).length > 1;

                    return `
                    <div class="space-y-5 animate-fade-in py-4">
                        <div class="text-center space-y-2">
                            <div style="font-size:3rem;">🏆</div>
                            <h2 class="text-3xl font-black gradient-gold uppercase">¡Fin del Torneo!</h2>
                        </div>

                        <!-- Podio -->
                        <div class="space-y-3">
                            ${sorted.map((pl, i) => {
                                const isWinner = pl.score === winner.score;
                                const isLoser = pl.score === loser.score && i === sorted.length-1;
                                return `
                                <div class="glass p-4 rounded-2xl flex items-center gap-4 border ${isWinner ? 'border-amber-500/40 bg-amber-500/5' : isLoser ? 'border-red-500/30 bg-red-500/5' : 'border-white/5'}">
                                    <span class="text-2xl">${isWinner ? '🥇' : i===1 ? '🥈' : isLoser ? '💀' : '🥉'}</span>
                                    <div class="flex-1">
                                        <p class="font-black text-white">${pl.name}</p>
                                        <p class="text-xs text-slate-400">Turno ${pl.turnsPlayed}/3 completados</p>
                                    </div>
                                    <div class="text-right">
                                        <p class="font-black text-xl ${pl.score >= 0 ? 'text-emerald-400' : 'text-red-400'}">${pl.score >= 0 ? '+' : ''}${pl.score}</p>
                                        <p class="text-xs text-slate-500">puntos</p>
                                    </div>
                                </div>`;
                            }).join('')}
                        </div>

                        <!-- Premios/Castigos -->
                        <div class="glass p-5 rounded-3xl border border-amber-500/20 space-y-3">
                            <div class="bg-amber-500/10 rounded-2xl p-4 border border-amber-500/20">
                                <p class="text-amber-400 font-black">🥇 ${winner.name} GANA</p>
                                <p class="text-slate-300 text-sm">${isTie ? 'Empate: reparten' : 'Asigna'} 4 tragos entre los demás</p>
                            </div>
                            <div class="bg-red-500/10 rounded-2xl p-4 border border-red-500/20">
                                <p class="text-red-400 font-black">💀 ${loser.name} PIERDE</p>
                                <p class="text-slate-300 text-sm">Toma 1 trago de castigo</p>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <button onclick="initUltimaCartaLocal()" class="glass p-4 rounded-2xl font-bold text-amber-400 border border-amber-500/30 touch-feedback ripple">
                                🔄 Revancha
                            </button>
                            <button onclick="changeView('menu')" class="glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">
                                🏠 Menú
                            </button>
                        </div>
                    </div>`;
                }

                return `<div class="text-center py-8 text-slate-400">Cargando...</div>`;
            },

            roomLobby: () => {
                const room = state.roomState;
                if (!room || !room.code) {
                    return `
                    <div class="space-y-6 animate-fade-in py-4">
                        <div class="text-center space-y-2">
                            <div style="font-size:3rem;">📡</div>
                            <h2 class="text-2xl font-black gradient-gold uppercase">Sala Online</h2>
                            <p class="text-slate-400 text-sm">Jugá La Última Carta en tiempo real</p>
                        </div>

                        <div class="space-y-4">
                            <!-- Crear sala -->
                            <div class="glass p-6 rounded-3xl border border-amber-500/20 space-y-4">
                                <h3 class="font-black text-amber-400 uppercase text-sm tracking-widest">Crear Nueva Sala</h3>
                                <input id="host-name-input" type="text" placeholder="Tu nombre..."
                                    class="w-full bg-slate-800 px-4 py-3 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                                    value="${state.players && state.players[0] ? (state.players[0].name || '') : ''}" />
                                <button onclick="createRoom()" class="w-full p-4 rounded-2xl font-black text-slate-950 text-lg touch-feedback ripple" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                                    🚀 Crear Sala
                                </button>
                            </div>

                            <!-- Unirse a sala -->
                            <div class="glass p-6 rounded-3xl border border-white/10 space-y-4">
                                <h3 class="font-black text-slate-300 uppercase text-sm tracking-widest">Unirse a Sala Existente</h3>
                                <input id="room-code-input" type="text" placeholder="Código (ej: AS92)"
                                    maxlength="4"
                                    class="w-full bg-slate-800 px-4 py-3 rounded-xl text-white text-center font-black text-xl uppercase focus:outline-none focus:ring-2 focus:ring-amber-500"
                                    oninput="this.value=this.value.toUpperCase()" />
                                <input id="guest-name-input" type="text" placeholder="Tu nombre..."
                                    class="w-full bg-slate-800 px-4 py-3 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-amber-500" />
                                <button onclick="joinRoom()" class="w-full p-4 rounded-2xl font-bold text-white bg-slate-700 hover:bg-slate-600 touch-feedback ripple">
                                    🚪 Unirse
                                </button>
                            </div>
                        </div>

                        <button onclick="changeView('ultimaCarta')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">← Volver</button>
                    </div>`;
                }

                // Sala creada/unida
                const players = room.players || [];
                const isHost = room.isHost;
                return `
                <div class="space-y-6 animate-fade-in py-4">
                    <div class="text-center space-y-3">
                        <p class="text-xs text-amber-400 font-bold uppercase tracking-widest">${isHost ? '👑 Sos el Anfitrión' : '🙋 Estás como Invitado'}</p>
                        <div class="glass p-6 rounded-3xl border pulse-border">
                            <p class="text-slate-400 text-xs mb-1">Código de Sala</p>
                            <div class="room-code-display">${room.code}</div>
                            <p class="text-slate-500 text-xs mt-1">Compartí este código</p>
                        </div>
                    </div>

                    <div class="glass p-5 rounded-3xl border border-white/5">
                        <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Jugadores en Sala (${players.length})</p>
                        <div class="space-y-2">
                            ${players.map((p,i) => `
                                <div class="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                                    <span class="text-xl">${['🔵','🟢','🟡','🔴','🟣','🟠'][i%6]}</span>
                                    <span class="font-bold">${p.name}</span>
                                    ${i === 0 ? '<span class="ml-auto text-xs text-amber-400 font-bold">HOST</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    ${isHost ? `
                    <button onclick="startOnlineGame()" class="w-full p-5 rounded-2xl font-black text-slate-950 text-lg touch-feedback ripple ${players.length < 2 ? 'opacity-50 pointer-events-none' : ''}" style="background:linear-gradient(135deg,#FFD700,#D4AF37);">
                        ${players.length < 2 ? '⏳ Esperando jugadores...' : '▶️ Iniciar Partida'}
                    </button>
                    ` : `
                    <div class="glass p-4 rounded-2xl border border-amber-500/20 text-center">
                        <p class="text-amber-400 text-sm">⏳ Esperando que el host inicie la partida...</p>
                    </div>
                    `}

                    <button onclick="leaveRoom()" class="w-full glass p-4 rounded-2xl font-bold text-red-400 border border-red-500/20 touch-feedback">
                        🚪 Salir de la Sala
                    </button>
                </div>`;
            },
"""

idx_views_close = html.find("        };\n\n        function iniciarJuego(view = 'menu') {")
if idx_views_close != -1:
    html = html[:idx_views_close] + VIEWS_INJECT + html[idx_views_close:]
    print("✅ Vistas insertadas")
else:
    print("❌ No se encontró el cierre de views (function iniciarJuego)")


# 6. FUNCIONES DEL JUEGO
FUNCTIONS_INJECT = """
        // ========================================
        // SUPABASE CONFIG
        // ========================================
        const SUPABASE_URL = 'https://lojhzzwrtyytjbdowayv.supabase.co';
        const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamh6endydHl5dGpiZG93YXl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0NTIzNDMsImV4cCI6MjA5NjAyODM0M30.ybGm52rGBCUd3KQTXJGwBFtXeFL_ac8_Grc8bR1wI2A';
        let supabaseClient = null;
        let realtimeChannel = null;

        function initSupabase() {
            try {
                if (window.supabase) {
                    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
                    console.log('✅ Supabase conectado');
                }
            } catch(e) { console.warn('Supabase no disponible:', e); }
        }

        // ========================================
        // ADMIN GATE — SHA-256
        // ========================================
        const ADMIN_HASH = '1d3712aef3744721a276e2e693b819a7abde8c2252f35f267ff2f315e18232bb';
        let pinBuffer = '';

        async function hashString(str) {
            const encoder = new TextEncoder();
            const data = encoder.encode(str);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2,'0')).join('');
        }

        function adminPinInput(digit) {
            if (pinBuffer.length >= 8) return;
            pinBuffer += digit;
            updatePinDots();
            if (pinBuffer.length === 8) setTimeout(adminPinSubmit, 200);
        }

        function adminPinClear() {
            if (pinBuffer.length === 0) return;
            pinBuffer = pinBuffer.slice(0, -1);
            updatePinDots();
        }

        function updatePinDots() {
            for (let i = 0; i < 8; i++) {
                const dot = document.getElementById('pd' + i);
                if (dot) dot.classList.toggle('filled', i < pinBuffer.length);
            }
        }

        async function adminPinSubmit() {
            if (!pinBuffer) return;
            const hash = await hashString(pinBuffer);
            if (hash === ADMIN_HASH) {
                unlockAdmin();
            } else {
                showAdminError('PIN incorrecto');
                const lockbox = document.getElementById('admin-numpad');
                if (lockbox) { lockbox.classList.add('lock-shake'); setTimeout(() => lockbox.classList.remove('lock-shake'), 500); }
                pinBuffer = '';
                updatePinDots();
            }
        }

        async function adminTextSubmit() {
            const input = document.getElementById('admin-text-input');
            if (!input || !input.value) return;
            const hash = await hashString(input.value.trim());
            if (hash === ADMIN_HASH) {
                unlockAdmin();
            } else {
                showAdminError('Contraseña incorrecta ❌');
                input.value = '';
                const box = input.parentElement;
                if (box) { box.classList.add('lock-shake'); setTimeout(() => box.classList.remove('lock-shake'), 500); }
            }
        }

        function showAdminError(msg) {
            const el = document.getElementById('admin-error-msg');
            if (el) { el.textContent = msg; setTimeout(() => { if (el) el.textContent = ''; }, 2500); }
        }

        function unlockAdmin() {
            sessionStorage.setItem('ablm_unlocked', '1');
            const ls = document.getElementById('admin-lockscreen');
            if (ls) {
                ls.classList.add('unlocking');
                setTimeout(() => { ls.style.display = 'none'; }, 500);
            }
            initSupabase();
            showToast('🔓 ¡Bienvenido Dengo!');
        }

        function checkAdminSession() {
            if (sessionStorage.getItem('ablm_unlocked') === '1') {
                const ls = document.getElementById('admin-lockscreen');
                if (ls) ls.style.display = 'none';
                initSupabase();
            }
        }

        // ========================================
        // LA ÚLTIMA CARTA — LÓGICA
        // ========================================
        function buildDeck() {
            const ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A'];
            const values = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14};
            const suits = ['♠','♥','♦','♣'];
            const deck = [];
            for (const suit of suits) {
                for (const rank of ranks) {
                    deck.push({ rank, suit, value: values[rank] });
                }
            }
            for (let i = deck.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [deck[i], deck[j]] = [deck[j], deck[i]];
            }
            return deck;
        }

        function initUltimaCartaLocal() {
            const players = (state.players || []).map(p => ({
                name: p.name || p,
                score: 0,
                turnsPlayed: 0
            }));
            if (players.length < 2) { showToast('⚠️ Mínimo 2 jugadores'); changeView('setup'); return; }

            state.ultimaCarta = {
                active: true,
                players,
                currentPlayerIndex: 0,
                deck: buildDeck(),
                deckIndex: 0,
                totalRounds: 3 * players.length,
                currentRound: 1,
                phase: 'cobarde',
                currentStep: 0,
                currentPoints: 0,
                currentDrinks: 0,
                drawnCards: [],
                revealed: false,
                lastGuessCorrect: false,
                revanchaCard: null,
                lastRevanchaCorrect: false,
            };
            saveState();
            changeView('ultimaCarta');
        }

        function ucDrawCard() {
            const uc = state.ultimaCarta;
            if (uc.deckIndex >= uc.deck.length) {
                uc.deck = buildDeck();
                uc.deckIndex = 0;
            }
            return uc.deck[uc.deckIndex++];
        }

        function ucCobarde() {
            showToast('🏳️ Cobarde — 1 trago');
            vibrate([50,50,100]);
            ucAdvancePlayer();
        }

        function ucStartEscalera() {
            const uc = state.ultimaCarta;
            uc.phase = 'escalera';
            uc.currentStep = 0;
            uc.currentPoints = 0;
            uc.currentDrinks = 0;
            uc.revealed = false;
            uc.drawnCards = [ucDrawCard(), ucDrawCard(), ucDrawCard(), ucDrawCard()];
            saveState();
            render();
        }

        function ucGuess(guess) {
            const uc = state.ultimaCarta;
            const card = uc.drawnCards[uc.currentStep];
            const step = uc.currentStep;
            let correct = false;

            if (step === 0) {
                const isPar = card.value % 2 === 0;
                correct = (guess === 'par' && isPar) || (guess === 'impar' && !isPar);
            } else if (step === 1) {
                const prev = uc.drawnCards[step - 1];
                correct = (guess === 'mayor' && card.value > prev.value) || (guess === 'menor' && card.value < prev.value);
                if (card.value === prev.value) correct = false;
            } else if (step === 2) {
                const isRed = ['♥','♦'].includes(card.suit);
                correct = (guess === 'rojo' && isRed) || (guess === 'negro' && !isRed);
            } else if (step === 3) {
                correct = guess === card.suit;
            }

            uc.revealed = true;
            uc.lastGuessCorrect = correct;

            if (correct) {
                uc.currentPoints += [1,2,3,4][step];
                if (uc.currentDrinks > 0) uc.currentDrinks = Math.max(0, uc.currentDrinks - 1);
                vibrate(100);
            } else {
                uc.currentDrinks++;
                vibrate([50,100]);
            }

            saveState();
            render();
        }

        function ucPlantarse() {
            ucFinalizarTurno(true);
        }

        function ucContinuar() {
            const uc = state.ultimaCarta;
            uc.currentStep++;
            uc.revealed = false;
            uc.lastGuessCorrect = false;
            saveState();
            render();
        }

        function ucAceptarDerrota() {
            ucFinalizarTurno(false);
        }

        function ucRevancha() {
            const uc = state.ultimaCarta;
            uc.phase = 'revancha';
            uc.revanchaCard = null;
            saveState();
            render();
        }

        function ucGuessRevancha(guess) {
            const uc = state.ultimaCarta;
            const card = ucDrawCard();
            uc.revanchaCard = card;
            const prevCard = uc.drawnCards[uc.currentStep];
            const correct = (guess === 'mayor' && card.value > prevCard.value) || (guess === 'menor' && card.value < prevCard.value);
            uc.lastRevanchaCorrect = correct;

            const prevPoints = [1,2,3,4][uc.currentStep - 1] || 1;

            if (correct) {
                uc.currentDrinks = Math.max(0, uc.currentDrinks - 1);
                uc.currentPoints += prevPoints;
                vibrate([100,50,100]);
            } else {
                uc.currentDrinks++;
                uc.currentPoints -= prevPoints;
                vibrate([200]);
            }

            saveState();
            render();
        }

        function ucFinalizarTurno(won) {
            const uc = state.ultimaCarta;
            const player = uc.players[uc.currentPlayerIndex];

            if (won && uc.currentPoints > 0) {
                player.score += uc.currentPoints;
            } else if (!won && uc.phase === 'revancha' && !uc.lastRevanchaCorrect) {
                if (uc.currentPoints < 0) player.score += uc.currentPoints;
            }

            player.turnsPlayed++;

            const allDone = uc.players.every(p => p.turnsPlayed >= 3);
            if (allDone) {
                uc.phase = 'final';
                vibrate([100,50,100,50,200]);
                saveState();
                render();
                return;
            }

            ucAdvancePlayer();
        }

        function ucAdvancePlayer() {
            const uc = state.ultimaCarta;
            let nextIdx = (uc.currentPlayerIndex + 1) % uc.players.length;
            let attempts = 0;
            while (uc.players[nextIdx].turnsPlayed >= 3 && attempts < uc.players.length) {
                nextIdx = (nextIdx + 1) % uc.players.length;
                attempts++;
            }
            uc.currentPlayerIndex = nextIdx;
            uc.currentRound++;
            uc.phase = 'cobarde';
            uc.currentStep = 0;
            uc.currentPoints = 0;
            uc.currentDrinks = 0;
            uc.drawnCards = [];
            uc.revealed = false;
            saveState();
            render();
        }

        // ========================================
        // SUPABASE ROOMS
        // ========================================
        function genRoomCode() {
            const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
            return Array.from({length:4}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
        }

        async function createRoom() {
            if (!supabaseClient) { showToast('⚠️ Sin conexión a Supabase'); return; }
            const nameInput = document.getElementById('host-name-input');
            const hostName = nameInput ? nameInput.value.trim() : '';
            if (!hostName) { showToast('✍️ Ingresá tu nombre'); return; }

            const code = genRoomCode();
            const gameState = { status: 'waiting', players: [{ name: hostName }] };

            try {
                const { error } = await supabaseClient.from('rooms').insert({
                    code,
                    game_state: gameState,
                    expires_at: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString()
                });
                if (error) { showToast('❌ Error: ' + error.message); return; }

                state.roomState = { code, isHost: true, hostName, players: [{ name: hostName }] };
                if (!state.players) state.players = [];
                state.players = [{ name: hostName }];
                saveState();
                subscribeToRoom(code);
                render();
            } catch(e) { showToast('❌ ' + e.message); }
        }

        async function joinRoom() {
            if (!supabaseClient) { showToast('⚠️ Sin conexión a Supabase'); return; }
            const codeInput = document.getElementById('room-code-input');
            const nameInput = document.getElementById('guest-name-input');
            const code = codeInput ? codeInput.value.trim().toUpperCase() : '';
            const guestName = nameInput ? nameInput.value.trim() : '';
            if (!code || code.length !== 4) { showToast('⚠️ Código de 4 letras'); return; }
            if (!guestName) { showToast('✍️ Ingresá tu nombre'); return; }

            try {
                const { data, error } = await supabaseClient.from('rooms').select('*').eq('code', code).single();
                if (error || !data) { showToast('❌ Sala no encontrada'); return; }

                const gs = data.game_state;
                if (gs.status !== 'waiting') { showToast('⚠️ La partida ya comenzó'); return; }

                const updatedPlayers = [...(gs.players || []), { name: guestName }];
                try {
                    const payload = { game_state: { ...gs, players: updatedPlayers } };
                    const res = await casUpdateRoom(code, payload);
                    if (res && res.error) console.warn('joinRoom update error', res.error);
                } catch(e) { console.warn('joinRoom supabase error', e); }

                state.roomState = { code, isHost: false, guestName, players: updatedPlayers };
                saveState();
                subscribeToRoom(code);
                render();
            } catch(e) { showToast('❌ ' + e.message); }
        }

        function subscribeToRoom(code) {
            if (!supabaseClient) return;
            if (realtimeChannel) realtimeChannel.unsubscribe();

            realtimeChannel = supabaseClient.channel('room:' + code)
                .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'rooms', filter: 'code=eq.' + code },
                payload => {
                    const gs = payload.new.game_state;
                    if (state.roomState && gs) {
                        state.roomState.players = gs.players;
                        if (gs.status === 'playing') {
                            state.ultimaCarta = gs.ultimaCarta;
                            state.view = 'ultimaCarta';
                        }
                        saveState();
                        render();
                    }
                }).subscribe();
        }

        async function startOnlineGame() {
            if (!supabaseClient || !state.roomState) return;
            const code = state.roomState.code;
            
            // Build initial UC state
            const players = state.roomState.players.map(p => ({
                name: p.name, score: 0, turnsPlayed: 0
            }));
            const uc = {
                active: true, players, currentPlayerIndex: 0,
                deck: buildDeck(), deckIndex: 0,
                totalRounds: 3 * players.length, currentRound: 1,
                phase: 'cobarde', currentStep: 0, currentPoints: 0, currentDrinks: 0,
                drawnCards: [], revealed: false, lastGuessCorrect: false,
                revanchaCard: null, lastRevanchaCorrect: false,
                isOnline: true
            };
            
            const gs = { status: 'playing', players: state.roomState.players, ultimaCarta: uc };
            try {
                const res = await casUpdateRoom(code, { game_state: gs });
                if (res && res.error) console.warn('startOnlineGame update error', res.error);
            } catch(e) { console.warn('startOnlineGame supabase error', e); }
        }

        function leaveRoom() {
            state.roomState = null;
            if (realtimeChannel) { realtimeChannel.unsubscribe(); realtimeChannel = null; }
            saveState();
            changeView('ultimaCarta');
        }
"""

idx_funcs = html.find('        function reiniciarRetoCadena() {')
if idx_funcs != -1:
    html = html[:idx_funcs] + FUNCTIONS_INJECT + '\n' + html[idx_funcs:]
    print("✅ Funciones insertadas")
else:
    print("❌ No se encontro lugar para funciones (reiniciarRetoCadena)")

# 7. INIT ADMIN EN LOAD
INIT_INJECT = """
            checkAdminSession();
"""
idx_init = html.find('            // Service Worker removido (sw.js eliminado)\\n        });')
if idx_init == -1:
    idx_init = html.find('            // Service Worker removido (sw.js eliminado)')
if idx_init != -1:
    html = html[:idx_init] + INIT_INJECT + html[idx_init:]
    print("✅ CheckAdmin insertado")

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ INICIAR.html guardado exitosamente!")
