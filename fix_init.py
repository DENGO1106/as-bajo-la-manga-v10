import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix: restore the working render() call + fix init at the bottom
# Current broken bottom (in second <script>):
old_bottom = """        // Initialize Supabase now that consts are defined
        initSupabase();
        // checkSession is async - it will call render() when done
        checkSession().then(() => {
            render();
            if (state.roomCode) {
                conectarSala(state.roomCode);
            }
        });"""

new_bottom = """        // Initialize Supabase now that consts are defined
        initSupabase();
        checkSession();
        if (state.roomCode) {
            conectarSala(state.roomCode);
        }"""

html = html.replace(old_bottom, new_bottom)

# 2. Restore the initial render() call in first script (currently commented out)
old_comment = "        // render() is called after checkSession() resolves (bottom of script)"
new_render = "        // Initial render\n        render();"
html = html.replace(old_comment, new_render)

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ Inicialización restaurada al patrón que funcionaba")
