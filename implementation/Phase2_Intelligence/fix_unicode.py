import re

# Read the test file
with open('test_phase2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode symbols with ASCII equivalents
replacements = {
    '🚀': '>>',
    '📝': '[*]',
    '📊': '[*]',
    '🎯': '[*]',
    '🎤': '[*]',
    '🌍': '[*]',
    '🔗': '[->]',
    '✅': '[+]',
    '❌': '[-]',
    '⚠️': '[!]',
    '📋': '[=]',
    '🔥': '[!]',
    '⭐': '[*]',
    '🎉': '[!]'
}

for unicode_char, ascii_replacement in replacements.items():
    content = content.replace(unicode_char, ascii_replacement)

# Write back to file
with open('test_phase2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Unicode symbols replaced successfully!")