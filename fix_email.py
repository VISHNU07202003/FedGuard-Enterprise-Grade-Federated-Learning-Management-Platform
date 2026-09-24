with open('pyproject.toml', 'r') as f:
    text = f.read()

text = text.replace('"pydantic>=2.0.0",', '"pydantic>=2.0.0",\n    "email-validator>=2.0.0",')

with open('pyproject.toml', 'w') as f:
    f.write(text)
