import re

def analyze_script_syntax():
    with open('INICIAR.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
    if not scripts:
        print("No script tags found")
        return
        
    js = scripts[0]
    
    depth = 0
    in_string = False
    string_char = None
    in_template = False
    escape = False
    
    last_unclosed_line = None
    
    lines = js.split('\n')
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if escape:
                escape = False
                continue
                
            if char == '\\':
                escape = True
                continue
                
            if in_string:
                if char == string_char:
                    in_string = False
                continue
                
            if in_template:
                if char == '`':
                    in_template = False
                elif char == '$' and j + 1 < len(line) and line[j+1] == '{':
                    pass
                continue
                
            if char in ["'", '"']:
                in_string = True
                string_char = char
            elif char == '`':
                in_template = True
                last_unclosed_line = i + 1
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                
    print(f"Final depth: {depth}")
    print(f"In template: {in_template}")
    print(f"Last unclosed template at script line: {last_unclosed_line}")
    if in_template:
        print(f"Line content: {lines[last_unclosed_line-1]}")

analyze_script_syntax()
