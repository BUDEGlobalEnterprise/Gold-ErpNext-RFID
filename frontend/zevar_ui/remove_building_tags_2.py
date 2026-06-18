import re

with open('src/pages/Dashboard.vue', 'r') as f:
    content = f.read()

# Remove 'data-building' anywhere it appears as an attribute
content = re.sub(r'\s*data-building\s*', '', content)

with open('src/pages/Dashboard.vue', 'w') as f:
    f.write(content)
