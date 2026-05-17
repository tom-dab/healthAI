import sys
import os

# Try multiple PDF libraries
pdf_path = r'c:\Users\Hanane\Downloads\Subscription Payment-2026-04-30-081053.pdf'

try:
    # Try pdfplumber first
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        print(f"✓ Found {len(pdf.pages)} pages\n")
        for i, page in enumerate(pdf.pages):
            print(f"{'='*60}")
            print(f"PAGE {i+1}")
            print(f"{'='*60}")
            text = page.extract_text()
            if text:
                print(text)
            
            # Try to extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\n[TABLES FOUND]")
                for j, table in enumerate(tables):
                    print(f"\nTable {j+1}:")
                    for row in table:
                        print(row)
except ImportError as e:
    print(f"pdfplumber not available: {e}")
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            print(f"PAGE {i+1}:")
            print(page.extract_text())
    except ImportError:
        print("pypdf not available either")
        print("Install with: pip install pdfplumber pypdf")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
