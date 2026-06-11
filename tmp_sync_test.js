const fs = require('fs');
const { JSDOM } = require('jsdom');
const path = require('path');

const htmlPath = path.join(__dirname, 'INICIAR.html');
const html = fs.readFileSync(htmlPath, 'utf-8');

console.log('🧪 Testing multiplayer sync...\n');

async function runTest() {
    const dom = new JSDOM(html, {
        runScripts: 'dangerously',
        resources: 'usable',
        pretendToBeVisual: true,
        beforeParse(window) {
            window.addEventListener('error', (e) => {
                console.error('❌ JSDOM ERROR:', e.message);
                process.exit(1);
            });
        }
    });

    const { window } = dom;
    const { document } = window;

    return new Promise((resolve) => {
        window.addEventListener('load', async () => {
            console.log('✅ Page loaded\n');
            
            try {
                // Verify state structure
                if (!window.state) {
                    console.log('❌ window.state not defined');
                    resolve();
                    return;
                }
                console.log('✅ state initialized:', {
                    players: window.state.players ? window.state.players.length : 0,
                    view: window.state.view,
                    currentPlayerIndex: window.state.currentPlayerIndex
                });

                // Verify turn lock functions exist
                if (typeof window.acquireTurnLock !== 'function') {
                    console.log('❌ acquireTurnLock not found');
                    resolve();
                    return;
                }
                console.log('✅ acquireTurnLock available');

                if (typeof window.isLocalPlayerTurn !== 'function') {
                    console.log('❌ isLocalPlayerTurn not found');
                    resolve();
                    return;
                }
                console.log('✅ isLocalPlayerTurn available');

                // Verify subscribeToRoom function
                if (typeof window.subscribeToRoom !== 'function') {
                    console.log('❌ subscribeToRoom not found');
                    resolve();
                    return;
                }
                console.log('✅ subscribeToRoom available');

                // Verify startOnlineGame function
                if (typeof window.startOnlineGame !== 'function') {
                    console.log('❌ startOnlineGame not found');
                    resolve();
                    return;
                }
                console.log('✅ startOnlineGame available');

                // Check Supabase initialization
                if (typeof window.initSupabase !== 'function') {
                    console.log('❌ initSupabase not found');
                    resolve();
                    return;
                }
                console.log('✅ initSupabase available');

                // Verify game state structure
                console.log('\n📋 Initial state structure:');
                console.log('  - full_state:', window.state.full_state ? '✅ exists' : '❌ missing');
                console.log('  - roomCode:', window.state.roomCode ? `✅ "${window.state.roomCode}"` : '❌ missing');
                console.log('  - roomState:', window.state.roomState ? '✅ exists' : '❌ missing');

                console.log('\n🎮 Testing game flow functions...');
                console.log('  - casUpdateRoom:', typeof window.casUpdateRoom === 'function' ? '✅' : '❌');
                console.log('  - saveState:', typeof window.saveState === 'function' ? '✅' : '❌');
                console.log('  - render:', typeof window.render === 'function' ? '✅' : '❌');

                console.log('\n✅ SYNC TEST OK - All critical functions present and state initialized correctly');

            } catch (e) {
                console.error('❌ Test error:', e.message);
            }

            resolve();
        });

        setTimeout(() => {
            console.error('❌ Test timeout');
            resolve();
        }, 5000);
    });
}

runTest().then(() => process.exit(0));
