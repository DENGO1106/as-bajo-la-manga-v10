import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

# REMOVE SABIO FUNCTIONS
html = re.sub(r'        function initSabio\(\) \{.*?(?=        function filterLib\(\) \{)', '', html, flags=re.DOTALL)

# REMOVE SABIO VIEWS
html = re.sub(r'            sabio: \(\) => `.*?            \`,(?=\n\n            quienEsMas:)', '', html, flags=re.DOTALL)
html = re.sub(r'            sabioQuestion: \(\) => \{.*?(?=            bomba: \(\) => `)', '', html, flags=re.DOTALL)

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ INICIAR.html modificado: eliminadas funciones y vistas del Sabio")
