\# gaslightCTF 2026 — Forensics: `icon-sketch` (366 pts)



\*\*Category:\*\* Forensics

\*\*Solves:\*\* 116

\*\*Author:\*\* riyc



\*\*Description:\*\*

> the pee people found the first version of the gaslightCTF icon... apparently theres a flag in here?



\*\*Attachment:\*\* `icon.zip` → contains `icon.png`



\---



\## 1. Initial Recon



Unzipping the attachment gives a single PNG:



```

$ unzip icon.zip

$ file icon.png

icon.png: PNG image data, 2000 x 800, 8-bit/color RGBA, non-interlaced

```



Opening it just shows the gaslightCTF logo — a gas can dripping fuel that turns into flames spelling out "gaslightingCTF":



!\[icon](icon.png)



No visible flag in the image itself, and the description hints heavily at metadata ("first version of the icon", "theres a flag in here") — this points to a metadata-stego challenge rather than pixel/LSB stego.



\## 2. Chunk Analysis



`exiftool`/`binwalk` weren't available in my environment, so I parsed the PNG chunk structure by hand with a short Python script:



```python

import struct

data = open('icon.png','rb').read()

i = 8

while i < len(data):

&#x20;   length = struct.unpack('>I', data\[i:i+4])\[0]

&#x20;   ctype = data\[i+4:i+8].decode('ascii', errors='replace')

&#x20;   print(ctype, length, 'at offset', i)

&#x20;   i += 8 + length + 4

```



Output:



```

IHDR 13 at offset 8

iCCP 355 at offset 33

cICP 4 at offset 400

eXIf 210 at offset 416

pHYs 9 at offset 638

iTXt 1522 at offset 659

tEXt 58 at offset 2193

IDAT 16384 at offset 2263

IDAT 16384 at offset 18659

IDAT 8081 at offset 35055

IEND 0 at offset 43148

```



A vanilla exported PNG doesn't usually carry an `eXIf` chunk \*and\* a 1.5KB `iTXt` (XMP) chunk \*and\* a `tEXt` chunk. Something (probably `exiftool`) was used to hand-stuff extra metadata into this file — exactly where a forensics challenge would hide data.



\## 3. Digging Into the Metadata



\### 3.1 `eXIf` chunk — the clue



The `eXIf` chunk is a raw TIFF/EXIF blob. Inside it, the \*\*ImageDescription\*\* field contains a base64 string:



```

dGhlIHBlZSBwZW9wbGUgc2FpZCB0byBkZWNvZGUgYW5kIHB1dCB0aGUgdGl0bGVzIHRvZ2V0aGVy

```



Decoding it:



```

"the pee people said to decode and put the titles together"

```



This is the puzzle's instruction: there are multiple \*\*Title\*\* fields hidden in the file, each base64-encoded, and they need to be decoded and combined.



\### 3.2 `iTXt` chunk — the titles



The `iTXt` chunk holds an embedded XMP packet (added by ExifTool 12.57, per the `xmptk` attribute). Inside the XMP, there are two separate base64-encoded title strings:



\- One nested under `Iptc4xmpExt:AOTitle` (an "artwork title" field):

&#x20; ```

&#x20; MmUgMmUgMmUgMmUgMmUgMmUgMmUgMmUgNDMgNTQgNDYgMmUgMmUgMmUgNWYgMmUgNjggMzQgMmUgNWYgMmUgMmUgNzAgNzAgMzAgNzMgMzMgMmUgMmUgMzIgNjIgNWYgMmUgMzEgNzMgMmUgMmUgN2Q=

&#x20; ```

\- One under the standard Dublin Core `dc:title`:

&#x20; ```

&#x20; dHpob3J0c2cuLi57cjUuZy4uZy5oZi4uLi4ud18uLi5rLi5oPy4=

&#x20; ```



The second one also shows up again as a `tEXt` chunk with the key `Title` — so it's duplicated, but there are only \*\*two distinct\*\* encoded titles overall, matching the plural "titles" in the clue.



\### 3.3 Decoding both titles



Base64-decoding the two strings gives:



\*\*Title A\*\* (from `AOTitle`) — this one base64-decodes to a \*hex string\*, so it needs a second decode pass (`bytes.fromhex`):



```

2e 2e 2e 2e 2e 2e 2e 2e 43 54 46 2e 2e 2e 5f 2e 68 34 2e 5f 2e 2e 70 70 30 73 33 2e 2e 32 62 5f 2e 31 73 2e 2e 7d

&#x20;     ↓ hex → ASCII

........CTF...\_.h4.\_..pp0s3..2b\_.1s..}

```



\*\*Title B\*\* (from `dc:title` / `tEXt`) — decodes straight to ASCII:



```

tzhortsg...{r5.g..g.hf.....w\_...k..h?.

```



\## 4. Putting the Titles Together



