import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('INICIAR.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('\\${', '${')
html = html.replace('\\`', '`')

with open('INICIAR.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Fixed backslash escaping')
