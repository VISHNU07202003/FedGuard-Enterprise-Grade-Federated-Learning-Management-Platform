import re

with open('pyproject.toml', 'r') as f:
    text = f.read()

text = re.sub(r'\s*"torch>=.*?",\n', '\n', text)
text = text.replace('"flwr[simulation]>=1.9.0"', '"flwr>=1.9.0"')

with open('pyproject.toml', 'w') as f:
    f.write(text)
