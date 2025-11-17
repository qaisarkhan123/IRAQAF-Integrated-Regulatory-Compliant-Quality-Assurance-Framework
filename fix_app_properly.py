#!/usr/bin/env python3
"""
Fix app.py by wrapping all module-level code that depends on 'latest' in a guard condition.
This prevents AttributeError when 'latest' is not defined at module load time.
"""

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first reference to 'latest' variable at module level
# (around line 7382 where "agg = latest.get" appears)
# and wrap everything from there until the end of the module-level code section

# Key insight: We need to find where the problem starts and wrap everything
# that depends on 'latest' in a single large if block

# Search for the "Gather data" comment that starts the problematic section
problem_start_marker = "# Gather data\nagg = latest.get"

if problem_start_marker in content:
    # Find the position
    pos = content.find(problem_start_marker)

    # Find the last major section header before we reach the style definitions
    # Look for "# ---------- Enhanced style helpers ----------" or similar
    style_marker = "# ---------- Enhanced style helpers ----------"
    style_pos = content.find(style_marker)

    if pos > -1 and style_pos > pos:
        # Get everything before the problem
        before_problem = content[:pos]
        # Get the problematic middle section
        problem_section = content[pos:style_pos]
        # Get everything after (starting from style marker)
        after_problem = content[style_pos:]

        # Wrap the problem section in a guard
        wrapped_section = f'''if 'latest' in globals() and latest is not None:
{problem_section}
else:
    st.info("📊 Dashboard Overview: Load or generate a report to view assessment results.")

'''

        # Reconstruct the file
        new_content = before_problem + wrapped_section + after_problem

        with open('dashboard/app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✓ Success: Wrapped problematic section in guard condition")
        print(
            f"  Problem section spanned ~{problem_section.count(chr(10))} lines")
    else:
        print("✗ Could not find style marker")
        print(f"  Positions: problem={pos}, style={style_pos}")
else:
    print("✗ Could not find problem start marker")
    print(f"  Looking for: {repr(problem_start_marker)}")
