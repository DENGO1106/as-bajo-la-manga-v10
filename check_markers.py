import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', encoding='utf-8') as f:
    html = f.read()

print('Buscando puntos de insercion...')

tag_tailwind = '<script src="https://cdn.tailwindcss.com"></script>'
tag_css_end = '        /* Prevent pull-to-refresh'
tag_body = '<body class="min-h-screen flex flex-col">'
tag_biblioteca = '                    <!-- Biblioteca -->'
tag_retocadena_view = 'retoCadena: () => {'
tag_views_close = '        };\n\n        // Initialize'
tag_reiniciar = '        function reiniciarRetoCadena()'
tag_domloaded = '            // Service Worker removido (sw.js eliminado)\n        });'
tag_trash = '            trash: { toxic: [], poker: [], sinexcusas: [], quienEsMas: [], bomba: [], cadena: [] }'
tag_render_title = "            const title = state.view === 'sinexcusas' ? 'SIN EXCUSAS' : String(state.view).toUpperCase().replace('_', ' ');"

markers = {
    'tailwind': html.find(tag_tailwind),
    'css_end': html.find(tag_css_end),
    'body': html.find(tag_body),
    'biblioteca': html.find(tag_biblioteca),
    'retocadena_view': html.rfind(tag_retocadena_view),
    'views_close': html.find(tag_views_close, html.rfind(tag_retocadena_view)),
    'reiniciar': html.find(tag_reiniciar),
    'domloaded': html.find(tag_domloaded),
    'trash': html.find(tag_trash),
    'render_title': html.find(tag_render_title),
}

for k, v in markers.items():
    status = 'OK' if v != -1 else 'NOT FOUND'
    print(f'  {k}: {v} [{status}]')
