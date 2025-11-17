#!/usr/bin/env python3
"""
Comprehensive fix for app.py:
1. Add guard check for 'latest' variable
2. Wrap all problematic code in if/else
3. Properly indent everything
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "_failed_clauses_summary" function end
# and insert our guard check right before "# Gather data"
insert_pos = -1
for i in range(7380, 7400):
    if i < len(lines) and "# Gather data" in lines[i]:
        insert_pos = i
        break

if insert_pos == -1:
    print("Could not find insertion point")
    exit(1)

# Find end of the problematic section (before "# Bottom Panels")
end_pos = -1
for i in range(insert_pos, min(insert_pos + 300, len(lines))):
    if "# =========================" in lines[i] and "Bottom Panels" in lines[i+1] if i+1 < len(lines) else False:
        end_pos = i
        break

if end_pos == -1:
    print("Could not find end position")
    exit(1)

print(
    f"Found: Gather data at {insert_pos+1}, Bottom Panels marker at {end_pos+1}")

# Extract the section to modify
before = lines[:insert_pos]
to_wrap = lines[insert_pos:end_pos]
after = lines[end_pos:]

# Create wrapped version with if/else
wrapped = [
    "\n",
    "# Initialize 'latest' if not defined (module-level code guard)\n",
    "if 'latest' not in dir():\n",
    "    latest = None\n",
    "\n",
    "# Gather data - only if 'latest' is available\n",
    "if latest is not None:\n",
]

# Indent all lines in the problematic section by 4 spaces
for line in to_wrap:
    if line.strip():  # Non-blank lines
        wrapped.append('    ' + line)
    else:
        wrapped.append(line)

# Add else clause
wrapped.extend([
    "else:\n",
    "    # If 'latest' data is not available, show placeholder\n",
    "    st.info(\"📊 Dashboard Ready: Upload or generate a security report to view assessment results\")\n",
    "\n",
])

# Reconstruct file
new_lines = before + wrapped + after

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(
    f"✓ Successfully wrapped and indented code. New file has {len(new_lines)} lines")