Both decoded strings are the \*\*same length (38 chars)\*\* and use `.` as a placeholder. Overlaying them character-by-character, every position has a real character in \*exactly one\* of the two strings and a `.` in the other — a perfect, unambiguous jigsaw fit:



```python

merged = ''

for a, b in zip(title\_a, title\_b):

&#x20;   merged += a if a != '.' else b

```



Result:



```

tzhortsgCTF{r5\_gh4g\_hfpp0s3w\_2b\_k1sh?}

```



Progress — we can clearly see a `CTF{...}` wrapper in there, but there's a garbled `tzhortsg` prefix and the inside still doesn't read as anything sensible.



\## 5. The Prefix Is Atbash



`tzhortsg` looked deliberately "scrambled" rather than random. Running it through an \*\*Atbash cipher\*\* (a↔z, b↔y, c↔x, … the classic mirror-alphabet substitution) gives:



```

t→g  z→a  h→s  o→l  r→i  t→g  s→h  g→t

= gaslight

```



That's not a coincidence — "gaslight" is literally the CTF's name (visible right there in the icon artwork: \*"gaslightingCTF"\*). This confirms Atbash is the right transform, and it also tells us \*\*which characters in the merged string came from which title\*\*: the prefix came entirely from Title B, and Title B's contribution throughout the rest of the string is \*also\* Atbash-ciphered, while Title A's contribution is plain leetspeak.



So the correct decoding rule is:



\- Character came from \*\*Title A\*\* → keep as-is (plaintext).

\- Character came from \*\*Title B\*\* → apply Atbash.



Re-running the merge with that rule:



```python

def atbash(c):

&#x20;   if c.islower():

&#x20;       return chr(ord('z') - (ord(c) - ord('a')))

&#x20;   if c.isupper():

&#x20;       return chr(ord('Z') - (ord(c) - ord('A')))

&#x20;   return c



out = ''

for a, b in zip(title\_a, title\_b):

&#x20;   out += a if a != '.' else atbash(b)

```



Result:



```

gaslightCTF{i5\_th4t\_supp0s3d\_2b\_p1ss?}

```



\## 6. Final Leetspeak Decode



Swapping the leetspeak digits back to letters (`4→a`, `3→e`, `0→o`, `1→i`, `5→s`) inside the braces:



```

i5\_th4t\_supp0s3d\_2b\_p1ss  →  is\_that\_supposed\_2b\_piss?

```



Which reads perfectly as a joking phrase: \*\*"is that supposed to be piss?"\*\* — a fitting punchline given the icon art is a gas can dripping liquid onto flames, and the challenge description's running joke about "the pee people."



\## 7. Flag



```

gaslightCTF{i5\_th4t\_supp0s3d\_2b\_p1ss?}

```



\## 8. Full Solve Script



```python

import struct, re, base64



data = open('icon.png', 'rb').read()



def get\_chunk(offset):

&#x20;   length = struct.unpack('>I', data\[offset:offset+4])\[0]

&#x20;   ctype = data\[offset+4:offset+8]

&#x20;   cdata = data\[offset+8:offset+8+length]

&#x20;   return ctype, cdata



\# Locate chunks (found via manual chunk walk)

\_, exif = get\_chunk(416)

\_, itxt = get\_chunk(659)



def b64s(blob):

&#x20;   return re.findall(rb'\[A-Za-z0-9+/]{20,}={0,2}', blob)



candidates = b64s(itxt)

title\_a\_hex = base64.b64decode(candidates\[2]).decode()      # "2e 2e .. 7d"

title\_a = bytes.fromhex(title\_a\_hex.replace(' ', '')).decode()

title\_b = base64.b64decode(candidates\[3]).decode()           # "tzhortsg...{..."



def atbash(c):

&#x20;   if c.islower():

&#x20;       return chr(ord('z') - (ord(c) - ord('a')))

&#x20;   if c.isupper():

&#x20;       return chr(ord('Z') - (ord(c) - ord('A')))

&#x20;   return c



merged = ''

for a, b in zip(title\_a, title\_b):

&#x20;   merged += a if a != '.' else atbash(b)



print(merged)  # gaslightCTF{i5\_th4t\_supp0s3d\_2b\_p1ss?}

```



\## 9. Takeaways



\- Always check for stuffed/extra PNG metadata chunks (`eXIf`, `iTXt`/XMP, `tEXt`) — they're a favorite hiding spot for forensics challenges, especially when the file was clearly re-saved through a tool like ExifTool.

\- Multi-layer encodings (base64 → hex → base64) plus a "split across two fields" jigsaw is a common technique to force a step-by-step decode rather than a single automated pass.

\- When a decoded fragment looks like noise but is the right \*length\* and \*character set\* for a known word (here, the challenge's own name), try classic ciphers like Atbash or ROT13 before assuming it's garbage.

\- The `.` placeholders being perfectly complementary between the two title strings (no collisions) was the strongest signal that "overlay" was the intended merge operation, not concatenation.

