def name(*names):
    name = ''.join(map(lambda name: name.title(), names))
    name = ''.join(e for e in name if e.isalnum())
    return name
