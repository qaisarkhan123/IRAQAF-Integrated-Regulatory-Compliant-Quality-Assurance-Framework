#!/usr/bin/env python3
"""
Fix indentation after wrapping in guard condition.
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the "if 'latest' in globals()" line and indent everything until "else:"
in_guard = False
in_else = False
fixed_lines = []
indent_lines = []

for i, line in enumerate(lines):
    if "if 'latest' in globals() and latest is not None:" in line:
        in_guard = True
        fixed_lines.append(line)
        print(f"Found guard at line {i+1}")
    elif in_guard and line.strip().startswith('else:'):
        # Found the else, now indent all collected lines
        for indent_line in indent_lines:
            if indent_line.strip():  # Don't indent blank lines
                fixed_lines.append('    ' + indent_line)
            else:
                fixed_lines.append(indent_line)
        fixed_lines.append(line)
        in_guard = False
        in_else = True
        indent_lines = []
        print(f"Found else at line {i+1}")
    elif in_guard:
        # Collect lines to indent
        indent_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back
with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"✓ Fixed indentation. Indented {len(indent_lines)} lines")
