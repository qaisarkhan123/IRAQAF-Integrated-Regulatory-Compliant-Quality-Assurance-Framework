# Fix app.py by removing problematic module-level code

with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

# Find the line with 'gqas = agg.get'
start_idx = -1
end_idx = -1

for i in range(7390, min(7800, len(lines))):
    if 'gqas = agg.get' in lines[i]:
        start_idx = i
        print(f'Found gqas at line {i+1}')
        break

if start_idx > -1:
    # Find where 'if use_llm' block ends and next section starts
    for i in range(start_idx + 1, len(lines)):
        if '# =========================' in lines[i]:
            end_idx = i
            print(f'Found end marker at line {i+1}')
            break

    if end_idx > -1:
        # Keep everything before problem, replace with placeholder, add everything after
        new_lines = (lines[:start_idx] +
                     ['\n', '# Report overview section\n', 'st.info("Dashboard: Upload report to view detailed results")\n', '\n'] +
                     lines[end_idx:])
        with open('dashboard/app.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(
            f'Success: removed lines {start_idx+1}-{end_idx}, now {len(new_lines)} total lines')
    else:
        print('Could not find end')
else:
    print('Could not find start')
