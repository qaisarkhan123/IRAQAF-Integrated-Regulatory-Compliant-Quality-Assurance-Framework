#!/usr/bin/env python3
"""
Fix app.py by moving all code that uses 'latest', 'agg', 'score_rows' inside the if block.

Strategy:
1. Find the "if latest is not None:" block (starts around line 7395)
2. Find the corresponding "else:" block (around line 7668)
3. Find the CSS/style code section that's at module level after the else
4. Find where the problematic code starts (around line 8434: "st.markdown('---')")
5. Move that code and everything after it inside the if block, before the else
"""

with open('dashboard/app.py', 'r') as f:
    lines = f.readlines()

# Find the if/else structure
if_line_idx = None
else_line_idx = None

for i, line in enumerate(lines):
    if i >= 7390 and 'if latest is not None:' in line:
        if_line_idx = i
    if i >= 7665 and i <= 7670 and 'else:' in line and 'latest' not in lines[i+1]:
        else_line_idx = i
        break

if if_line_idx is None or else_line_idx is None:
    print(
        f"❌ Could not find if/else structure. if={if_line_idx}, else={else_line_idx}")
    exit(1)

print(f"Found: if at {if_line_idx+1}, else at {else_line_idx+1}")

# Find where the problematic code starts (the st.markdown("---") line)
problem_start_idx = None
for i, line in enumerate(lines):
    if i > else_line_idx and 'st.markdown("---")' in line and '# Original export buttons' in lines[i+1]:
        problem_start_idx = i
        break

if problem_start_idx is None:
    print("❌ Could not find the problem section start")
    exit(1)

print(f"Found problem section at {problem_start_idx+1}")

# The CSS section between else (7668) and problem section (8434) needs to stay at module level
# but everything from problem section onwards needs to be indented

result_lines = []

# Keep everything up to and including the else block's st.info()
for i in range(else_line_idx + 3):  # else, comment, st.info(), blank line
    result_lines.append(lines[i])

# Keep the CSS/style section and function definitions (module-level, OK)
for i in range(else_line_idx + 3, problem_start_idx):
    result_lines.append(lines[i])

# Now indent everything from problem_start_idx onwards by 4 spaces
# These lines need to be inside the if block
for i in range(problem_start_idx, len(lines)):
    line = lines[i]
    if line.strip():  # Non-empty line
        result_lines.append('    ' + line)  # Add 4 spaces
    else:
        result_lines.append(line)  # Keep empty lines as-is

# But wait, we need to restructure the if/else to accommodate this...
# Actually, simpler: move these lines to be inside the if block before the else

# Let me redo this:
result_lines = []

# Lines up to the else block: keep as-is
for i in range(else_line_idx):
    result_lines.append(lines[i])

# Now, indent the problem section to be inside the if block
for i in range(problem_start_idx, len(lines)):
    line = lines[i]
    if line.strip():
        result_lines.append('    ' + line)
    else:
        result_lines.append(line)

# Add the else block after
result_lines.append('\n')
result_lines.append('else:\n')
result_lines.append(
    '    # If \'latest\' data is not available, show placeholder\n')
result_lines.append(
    '    st.info("📊 Dashboard Ready: Upload or generate a security report to view assessment results")\n')

# Add the CSS/style code and function definitions that were between else and problem start
for i in range(else_line_idx + 3, problem_start_idx):
    result_lines.append(lines[i])

with open('dashboard/app.py', 'w') as f:
    f.writelines(result_lines)

print(f"✓ Successfully reorganized app.py")
print(f"  File now has {len(result_lines)} lines (was {len(lines)})")
