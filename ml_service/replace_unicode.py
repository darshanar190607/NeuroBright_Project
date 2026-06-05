import os

replacements = {
    '[OK]': '[OK]',
    '[FAIL]': '[FAIL]',
    '[NeuroBright]': '[NeuroBright]',
    '': '',
    '->': '->',
    'x': 'x'
}

r_count = 0
for root, dirs, files in os.walk('d:/Practice Projects/Neuroaptive_ML_EEG/ml_service'):
    for file in files:
        if file.endswith('.py') or file.endswith('.md'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            original_content = content
            for k, v in replacements.items():
                content = content.replace(k, v)
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Updated {filepath}')
                r_count += 1

print(f'Updated {r_count} files.')
