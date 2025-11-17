#!/usr/bin/env python3
"""
Fix indentation - ensure all lines from 7398-7667 have proper indentation inside the if block.
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines to indent: 7398 to 7667 (0-indexed: 7397 to 7666)
# Need to add 4 spaces to every line that needs indenting
start_line = 7397
end_line = 7667

for i in range(start_line, min(end_line + 1, len(lines))):
    line = lines[i]
    if line.strip():  # If line is not blank
        # Add 4 spaces to the beginning
        lines[i] = '    ' + line

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(
    f'Added 4 spaces to lines {start_line+1} to {min(end_line+1, len(lines))}')
