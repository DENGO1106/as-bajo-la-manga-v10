import re
import json

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update SIN_EXCUSAS_CARDS
with open('osc_cartas_digitales.json', 'r', encoding='utf-8') as f:
    osc_cards = json.load(f)

# Format to JS array string
cards_js = "const SIN_EXCUSAS_CARDS = " + json.dumps(osc_cards, ensure_ascii=False, indent=4) + ";"
html = re.sub(r'const SIN_EXCUSAS_CARDS = \[.*?\];', cards_js, html, flags=re.DOTALL)

# 2. Fix sinexcusas view
sinexcusas_view = """            sinexcusas: () => {
                const CAT_META = {
                    'TODAS':          { icon: '🎲', desc: 'Todas las cartas' },
                    'bala_perdida':   { icon: '🎯', desc: 'Ataque directo' },
                    'juego':          { icon: '🎮', desc: 'Todos participan' },
                    'bendicion':      { icon: '✨', desc: 'Tu momento de suerte' },
                    'mision_oculta':  { icon: '🕵️', desc: 'Misión secreta' },
                    'la_ley':         { icon: '⚖️', desc: 'La ley es la ley' },
                    'desafio':        { icon: '🔥', desc: 'Cumple o bebe' },
                    'maldicion':      { icon: '💀', desc: 'Te llegó la maldición' },
                    'corona':         { icon: '👑', desc: 'El poder absoluto' }
                };
                const CAT_DISPLAY = {
                    'TODAS': 'TODAS',
                    'bala_perdida': 'BALA PERDIDA',
                    'juego': 'JUEGO',
                    'bendicion': 'BENDICIÓN',
                    'mision_oculta': 'MISIÓN OCULTA',
                    'la_ley': 'LA LEY',
                    'desafio': 'DESAFÍO',
                    'maldicion': 'MALDICIÓN',
                    'corona': 'LA CORONA DEL REY'
                };
                const allCats = ['TODAS', ...new Set(SIN_EXCUSAS_CARDS.map(c => c.cat))];
                const cardCount = state.sinexcusas.category.includes('TODAS')
                    ? SIN_EXCUSAS_CARDS.filter(c => !state.trash.sinexcusas.includes(String(c.id))).length
                    : SIN_EXCUSAS_CARDS.filter(c => state.sinexcusas.category.includes(c.cat) && !state.trash.sinexcusas.includes(String(c.id))).length;

                if (state.sinexcusas.index === -1) {
                    return `
                        <div class="space-y-6 animate-fade-in pb-8 pt-4">
                            <!-- Header -->
                            <div class="text-center space-y-2">
                                <div class="bg-cyan-500/10 w-20 h-20 rounded-full flex items-center justify-center border border-cyan-500/30 mx-auto">
                                    <span class="text-4xl">🍻</span>
                                </div>
                                <h2 class="text-3xl font-extrabold text-cyan-400">SIN EXCUSAS</h2>
                                <p class="text-slate-400 text-sm">Elegí las categorías que quieras jugar</p>
                            </div>

                            <!-- Contador dinámico -->
                            <div class="glass rounded-2xl px-6 py-3 flex items-center justify-center gap-3 border border-cyan-500/20">
                                <span class="text-cyan-400 text-2xl font-black">${cardCount}</span>
                                <span class="text-slate-400 text-sm font-bold uppercase tracking-wider">cartas disponibles</span>
                            </div>

                            <!-- Chips de categoría -->
                            <div class="space-y-3">
                                <p class="text-xs text-cyan-400 font-bold uppercase tracking-widest text-center">Categorías</p>
                                <div class="flex flex-col gap-3">
                                    ${allCats.map(cat => {
                                        const isActive = state.sinexcusas.category.includes(cat);
                                        const meta = CAT_META[cat] || { icon: '🎴', desc: '' };
                                        const displayName = CAT_DISPLAY[cat] || cat.toUpperCase().replace('_',' ');
                                        const count = cat === 'TODAS'
                                            ? SIN_EXCUSAS_CARDS.filter(c => !state.trash.sinexcusas.includes(String(c.id))).length
                                            : SIN_EXCUSAS_CARDS.filter(c => c.cat === cat && !state.trash.sinexcusas.includes(String(c.id))).length;
                                        return `
                                        <button onclick="toggleSinExcusasCategory('${cat.replace(/'/g, "\\\\'")}')"
                                                class="w-full flex items-center gap-4 p-4 rounded-2xl border transition-all touch-feedback ripple
                                                       ${isActive
                                                           ? 'bg-cyan-500/20 border-cyan-400/60 shadow-lg shadow-cyan-500/10'
                                                           : 'glass border-white/5 hover:border-cyan-500/30'}">
                                            <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 text-2xl
                                                        ${isActive ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'}">
                                                ${meta.icon}
                                            </div>
                                            <div class="flex-1 text-left">
                                                <p class="font-black text-sm uppercase tracking-wide ${isActive ? 'text-cyan-300' : 'text-slate-300'}">${displayName}</p>
                                                <p class="text-xs text-slate-500 mt-0.5">${meta.desc}</p>
                                            </div>
                                            <div class="flex-shrink-0 flex flex-col items-end gap-1">
                                                <span class="text-xs font-bold ${isActive ? 'text-cyan-400' : 'text-slate-600'}">${count} cartas</span>
                                                <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0
                                                            ${isActive ? 'border-cyan-400 bg-cyan-400' : 'border-slate-600 bg-transparent'}">
                                                    ${isActive ? '<span class="text-slate-950 text-xs font-black">✓</span>' : ''}
                                                </div>
                                            </div>
                                        </button>
                                    `}).join('')}
                                </div>
                            </div>

                            <!-- Botón empezar -->
                            <button onclick="startSinExcusas()"
                                    class="w-full bg-cyan-600 text-white font-black py-5 rounded-2xl text-lg uppercase shadow-lg shadow-cyan-500/20 ripple touch-feedback ${cardCount === 0 ? 'opacity-40 pointer-events-none' : ''}">
                                🍻 EMPEZAR (${cardCount} cartas)
                            </button>
                            <button onclick="changeView('menu')" class="w-full glass p-4 rounded-2xl font-bold text-slate-400 touch-feedback">
                                ← Volver al Menú
                            </button>
                        </div>
                    `;
                }

                const card = state.sinexcusas.deck[state.sinexcusas.index];
                const currentPlayer = state.players[state.currentPlayerIndex];

                return `
                <div class="space-y-8 animate-fade-in flex flex-col items-center">
                    <div class="w-full text-center space-y-1">
                        <span class="text-xs text-cyan-400 font-bold uppercase tracking-[0.3em]">Turno de</span>
                        <h2 class="text-2xl font-black text-white uppercase">${currentPlayer?.name || currentPlayer}</h2>
                    </div>

                    <div class="w-full rounded-[2.5rem] p-8 min-h-[420px] flex flex-col items-center justify-center card-shadow ${state.sinexcusas.animationClass || 'card-enter'} relative overflow-hidden"
                         style="background: linear-gradient(135deg, ${card.color}22 0%, #0f172a 60%); border: 2px solid ${card.color}66;">
                        <div class="absolute -top-8 -right-8 text-[100px] opacity-5 pointer-events-none">🃏</div>

                        <!-- Categoría badge -->
                        <div class="text-[10px] font-black tracking-[0.3em] px-5 py-2 rounded-full uppercase mb-6 border"
                             style="color:${card.color}; border-color:${card.color}44; background:${card.color}15;">
                            ${card.title}
                        </div>

                        <!-- Texto principal -->
                        <div class="flex-grow flex items-center justify-center text-center w-full px-2">
                            <p class="text-white text-xl font-bold leading-relaxed ${card.textSize || 'text-lg'}">${card.body}</p>
                        </div>
                    </div>

                    <div class="flex w-full gap-4">
                        <button onclick="resetSinExcusasDeck(); vibrate(100); showToast('¡Mazo mezclado!');" class="flex-1 glass p-4 rounded-2xl btn-hover text-slate-400 font-bold uppercase tracking-wider text-xs ripple touch-feedback">Mezclar</button>
                        <button onclick="drawSinExcusasCard()" class="flex-[2] text-white p-4 rounded-2xl font-black btn-hover text-lg uppercase tracking-tight shadow-lg ripple touch-feedback" style="background:${card.color}; box-shadow: 0 10px 30px ${card.color}44;">Siguiente</button>
                    </div>
                </div>
                `;
            },"""

