

\# gaslightCTF: blackout (Forensics)



\## Challenge Details

\* \*\*Category:\*\* Forensics

\* \*\*Points:\*\* 281 (148 solves)

\* \*\*Author:\*\* riyc

\* \*\*Provided File:\*\* `recovered\_file`



\## Description

> \*i was doing my work, then my power went off! my computer spat this out afterwards, can you recover the flag?\*



\---



\## 1. Initial Triage

The provided challenge attachment is an extensionless file named `recovered\_file`\[cite: 1].



Inspecting the file header reveals standard PDF magic bytes\[cite: 1]:

```bash

$ file recovered\_file

recovered\_file: PDF document, version 1.4



$ head -n 2 recovered\_file

%PDF-1.4

1 0 obj <</Title (recovered\_file) /Producer (Skia/PDF m153 Google Docs Renderer)>>



```



\* \*\*Magic Bytes:\*\* `%PDF-1.4` confirms this is a standard PDF document.





\* \*\*Producer:\*\* `Skia/PDF m153 Google Docs Renderer` indicates the file was exported from Google Docs.







\---



\## 2. Vulnerability \& Mechanism Analysis



When opened in a standard graphical PDF reader, the contents appear heavily obscured or blacked out, aligning with the challenge title \*\*"blackout"\*\*.



\### How PDFs Render Content:



\* A PDF is structured as an object graph containing ordered streams of drawing operations.





\* Text operations (`BT`, `Tj`, `ET`) place character glyphs onto the canvas.

\* Path-drawing operations fill geometric coordinates with color values (e.g., solid black `#000000`).

\* When visual "redactions" are made improperly in word processors (like drawing black shapes or highlights over sensitive text), the renderer draws the text first and layers the opaque shape directly over it.

\* The underlying character stream in the `/Contents` objects remains unscrubbed and fully intact.







Because programmatic extraction utilities (e.g., `pypdf`, `pdftotext`) parse raw character stream instructions rather than rendering visual layers, blacked-out content is extracted as plain text.



\---



\## 3. Reproduction \& Extraction



Using a Python script with `pypdf`, we iterate through all page text streams and match CTF flag patterns via regular expressions:



```python

import pypdf

import re



def solve():

&#x20;   reader = pypdf.PdfReader("recovered\_file")

&#x20;   flag\_pattern = re.compile(r"\[A-Za-z0-9\_]+CTF\\{.\*\\}")



&#x20;   for page\_index, page in enumerate(reader.pages, start=1):

&#x20;       extracted\_text = page.extract\_text()

&#x20;       matches = flag\_pattern.findall(extracted\_text)

&#x20;       if matches:

&#x20;           print(f"\[+] Flag discovered on Page {page\_index}: {matches\[0]}")

&#x20;           return



&#x20;   print("\[-] No flag pattern matched.")



if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   solve()



```



\### Execution Output:



```text

\[+] Flag discovered on Page 6: gaslightCTF{c0w4bung4\_f1le\_4ev3r}



```



The document spans 8 pages populated with repetitive filler text (`"cowabunga bunga bunga..."`). On Page 6, the target flag string is embedded directly in the stream:



```text

cowabunga 

gaslightCTF{c0w4bung4\_f1le\_4ev3r} 

tongue



```



\---



\## 4. Key Takeaways



\* \*\*Visual Layering ≠ Sanitization:\*\* Graphical overlays and cosmetic highlights do not sanitize underlying PDF character object streams.





\* \*\*Stream-Level Triage:\*\* Always examine unrendered object streams using tools like `pypdf`, `pdftotext`, or `qpdf` when analyzing potentially redacted documents.







```



```

