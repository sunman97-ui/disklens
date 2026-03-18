# 🔍 DiskLens

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](#)

**DiskLens** is a high-performance disk space analyzer and cleanup utility built with Python and Tkinter. It provides a visual deep-dive into your storage, allowing you to identify space-hogging folders, locate duplicate files, and safely reclaim space by sending unwanted items to the system Recycle Bin.

---

## ✨ Features

*   **📊 Interactive Treemap**: Visualise your disk usage with nested rectangles (powered by `squarify`).
*   **📈 Resource Charts**: View top folders and distribution of file types via Matplotlib.
*   **👯 Duplicate Finder**: Locate redundant files using fast XXHash-based comparison.
*   **🗑️ Safe Deletion**: Integrated with `send2trash` to move files to the Recycle Bin rather than permanent deletion.
*   **🛡️ Safety First**: Hardcoded "Safe Scan" areas and a robust blocklist to prevent accidental modification of system files.

---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.10+** (Ensure Python is added to your PATH).
*   **Windows OS** (Primary platform for `run.ps1` and Windows-specific safety guards).

### Installation & First Run

Before running DiskLens for the first time, you must set up your virtual environment and install dependencies:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sunman97-ui/disklens.git
    cd disklens
    ```

2.  **Create a virtual environment**:
    ```powershell
    # Using the 'py' launcher (recommended for Windows)
    py -m venv .venv

    # OR using standard python command
    python -m venv .venv
    ```

3.  **Activate and Install**:
    ```powershell
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```

### Subsequent Runs

After the initial setup, you have two ways to launch DiskLens:

*   **Recommended (One-click)**: Right-click `run.ps1` and select **Run with PowerShell**. This automatically uses the virtual environment's Python interpreter.
*   **Manual**:
    ```powershell
    .venv\Scripts\activate
    python main.py
    ```

---

## 🛡️ Safety & Security

### Safe Scan Folders
DiskLens enforces a **"Safe Scan Area"** policy. By default, it will only allow scanning within specific user directories (e.g., `Downloads`, `Documents`, `Desktop`, `Pictures`, `software`). 

**Note for Developers/Power Users**:
If you need to scan custom locations, these must be added to the `_safe_roots()` function in `main.py` on a per-user basis. This protection ensures that critical system directories are never accidentally modified or deleted.

### Blocklist & Guards
The scanner (`src/scanner.py`) includes a hardcoded blocklist of system-critical paths:
*   `C:\Windows`
*   `C:\ProgramData\Microsoft`
*   `System Volume Information`
*   Root-level system files (e.g., `pagefile.sys`, `ntldr`)
*   **Reparse Points**: Symbolic links and junctions are never followed to prevent infinite loops.

---

## 🏗️ Technical Architecture

DiskLens is designed for speed and safety. Here is how the core components interact:

### 1. Multi-threaded Scanner (`src/scanner.py`)
The scanner uses a `ThreadPoolExecutor` to perform parallel directory traversal. It utilizes `os.scandir()` for high-performance file discovery and applies safety filters *before* descending into any directory or calling `stat()` on a file.

### 2. Fast Duplicate Identification (`src/duplicates.py`)
Duplicates are found in two stages:
1.  **Size Matching**: Files with identical sizes are grouped.
2.  **Hash Verification**: Only files with matching sizes are hashed using `xxhash` (a fast non-cryptographic hash) to confirm identity.

### 3. Visualisation Layer (`src/views/`)
*   **Treemap**: Uses the `squarify` algorithm to map file sizes to visual area.
*   **Charts**: Leverages `matplotlib` for generating high-quality bar and pie charts of your data.

### 4. Safe Deletion Logic
Deletion requests are passed to `send2trash`, ensuring that nothing is permanently deleted without a second chance via the Windows Recycle Bin.

---

## 🤝 Contributing

Contributions are welcome! Whether it's a bug fix, a new feature (like cloud storage scanning), or improved UI styling, please feel free to open a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
