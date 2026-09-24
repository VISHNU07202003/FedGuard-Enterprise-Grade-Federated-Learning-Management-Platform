with open('pyproject.toml', 'r') as f:
    text = f.read()

text = text.replace('"fastapi>=0.100.0",', '"fastapi>=0.100.0",\n    "PyJWT>=2.8.0",')

with open('pyproject.toml', 'w') as f:
    f.write(text)
