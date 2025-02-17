# %%
from pypdf import PdfReader, PdfWriter
import os 

os.chdir("D:/GitHub/bachelorseminar/document")

writer = PdfWriter()

# Read and add pages from the first PDF
reader1 = PdfReader("Deckblatt.pdf")
for page in reader1.pages:
    writer.add_page(page)

# Read and add pages from the second PDF
reader2 = PdfReader("Kubernetes.pdf")
for page in reader2.pages:
    writer.add_page(page)

# Write the merged PDF to a file
with open("Bachelorseminar.pdf", "wb") as output_pdf:
    writer.write(output_pdf)
