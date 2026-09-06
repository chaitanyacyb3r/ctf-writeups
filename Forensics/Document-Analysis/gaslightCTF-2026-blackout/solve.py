import pypdf

reader = pypdf.PdfReader("recovered_file")
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        print(f"--- Page {i+1} ---")
        print(text)