html = re.sub(r'sinexcusas: \(\) => \{.*?\},(\s+)(sabio:|retoCadena:)', sinexcusas_view + r'\1\2', html, flags=re.DOTALL)


# 3. Add player logic to Poker
poker_old = """                const card = state.pokerDeck[state.pokerIndex];
                const isRed = ['♥️', '♦️'].includes(card.suit);

                return `
                <div class="space-y-8 animate-fade-in flex flex-col items-center">
                    <div class="w-full glass rounded-[2.5rem] p-8 min-h-[400px] flex flex-col items-center justify-between card-shadow card-enter relative overflow-hidden border-red-500/30">"""

poker_new = """                const card = state.pokerDeck[state.pokerIndex];
                const isRed = ['♥️', '♦️'].includes(card.suit);
                const currentPlayer = state.players[state.currentPlayerIndex];

                return `
                <div class="space-y-8 animate-fade-in flex flex-col items-center">
                    <div class="w-full text-center space-y-1">
                        <span class="text-xs text-red-400 font-bold uppercase tracking-[0.3em]">Turno de</span>
                        <h2 class="text-2xl font-black text-white uppercase">${currentPlayer?.name || currentPlayer}</h2>
                    </div>

                    <div class="w-full glass rounded-[2.5rem] p-8 min-h-[400px] flex flex-col items-center justify-between card-shadow card-enter relative overflow-hidden border-red-500/30">"""

