import re

with open('main_backup.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace keyboard labels
content = content.replace('text="👍 Yaxshi"', 'text="👍 Zo\'r"')
content = content.replace('text="👎 Yomon"', 'text="👎 Yaxshilansin"')

# Replace existing messages
content = content.replace('"Sifat qanday?"', '"Natija yoqdimi?"')

# Find all answer_document calls
pattern = r'([ \t]*)(await (?:callback\.)?message\.answer_document\([\s\S]*?parse_mode="HTML"\n\s*\))'
matches = re.finditer(pattern, content)

for match in matches:
    indent = match.group(1)
    stmt = match.group(2)
    full_stmt = match.group(0)
    
    end_idx = match.end()
    snippet_after = content[end_idx:end_idx+200]
    
    if '"Natija yoqdimi?"' not in snippet_after and 'get_feedback_keyboard' not in snippet_after:
        is_callback = 'callback.message' in stmt
        prefix = 'await callback.message' if is_callback else 'await message'
        
        # Append exact same indentation as the captured block
        replacement = full_stmt + f'\n{indent}{prefix}.answer("Natija yoqdimi?", reply_markup=get_feedback_keyboard(doc_hash))'
        content = content.replace(full_stmt, replacement)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Feedback injected properly!")
