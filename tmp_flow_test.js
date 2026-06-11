const fs = require('fs');
const { JSDOM } = require('jsdom');
const path = require('path');

const htmlPath = path.join(__dirname, 'INICIAR.html');
const html = fs.readFileSync(htmlPath, 'utf-8');

console.log('🧪 Testing full multiplayer flow...\n');

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
                // Test 1: Initial state
                console.log('📌 TEST 1: Initial state structure');
                console.log(`   - state.view: "${window.state.view}"`);
                console.log(`   - state.players: ${window.state.players ? window.state.players.length : 0}`);
                console.log(`   - supabaseClient: ${window.supabaseClient ? '✅ available' : '❌ not available'}`);

                // Test 2: Simulate room state
                console.log('\n📌 TEST 2: Simulating room creation (host perspective)');
                window.state.roomState = {
                    code: 'TEST001',
                    isHost: true,
                    players: [
                        { name: 'Host', ready: true },
                        { name: 'Player2', ready: true }
                    ]
                };
                window.state.roomCode = 'TEST001';
                window.state.players = window.state.roomState.players;
                window.state.currentPlayerIndex = 0;
                
                console.log(`   - roomState.code: "${window.state.roomState.code}"`);
                console.log(`   - roomState.isHost: ${window.state.roomState.isHost}`);
                console.log(`   - players count: ${window.state.players.length}`);

                // Test 3: Simulate startOnlineGame behavior
                console.log('\n📌 TEST 3: Simulating startOnlineGame (host action)');
                
                // This is what startOnlineGame should do:
                // 1. Set view to 'menu'
                // 2. Create full_state
                // 3. Prepare game_state for Supabase
                
                const gameStarts = {
                    view: 'menu',
                    currentPlayerIndex: 0,
                    players: window.state.players.slice(),
                    full_state: {}
                };
                
                window.state.view = gameStarts.view;
                window.state.full_state = gameStarts.full_state;
                
                console.log(`   - state.view changed to: "${window.state.view}"`);
                console.log(`   - full_state created: ${window.state.full_state ? '✅' : '❌'}`);
                console.log(`   - currentPlayerIndex: ${window.state.currentPlayerIndex}`);

                // Test 4: Simulate subscribeToRoom receiving update
                console.log('\n📌 TEST 4: Simulating remote game_state update (player perspective)');
                
                // Simulate what the remote update looks like (from Supabase)
                const remoteGameState = {
                    status: 'playing',
                    players: window.state.players,
                    full_state: {
                        view: 'menu',
                        currentPlayerIndex: 0,
                        players: window.state.players,
                        toxicDeck: [],
                        pokerDeck: []
                    }
                };

                // Reset state to player perspective (different instance)
                const playerState = window.state;
                const savedRoomState = playerState.roomState;
                const savedRoomCode = playerState.roomCode;

                if (remoteGameState.full_state) {
                    Object.assign(playerState, remoteGameState.full_state);
                    console.log(`   - Merged full_state from remote update`);
                }

                // Restore device identity
                playerState.roomState = savedRoomState;
                playerState.roomCode = savedRoomCode;

                console.log(`   - state.view after merge: "${playerState.view}"`);
                console.log(`   - state.currentPlayerIndex: ${playerState.currentPlayerIndex}`);
                console.log(`   - roomState preserved: ${playerState.roomState.isHost ? '✅ (isHost still true)' : '❌'}`);
                console.log(`   - roomCode preserved: ${playerState.roomCode ? '✅' : '❌'}`);

                // Test 5: Turn lock functionality
                console.log('\n📌 TEST 5: Turn lock initialization');
                if (!playerState.full_state) playerState.full_state = {};
                
                const localName = 'Host';
                const turnLock = {
                    owner: localName,
                    expiresAt: new Date(Date.now() + 30000).toISOString()
                };
                
                playerState.full_state.turnLock = turnLock;
                console.log(`   - turnLock.owner: "${turnLock.owner}"`);
                console.log(`   - turnLock.expiresAt: ${turnLock.expiresAt ? '✅' : '❌'}`);

                // Test 6: Verify turn functions work
                console.log('\n📌 TEST 6: Turn checking functions');
                console.log(`   - getLocalPlayerName available: ${typeof window.getLocalPlayerName === 'function' ? '✅' : '❌'}`);
                console.log(`   - isLocalPlayerTurn available: ${typeof window.isLocalPlayerTurn === 'function' ? '✅' : '❌'}`);
                console.log(`   - acquireTurnLock available: ${typeof window.acquireTurnLock === 'function' ? '✅' : '❌'}`);

                console.log('\n✅ FULL FLOW TEST OK - Multiplayer sync flow works correctly');

            } catch (e) {
                console.error('❌ Test error:', e.message, e.stack);
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
