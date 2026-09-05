# OmniConvert

OmniConvert is a cross-platform desktop application built with Python and PyQt5. It provides a simple, modern interface to convert images, data files, documents, and media into various formats without sending data to external servers.

---

## Features

- **Dark-Themed UI:** Modern interface built using PyQt5.
- **Multithreaded Processing:** Prevents UI freezing during conversions.
- **Image Conversion:** Handles standard raster formats and PDF output.
- **Data & Documents:** Converts tabular structures between CSV, Excel, JSON, HTML, and Parquet formats.
- **Audio & Video:** Leverages FFmpeg for media format transcode.

---

## Supported Formats

| Category | Supported Formats |
| :--- | :--- |
| **Images** | PNG, JPG, JPEG, WEBP, BMP, GIF, ICO, TIFF, PDF |
| **Documents / Data** | CSV, XLSX, XLS, JSON, HTML, PARQUET, TXT, MD |
| **Audio / Video** | MP3, WAV, OGG, FLAC, MP4, MKV, AVI, WEBM |

---

## Prerequisites

- **Python 3.8+**
- **FFmpeg:** Required for audio and video conversion.
  - **Windows:** Download via [ffmpeg.org](https://ffmpeg.org/) or install via WinGet: `winget install ffmpeg`
  - **Linux:** `sudo apt install ffmpeg`
  - **macOS:** `brew install ffmpeg`

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Miaoumap24/OmniConv.git
   cd omniconvert

```

2. **Install Python dependencies:**
```bash
pip install PyQt5 pillow pdf2image pypdf pandas openpyxl markdown

```


*(Note: Missing core packages are auto-installed on the first script run if `pip` is configured in your environment.)*

---

## Usage

Run the main application script:

```bash
python main.py

```

1. Click **📁 Add Files** to populate the queue.
2. Choose the **Target category** and **Format** from the dropdowns.
3. (Optional) Click **📂 Change folder** to set a custom output path (defaults to `~/Downloads`).
4. Click **🚀 Start Conversion**.

---

## Project Structure

```text
├── OmniConv.py          # Application entry point, PyQt5 UI, and ConverterWorker thread
├── README.md            # Project documentation
└── requirements.txt     # List of Python dependencies

```

---

## License

Distributed under the AGPL-3.0 License. See `LICENSE` for more information.

```
