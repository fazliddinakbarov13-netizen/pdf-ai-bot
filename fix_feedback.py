import re
import os

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace keyboard labels
content = content.replace('text="👍 Yaxshi"', 'text="👍 Zo\'r"')
content = content.replace('text="👎 Yomon"', 'text="👎 Yaxshilansin"')

# Replace existing messages
content = content.replace('"Sifat qanday?"', '"Natija yoqdimi?"')

# Find all answer_document calls
pattern = r'(await (?:callback\.)?message\.answer_document\([\s\S]*?parse_mode="HTML"\n\s*\))'

matches = re.finditer(pattern, content)

for match in matches:
    stmt = match.group(0)
    # Check if the next line after the statement is a feedback prompt
    end_idx = match.end()
    snippet_after = content[end_idx:end_idx+200]
    
    if '"Natija yoqdimi?"' not in snippet_after and 'get_feedback_keyboard' not in snippet_after:
        # We need to append it.
        # Check if we have callback.message or just message
        is_callback = 'callback.message' in stmt
        prefix = 'await callback.message' if is_callback else 'await message'
        
        replacement = stmt + f'\n        {prefix}.answer("Natija yoqdimi?", reply_markup=get_feedback_keyboard(doc_hash))'
        content = content.replace(stmt, replacement)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Feedback injected!")
