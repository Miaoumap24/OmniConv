import sys
import os
import subprocess
import threading
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QFileDialog, QProgressBar,
        QListWidget, QListWidgetItem, QMessageBox, QFrame, QSplitter
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QObject
    from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
except ImportError:
    print("PyQt5 is required. Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5", "pillow", "pdf2image", "pypdf", "pandas", "openpyxl"])
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QFileDialog, QProgressBar,
        QListWidget, QListWidgetItem, QMessageBox, QFrame, QSplitter
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QObject
    from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

class ConverterWorker(QObject):
    finished = pyqtSignal(bool, str, str)
    progress = pyqtSignal(int)

    def __init__(self, file_path, target_format, output_dir):
        super().__init__()
        self.file_path = file_path
        self.target_format = target_format.lower()
        self.output_dir = output_dir

    def run(self):
        try:
            input_path = Path(self.file_path)
            output_file = Path(self.output_dir) / f"{input_path.stem}.{self.target_format}"
            ext_in = input_path.suffix.lower().replace('.', '')
            ext_out = self.target_format

            self.progress.emit(20)

            # --- IMAGE CONVERSIONS ---
            image_formats = ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'ico', 'pdf']
            if ext_in in ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'ico', 'tiff'] and ext_out in image_formats:
                from PIL import Image
                img = Image.open(input_path)
                if ext_out in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                if ext_out == 'pdf':
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(output_file, 'PDF')
                else:
                    img.save(output_file)

            # --- DATA / DOCUMENT CONVERSIONS ---
            elif ext_in in ['csv', 'xlsx', 'xls', 'json', 'parquet'] and ext_out in ['csv', 'xlsx', 'json', 'html', 'parquet']:
                import pandas as pd
                if ext_in == 'csv':
                    df = pd.read_csv(input_path)
                elif ext_in in ['xlsx', 'xls']:
                    df = pd.read_excel(input_path)
                elif ext_in == 'json':
                    df = pd.read_json(input_path)
                elif ext_in == 'parquet':
                    df = pd.read_parquet(input_path)

                self.progress.emit(60)

                if ext_out == 'csv':
                    df.to_csv(output_file, index=False)
                elif ext_out == 'xlsx':
                    df.to_excel(output_file, index=False)
                elif ext_out == 'json':
                    df.to_json(output_file, orient='records', indent=4)
                elif ext_out == 'html':
                    df.to_html(output_file, index=False)
                elif ext_out == 'parquet':
                    df.to_parquet(output_file, index=False)

            # --- AUDIO / VIDEO CONVERSIONS ---
            elif ext_in in ['mp4', 'mkv', 'avi', 'mov', 'webm', 'mp3', 'wav', 'ogg', 'flac', 'm4a']:
                # Call ffmpeg directly
                cmd = ['ffmpeg', '-y', '-i', str(input_path), str(output_file)]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.returncode != 0:
                    raise Exception("FFmpeg is required for audio/video conversion (not found or execution error).")

            # --- TEXT / MARKDOWN / HTML / PDF ---
            elif ext_in in ['md', 'html', 'txt'] and ext_out in ['html', 'txt', 'md']:
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if ext_out == 'txt':
                    import re
                    clean = re.sub('<[^<]+?>', '', content) if ext_in == 'html' else content
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(clean)
                elif ext_out == 'html':
                    if ext_in == 'md':
                        import markdown
                        html_content = f"<html><body>{markdown.markdown(content)}</body></html>"
                    else:
                        html_content = f"<html><body><pre>{content}</pre></body></html>"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                elif ext_out == 'md':
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Converted from {ext_in}\n\n{content}")

            else:
                raise Exception(f"Unsupported conversion: .{ext_in} to .{ext_out}")

            self.progress.emit(100)
            self.finished.emit(True, str(output_file), str(input_path))

        except Exception as e:
            self.finished.emit(False, str(e), str(self.file_path))


