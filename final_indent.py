#!/usr/bin/env python3
"""Indent lines 7680-end by 4 spaces to be inside the if block."""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 0-7679 stay as-is, lines 7680+ get indented
result_lines = lines[:7680]

for i in range(7680, len(lines)):
    line = lines[i]
    if line.strip():  # Non-empty line
        result_lines.append('    ' + line)
    else:
        result_lines.append(line)

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(result_lines)

print(f"✓ Indented lines 7680-{len(lines)} (total {len(result_lines)} lines)")
