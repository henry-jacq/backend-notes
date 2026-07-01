# Backend Notes: Systems Engineering

This repository contains structured systems engineering notes compiled into a single book-style PDF.

## PDF Compilation Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install GTK & Pango Dependencies (Windows)
WeasyPrint requires GTK3 and Pango for document rendering. Install these using MSYS2:

1. Download and run the installer from the [MSYS2 website](https://www.msys2.org/).
2. Launch the **MSYS2 UCRT64** terminal from your Start Menu.
3. Update the package database:
   ```bash
   pacman -Syu
   ```
4. Install the required GTK3 and Pango packages:
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-gtk3 mingw-w64-ucrt-x86_64-pango
   ```

The compile script automatically loads these DLLs from `C:\msys64\ucrt64\bin`.

### 3. Generate the PDF
Run the generator script at the repository root:
```bash
python generate_pdf.py
```
The compiled book will be saved as `backend_notes.pdf`.