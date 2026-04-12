import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to insert: load_msg = await message.answer("⏳ Ishlanmoqda, kuting...", parse_mode="HTML")
# And then replace it with the first status message.

# But some handlers already have: status_msg = await message.answer("...", parse_mode="HTML")
# For example, voice: status_msg = await message.answer("🔄 Ovoz matnga o'girilmoqda...", parse_mode="HTML")
# We can just change all these initial status messages to "⏳ Ishlanmoqda, kuting..."!
# Let's just find `status_msg = await message.answer(` and change its string to "⏳ Ishlanmoqda, kuting...".

content = re.sub(
    r'status_msg\s*=\s*await\s+message\.answer\(\s*".*?"',
    'status_msg = await message.answer("⏳ Ishlanmoqda, kuting..."',
    content
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Loading messages injected!")
