#!/usr/bin/env python3
"""
Fix module-level code execution issues in app.py by:
1. Moving all code after the else clause (line 7670) inside the if latest block
2. Properly indenting all lines to maintain proper structure
"""

import re

# Read the file
with open('dashboard/app.py', 'r') as f:
    lines = f.readlines()

# Find the else clause
else_line_idx = None
for i, line in enumerate(lines):
    if i >= 7667 and 'else:' in line and '# If \'latest\' data is not available' in lines[i+1]:
        else_line_idx = i
        break

if else_line_idx is None:
    print("❌ Could not find the else clause at expected location")
    exit(1)

print(f"Found else clause at line {else_line_idx + 1}")

# The placeholder st.info line should be indented
placeholder_idx = else_line_idx + 2  # The st.info line

# Everything after placeholder should be unindented (at module level)
# We need to:
# 1. Keep the if/else structure as is
# 2. Move everything after else back inside the if block
# 3. Ensure proper indentation

# Read the structure more carefully
new_lines = []

# Lines 1-7667 (before the guard): keep as is but need to check
new_lines = lines[:else_line_idx]

# Replace the else block to be: if latest is not None: [all remaining code]
# Actually, we need to re-architect this...

# The real issue: lines after the else clause need to be part of the if/else structure
# Let's find where the if latest is not None: block starts

if_block_start = None
for i in range(else_line_idx - 1, 0, -1):
    if 'if latest is not None:' in lines[i]:
        if_block_start = i
        break

if if_block_start is None:
    print("❌ Could not find 'if latest is not None:' statement")
    exit(1)

print(f"Found 'if latest is not None:' at line {if_block_start + 1}")

# Strategy: move all code from line 7671 onwards inside the if block
# This means:
# 1. Keep lines up to and including the st.info line
# 2. Indent everything after st.info by 4 spaces to be inside the if block
# 3. Remove the current else clause indentation (undo the st.info indent)

result_lines = lines[:if_block_start]  # Keep everything before the if

# Add back the if statement
result_lines.append(lines[if_block_start])  # "if latest is not None:\n"

# Add all the content of the if block (lines if_block_start+1 to else_line_idx-1)
# These are already properly indented
result_lines.extend(lines[if_block_start + 1:else_line_idx])

# Don't add the else clause - instead, indent all remaining code into the if block
# All remaining lines from else_line_idx onwards need to be:
# 1. Unindented (remove the else: indentation)
# 2. Then indented properly to be inside the if block

for i in range(else_line_idx, len(lines)):
    line = lines[i]

    # Skip the else clause entirely
    if i == else_line_idx:
        continue

    # Skip the else block content (the st.info line and its comment)
    if i == else_line_idx + 1 or i == else_line_idx + 2:
        continue

    # For all other lines, add them as-is (they're at module level after the else)
    # But we need to indent them to be inside the if block

    # Check if line is empty or just whitespace
    if line.strip() == '':
        result_lines.append(line)
    else:
        # Add 4 spaces to indent into the if block
        result_lines.append('    ' + line)

# Write the result
with open('dashboard/app.py', 'w') as f:
    f.writelines(result_lines)

print(f"✓ Fixed module-level code structure")
print(f"  - Moved all code after else clause into if block")
print(f"  - File has {len(result_lines)} lines (was {len(lines)})")
