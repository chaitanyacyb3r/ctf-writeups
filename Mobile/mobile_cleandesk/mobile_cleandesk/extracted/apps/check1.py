with open("dk.brunnerne.onevoice/f/statement-archive.seal", "rb") as f:
    blob = f.read()
print(len(blob))
print(blob[:32].hex())