html = html.replace(poker_old, poker_new)

poker_draw_old = """        function drawPokerCard() {
            state.pokerIndex++;
            if (state.pokerIndex >= state.pokerDeck.length || state.pokerIndex === -1) {
                state.pokerDeck = shuffleArray([...POKER_CARDS]);
                state.pokerIndex = 0;
                showToast('🔄 Se barajó el mazo nuevamente');
            }
            saveState();
            render();
        }"""

poker_draw_new = """        function drawPokerCard() {
            state.pokerIndex++;
            if (state.pokerIndex >= state.pokerDeck.length || state.pokerIndex === -1) {
                state.pokerDeck = shuffleArray([...POKER_CARDS]);
                state.pokerIndex = 0;
                showToast('🔄 Se barajó el mazo nuevamente');
            }
            state.currentPlayerIndex = (state.currentPlayerIndex + 1) % state.players.length;
            saveState();
            render();
        }"""

html = html.replace(poker_draw_old, poker_draw_new)

# 4. Re-enable players
html = html.replace("// if (state.players.length < 2) state.view = 'setup';", "if (!state.players || state.players.length < 2) state.view = 'setup';")
html = html.replace("<!-- Jugadores desactivados temporalmente -->", """<!-- Jugadores activos -->
                    <button onclick="changeView('setup')" class="w-full glass p-4 rounded-2xl flex items-center gap-4 border-white/10 btn-hover ripple touch-feedback">
                        <div class="flex gap-1">
                            ${(state.players || []).slice(0,5).map((_,i) => `<span class="text-xl">${['🔵','🟢','🟡','🔴','🟣','🟠'][i % 6]}</span>`).join('')}
                            ${(state.players || []).length > 5 ? `<span class="text-xs text-slate-400 self-center">+${state.players.length - 5}</span>` : ''}
                        </div>
                        <div class="text-left flex-1">
                            <p class="text-xs text-slate-500 uppercase tracking-widest font-bold">Jugadores</p>
                            <p class="text-sm font-bold text-white">${(state.players || []).map(p => p.name || p).join(', ') || 'Agregar jugadores'}</p>
                        </div>
                        <span class="text-slate-500 text-sm">✏️</span>
                    </button>""")

# 5. Move Sabio to group games
sabio_btn = """                    <button onclick="changeView('sabio')" class="w-full glass p-6 rounded-3xl flex items-center gap-4 btn-hover card-shadow group border-blue-500/20 ripple touch-feedback">
                        <div class="bg-blue-500/20 p-4 rounded-2xl group-hover:bg-blue-500/30 transition-colors">
                            <span class="text-2xl">🧙‍♂️</span>
                        </div>
                        <div class="text-left">
                            <h2 class="text-lg font-bold text-blue-400">EL SABIO DEL GUARO</h2>
                            <p class="text-slate-400 text-sm">Adivina la siguiente carta</p>
                        </div>
                    </button>"""

html = html.replace(sabio_btn, "")
grupo_header = """<!-- Juegos de Grupo Nuevos -->
                    <div class="text-sm uppercase tracking-widest text-slate-500 font-bold px-2 mt-8">👥 Juegos de Grupo</div>"""
html = html.replace(grupo_header, grupo_header + "\n\n" + sabio_btn)


# 6. Delete OSECAGA
html = re.sub(r'osecaga:\s*\{.*?\},', '', html, flags=re.DOTALL)
html = re.sub(r'drawOSeCagaCard\(\)\s*\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'mostrarInstruccionesOSeCaga\(\)\s*\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'resetOSeCagaDeck\(\)\s*\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'startOSeCaga\(\)\s*\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\{ id: \'osecaga\', label: \'💩 O SE CAGA\' \},', '', html)
html = re.sub(r'\} else if \(state\.view === \'osecaga\'.*?drawOSeCagaCard\(\);', '', html, flags=re.DOTALL)
html = re.sub(r'const OSECAGA_DATA = \{.*?\};', '', html, flags=re.DOTALL)
html = re.sub(r'const OSECAGA_ALL_CARDS = \[.*?\];', '', html, flags=re.DOTALL)

# Delete library tab logic without breaking syntax
html = re.sub(r'else if \(state\.libTab === \'osecaga\'\) items = OSECAGA_ALL_CARDS.*?obj: \{ id: c \} \}\)\);', '', html, flags=re.DOTALL)

# Delete Osecaga view
html = re.sub(r'osecaga: \(\) => \{.*?(?=quienEsMas: \(\) => \{)', '', html, flags=re.DOTALL)

# Cleanup any trailing commas in state
html = re.sub(r',\s*}', '}', html)

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
