import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

with open('INICIAR.html', encoding='utf-8') as f:
    html = f.read()

# Buscar cierre del objeto views (despues de retoCadena)
rc = html.rfind('retoCadena: () => {')
print('--- Context 2000-2600 chars after retoCadena ---')
chunk = html[rc+2000:rc+2600]
for i, line in enumerate(chunk.split('\n')):
    print(f'{i:3}: {repr(line)}')

print()
print('--- All trash: occurrences ---')
idx = html.find('trash:')
while idx != -1:
    print(f'  pos={idx}: {repr(html[idx:idx+80])}')
    idx = html.find('trash:', idx+1)
