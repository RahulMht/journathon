import os

def extract_text_from_folder(folder_path):
    combined_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            try:
                pdf_loader = PyPDFLoader(r'C:\Users\DELL\Desktop\Newspaper.pdf')
                pages = pdf_loader.load_and_split()
                context = "\n\n".join(str(p.page_content) for p in pages)
            except :
                print(f"Error reading PDF '{filename}")

    return combined_text

if __name__ == "__main__":
    folder_path = r"C:\Users\DELL\Desktop\Newspaper"  # Replace with your actual folder path
    context = extract_text_from_folder(folder_path)