class UniversalConverterUI(QMainWindow):
    FORMAT_MAP = {
        'Images': ['PNG', 'JPG', 'WEBP', 'BMP', 'GIF', 'ICO', 'TIFF', 'PDF'],
        'Documents / Data': ['CSV', 'XLSX', 'JSON', 'HTML', 'PARQUET', 'TXT', 'MD'],
        'Audio / Video': ['MP3', 'WAV', 'OGG', 'FLAC', 'MP4', 'MKV', 'AVI', 'WEBM']
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniConvert")
        self.resize(850, 550)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f111a;
            }
            QWidget {
                color: #e0e6ed;
                font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
                font-size: 13px;
            }
            QFrame#card {
                background-color: #1a1d2e;
                border-radius: 12px;
                border: 1px solid #282c45;
            }
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #282c45;
                color: #64748b;
            }
            QComboBox {
                background-color: #24283b;
                border: 1px solid #3b4261;
                border-radius: 6px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QListWidget {
                background-color: #161824;
                border: 1px solid #282c45;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1f2335;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #2d324d;
                color: #60a5fa;
            }
            QProgressBar {
                border: none;
                background-color: #161824;
                height: 8px;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 4px;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                color: #60a5fa;
            }
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(15, 15, 15, 15)

        title_lbl = QLabel("OmniConvert")
        title_lbl.setObjectName("title")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        self.btn_select_files = QPushButton("📁 Add Files")
        self.btn_select_files.clicked.connect(self.select_files)
        header_layout.addWidget(self.btn_select_files)

        main_layout.addWidget(header_card)

        body_card = QFrame()
        body_card.setObjectName("card")
        body_layout = QHBoxLayout(body_card)
        body_layout.setContentsMargins(15, 15, 15, 15)

        left_box = QVBoxLayout()
        left_box.addWidget(QLabel("<b>Selected files:</b>"))
        self.file_list = QListWidget()
        left_box.addWidget(self.file_list)

        btn_remove = QPushButton("❌ Remove files")
        btn_remove.setStyleSheet("background-color: #ef4444;")
        btn_remove.clicked.connect(self.remove_selected_file)
        left_box.addWidget(btn_remove)

        body_layout.addLayout(left_box, stretch=2)

        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        right_box.addWidget(QLabel("<b>Target format:</b>"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.FORMAT_MAP.keys())
        self.category_combo.currentTextChanged.connect(self.update_formats)
        right_box.addWidget(self.category_combo)

        self.format_combo = QComboBox()
        right_box.addWidget(self.format_combo)
        self.update_formats(self.category_combo.currentText())

        right_box.addSpacing(15)

        right_box.addWidget(QLabel("<b>Output directory:</b>"))
        self.output_dir = str(Path.home() / "Downloads")
        self.lbl_output_path = QLabel(f"{self.output_dir}")
        self.lbl_output_path.setWordWrap(True)
        self.lbl_output_path.setStyleSheet("color: #94a3b8; font-size: 11px;")
        right_box.addWidget(self.lbl_output_path)

        btn_change_dir = QPushButton("📂 Change folder")
        btn_change_dir.setStyleSheet("background-color: #334155;")
        btn_change_dir.clicked.connect(self.change_output_dir)
        right_box.addWidget(btn_change_dir)

        right_box.addStretch()

        self.btn_convert = QPushButton("🚀 Start Conversion")
        self.btn_convert.setStyleSheet("background-color: #10b981; font-size: 14px; padding: 12px;")
        self.btn_convert.clicked.connect(self.start_conversion)
        right_box.addWidget(self.btn_convert)

        body_layout.addLayout(right_box, stretch=1)
        main_layout.addWidget(body_card)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("Ready to convert your files.")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color: #94a3b8;")
        main_layout.addWidget(self.status_lbl)

        self.setCentralWidget(main_widget)

    def update_formats(self, category):
        self.format_combo.clear()
        self.format_combo.addItems(self.FORMAT_MAP.get(category, []))

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files")
        if files:
            for f in files:
                self.file_list.addItem(f)

    def remove_selected_file(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def change_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_dir)
        if directory:
            self.output_dir = directory
            self.lbl_output_path.setText(f"{self.output_dir}")

    def start_conversion(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "No file selected!")
            return

        target_fmt = self.format_combo.currentText()
        total_files = self.file_list.count()

        self.btn_convert.setEnabled(False)
        self.progress_bar.setValue(0)

        for i in range(total_files):
            file_path = self.file_list.item(i).text()
            self.status_lbl.setText(f"Converting {Path(file_path).name}...")

            thread = threading.Thread(
                target=self.run_worker_sync,
                args=(file_path, target_fmt, self.output_dir)
            )
            thread.start()
            thread.join()

            progress_val = int(((i + 1) / total_files) * 100)
            self.progress_bar.setValue(progress_val)

        self.status_lbl.setText("🎉 Conversion successful")
        self.btn_convert.setEnabled(True)
        QMessageBox.information(self, "Success", f"All files have been converted to: {self.output_dir}")

    def run_worker_sync(self, file_path, target_format, output_dir):
        worker = ConverterWorker(file_path, target_format, output_dir)
        worker.run()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UniversalConverterUI()
    window.show()
    sys.exit(app.exec_())