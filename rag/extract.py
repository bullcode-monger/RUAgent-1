from pypdf import PdfReader
import os

RAW_FLODER = "documents/raw"
OUTPUT_FOLDER = "documents/processed"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for root, dirs, files in os.walk(RAW_FLODER):

    for file in files:

        if not file.endswith(".pdf"):
            continue

        pdf_path = os.path.join(root, file)

        print(f"Reading {file}")

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

        txt_name = file.replace(".pdf", ".txt")

        with open(
            os.path.join(OUTPUT_FOLDER, txt_name),
            "w",
            encoding="utf-8"
        ) as f:
            
            f.write(text)

print("Extraction complete.")
