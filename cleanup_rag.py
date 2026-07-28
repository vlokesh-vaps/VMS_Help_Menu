import re

with open('src/core/rag.py', 'r') as f:
    content = f.read()

# Remove the lead collection function blocks using regex
patterns_to_remove = [
    r'def _lead_collection_is_active\(chat_history.*?\n    return False\n\n',
    r'def _extract_lead_details\(text.*?\n    return details\n\n',
    r'def _collect_lead_details\(chat_history.*?\n    return _extract_lead_details\(combined_user_text\)\n\n',
    r'def _build_lead_capture_answer\(chat_history.*?f"You can also call our sales team at \{VAPS_CONTACT_NUMBER\}."\n    \)\n\n',
]

for pattern in patterns_to_remove:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Remove VAPS_CONTACT_NUMBER from imports
content = content.replace('    VAPS_CONTACT_NUMBER,\n', '')

# Remove import re if not used
if 're.compile' not in content and 're.sub' not in content and 're.IGNORECASE' not in content:
    content = content.replace('import re\n', '')

with open('src/core/rag.py', 'w') as f:
    f.write(content)

print('File cleaned successfully!')

