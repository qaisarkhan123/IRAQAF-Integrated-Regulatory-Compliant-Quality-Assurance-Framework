#!/usr/bin/env python3
"""
Indent lines 7398-7667 by 4 spaces to place them inside the if latest block.
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines to indent: 7398 to 7667 (0-indexed: 7397 to 7666)
# indent all non-empty lines in this range
start_line = 7397
end_line = 7667

for i in range(start_line, min(end_line, len(lines))):
    if lines[i].strip():  # If line is not blank
        if not lines[i].startswith('    '):  # If not already indented
            lines[i] = '    ' + lines[i]

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'Indented lines {start_line+1} to {min(end_line, len(lines))}')
