import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('Initial render',        '// Initial render\n        render();'),
    ('welcome view',          "welcome: () => `"),
    ('onlineRoom view',       "onlineRoom: () => `"),
    ('crearSala',             'async function crearSala()'),
    ('saveState isRemote',    'function saveState(isRemote = false)'),
    ('ROOM_INACTIVITY_MS',    'const ROOM_INACTIVITY_MS'),
    ('checkSession+roomCode', 'checkSession();\n        if (state.roomCode)'),
    ('profile view',          "profile: () => `"),
    ('auth view',             "auth: () => `"),
    ('Supabase script tag',   'supabase-js@2'),
]

ok = True
for name, marker in checks:
    found = marker in html
    status = 'OK    ' if found else 'FALTA '
    print(status + name)
    if not found:
        ok = False

print()
print('RESULTADO: ' + ('TODO LISTO - se puede pushear' if ok else 'HAY ERRORES - revisar'))
