import re

with open('src/pages/Dashboard.vue', 'r') as f:
    content = f.read()

# Remove ' data-building'
content = content.replace(' data-building', '')

# Remove the building-badge spans
pattern = r'\s*<span class="building-badge">.*?Building</span>'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Write back
with open('src/pages/Dashboard.vue', 'w') as f:
    f.write(content)
