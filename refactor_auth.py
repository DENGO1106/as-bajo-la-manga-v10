import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 6. AUTH BUTTON IN MENU HEADER
AUTH_BTN = """
                    <!-- Auth Button -->
                    <button onclick="changeView('auth')" class="absolute top-4 right-4 glass p-2 rounded-xl text-xl touch-feedback border z-50 ${state.user ? 'border-emerald-500/40 text-emerald-400' : 'border-amber-500/20 text-amber-400'}">
                        ${state.user ? '🔓' : '🔐'}
                    </button>
"""
idx_menu_header = html.find('            menu: () => `\\n                <div class="space-y-4 animate-fade-in py-4">')
if idx_menu_header != -1:
    idx_menu_header += len('            menu: () => `\\n                <div class="space-y-4 animate-fade-in py-4">\\n')
    html = html[:idx_menu_header] + AUTH_BTN + html[idx_menu_header:]
else:
    # Try alternate spacing
    idx_menu_header = html.find('            menu: () => `\n                <div class="space-y-4 animate-fade-in py-4">')
    if idx_menu_header != -1:
        idx_menu_header += len('            menu: () => `\n                <div class="space-y-4 animate-fade-in py-4">\n')
        html = html[:idx_menu_header] + AUTH_BTN + html[idx_menu_header:]
    else:
        print("❌ No se encontro header menu")

# REMOVE EL SABIO DEL GUARO BUTTON
html = re.sub(r'\s*<button onclick="changeView\(\'sabio\'\).*?EL SABIO DEL GUARO.*?</button>', '', html, flags=re.DOTALL)

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ INICIAR.html modificado con Auth Button y eliminado Sabio button")
