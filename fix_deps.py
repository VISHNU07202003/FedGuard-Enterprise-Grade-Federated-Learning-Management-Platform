with open('pyproject.toml', 'r') as f:
    text = f.read()

text = text.replace('"passlib[bcrypt]",', '"passlib[bcrypt]",\n    "boto3",\n    "prometheus-client",\n    "openai",')

with open('pyproject.toml', 'w') as f:
    f.write(text)
