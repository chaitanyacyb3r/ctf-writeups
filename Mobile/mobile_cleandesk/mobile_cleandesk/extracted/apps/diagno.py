import base64
key = base64.b64decode("6mqMbv76RDT1G7yib5XrsS5DolJ+pPfZAGacZN3cTsc=")
print("key length:", len(key))

with open("dk.brunnerne.onevoice/f/statement-archive.seal", "rb") as f:
    blob = f.read()
print("blob length:", len(blob))
print("first 32 bytes:", blob[:32])
print("first 32 hex:", blob[:32].hex())
print("last 16 hex (tag if no header):", blob[-16:].hex())