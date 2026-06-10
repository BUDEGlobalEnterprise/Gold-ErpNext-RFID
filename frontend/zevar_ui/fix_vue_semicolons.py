import os
import re

directory = '/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/'

pattern = re.compile(r'(@click="\n(?:(?:\s+)[^"\n]+\n)+?)(?:\s+)"', re.MULTILINE)

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    def replacer(match):
        block = match.group(0)
        lines = block.split('\n')
        for i in range(1, len(lines) - 1):
            if lines[i].strip() and not lines[i].rstrip().endswith(';'):
                lines[i] = lines[i].rstrip() + ';'
        return '\n'.join(lines)
    
    new_content = pattern.sub(replacer, content)
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.vue'):
            fix_file(os.path.join(root, file))
