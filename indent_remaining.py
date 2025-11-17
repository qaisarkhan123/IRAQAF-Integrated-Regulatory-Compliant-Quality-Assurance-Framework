#!/usr/bin/env python3
"""
Indent all code from line 8440 onwards by 4 spaces to move it inside the if block.
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 0-8438 stay as-is (they're before/inside the section we're fixing)
# Lines 8439 onwards get indented

result_lines = lines[:8439]  # Lines 1-8439 (0-indexed: 0-8438)

# Indent lines 8440 onwards
for i in range(8439, len(lines)):
    line = lines[i]
    if line.strip():  # Non-empty line
        result_lines.append('    ' + line)
    else:
        result_lines.append(line)

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(result_lines)

print(f"✓ Indented lines 8440-{len(lines)} by 4 spaces")
print(f"  File has {len(result_lines)} lines (was {len(lines)})")
