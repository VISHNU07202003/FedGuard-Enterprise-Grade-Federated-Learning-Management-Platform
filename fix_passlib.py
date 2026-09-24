with open('pyproject.toml', 'r') as f:
    text = f.read()

text = text.replace('"email-validator>=2.0.0",', '"email-validator>=2.0.0",\n    "passlib[bcrypt]",')

with open('pyproject.toml', 'w') as f:
    f.write(text)
