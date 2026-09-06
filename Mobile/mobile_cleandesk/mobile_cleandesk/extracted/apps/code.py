import base64
import sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = base64.b64decode("6mqMbv76RDT1G7yib5XrsS5DolJ+pPfZAGacZN3cTsc=")
aesgcm = AESGCM(key)

conn = sqlite3.connect("dk.brunnerne.onevoice/db/notes.db")
cur = conn.cursor()
cur.execute("""
    SELECT m.id, p.display, m.direction, m.sent_ms, m.sealed
    FROM messages m JOIN peers p ON m.peer_id = p.peer_id
    ORDER BY m.sent_ms
""")

for id_, peer, direction, sent_ms, sealed in cur.fetchall():
    try:
        blob = base64.b64decode(sealed)
        nonce, ct = blob[:12], blob[12:]
        pt = aesgcm.decrypt(nonce, ct, None)
        print(f"[{id_}] {peer} ({direction}): {pt.decode()}")
    except Exception as e:
        print(f"[{id_}] {peer} ({direction}): FAILED - {e}")