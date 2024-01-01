import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QComboBox, QDesktopWidget, QFileDialog, QMenuBar, QAction
from PyQt5.QtCore import QFile, QTextStream, Qt
from pytube import YouTube
import os
import json

class YouTubeDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.messages = self.load_messages('languages/messages_en.json')  # Ruta actualizada
        self.init_ui()
        self.load_style_sheet()
        self.center_window()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.create_menu()

    def init_ui(self):
        self.setWindowTitle(self.messages['title'])
        self.setGeometry(0, 0, 400, 250)

        self.label = QLabel(self.messages['enter_link'], self)
        self.link_input = QLineEdit(self)
        
        self.format_label = QLabel(self.messages['select_video_format'], self)
        self.format_video_combo = QComboBox(self)
        self.format_audio_label = QLabel(self.messages['select_audio_format'], self)
        self.format_audio_combo = QComboBox(self)

        self.format_video_combo.addItems(["Seleccionar...", "MP4", "MKV"])
        self.format_audio_combo.addItems(["Seleccionar...", "MP3"])

        self.download_button = QPushButton(self.messages['download_button'], self)
        self.download_button.clicked.connect(self.download_video)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.link_input)
        layout.addWidget(self.format_label)
        layout.addWidget(self.format_video_combo)
        layout.addWidget(self.format_audio_label)
        layout.addWidget(self.format_audio_combo)
        layout.addWidget(self.download_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_style_sheet(self):
        style_sheet = QFile("style.css")
        if style_sheet.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_sheet)
            self.setStyleSheet(stream.readAll())

    def center_window(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(int(x), int(y))

    def load_messages(self, file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Archivo de idioma '{file_name}' no encontrado.")
            return {}

    def create_menu(self):
        menu_bar = self.menuBar()
        config_menu = menu_bar.addMenu('Lenguages')

        self.english_action = QAction('English', self)
        self.english_action.triggered.connect(lambda: self.change_language_to('languages/messages_en.json'))
        config_menu.addAction(self.english_action)

        self.spanish_action = QAction('Spanish', self)
        self.spanish_action.triggered.connect(lambda: self.change_language_to('languages/messages_es.json'))
        config_menu.addAction(self.spanish_action)

        self.japan_action = QAction('Japan', self)
        self.japan_action.triggered.connect(lambda: self.change_language_to('languages/messages_jp.json'))
        config_menu.addAction(self.japan_action)

    def change_language_to(self, language_file):
        self.messages = self.load_messages(language_file)
        self.change_language()
    
    def change_language(self):
        self.setWindowTitle(self.messages['title'])
        self.label.setText(self.messages['enter_link'])
        self.format_label.setText(self.messages['select_video_format'])
        self.format_audio_label.setText(self.messages['select_audio_format'])
        self.download_button.setText(self.messages['download_button'])

    def download_video(self):
        video_url = self.link_input.text()
        download_video_format = self.format_video_combo.currentText()
        download_audio_format = self.format_audio_combo.currentText()

        try:
            if download_video_format == "..." and download_audio_format == "...":
                QMessageBox.warning(self, 'Error', self.messages['select_at_least_one_format'])
                return

            yt = YouTube(video_url)
            video = None
            audio = None

            if download_video_format == "MP4":
                video = yt.streams.get_highest_resolution()
            elif download_video_format == "MKV":
                video = yt.streams.filter(file_extension='webm').first()
            
            if download_audio_format == "MP3":
                audio = yt.streams.filter(only_audio=True).first()

            if video or audio:
                default_location = os.path.join(os.path.expanduser("~"), "Desktop")
                save_location, _ = QFileDialog.getSaveFileName(self, self.messages['download_button'], default_location)
                if save_location:
                    if video:
                        video.download(output_path=os.path.dirname(save_location))
                    elif audio:
                        audio.download(output_path=os.path.dirname(save_location))
                    QMessageBox.information(self, self.messages['download_completed'], self.messages['file_downloaded_success'])
                else:
                    QMessageBox.warning(self, 'Error', self.messages['select_valid_location'])
            else:
                QMessageBox.warning(self, 'Error', self.messages['file_not_found'])
        except Exception as e:
            error_message = self.messages['error_download'].format(error_message=str(e))
            QMessageBox.critical(self, 'Error', error_message)

def run_app():
    app = QApplication(sys.argv)
    downloader_app = YouTubeDownloaderApp()
    downloader_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()
