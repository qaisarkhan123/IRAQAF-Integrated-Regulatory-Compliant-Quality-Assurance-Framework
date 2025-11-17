#!/usr/bin/env python3
"""
Wrap all the export/report code in an if block checking for 'agg' and 'score_rows'.
Lines after the if statement need to be indented.
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the if statement we just added
if_stmt_line = None
for i, line in enumerate(lines):
    if "if 'agg' in locals() and 'score_rows' in locals():" in line:
        if_stmt_line = i
        break

if if_stmt_line is None:
    print("❌ Could not find the if statement")
    exit(1)

print(f"Found if statement at line {if_stmt_line + 1}")

# Find where this section ends - look for the pattern that indicates the end
# We need to find where the else-like construct would be, or end of file
# For now, indent everything after the st.markdown("---") line to the end

# Starting from the line after the if statement, indent everything up to end of file
# Keep up to and including the if statement
result_lines = lines[:if_stmt_line + 1]

# Indent everything after
for i in range(if_stmt_line + 1, len(lines)):
    line = lines[i]
    if line.strip():  # Non-empty line
        result_lines.append('    ' + line)
    else:
        result_lines.append(line)

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(result_lines)

print(f"✓ Indented lines {if_stmt_line + 2}-{len(lines)} inside if block")
print(f"  File now has {len(result_lines)} lines (was {len(lines)})")
