from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from dotenv import dotenv_values
import sys
import os
import vlc


env_vars=dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

print(f"Current directory: {current_dir}")
print(f"Graphics directory: {GraphicsDirPath}")
print(f"Temp directory: {TempDirPath}")

def create_vlc_instance():
    # Create VLC instance with specific arguments to handle audio properly
    args = [
        '--no-audio',  # Disable audio completely
        '--quiet',     # Reduce VLC's output
        '--no-xlib',   # Prevent X11 dependency on Linux
        '--loop',      # Enable looping
        '--repeat'     # Enable repeat
    ]
    return vlc.Instance(args)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom","can you", "what's", "where's", "how's"]
    
    if any (word + "" in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1] [-1] in ['.', '?', '!']:
            new_query = new_query[-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def initialize_files():
    # Create Files directory if it doesn't exist
    os.makedirs(TempDirPath, exist_ok=True)
    
    # Initialize required files with default values
    files = {
        'Mic.data': 'False',
        'Status.data': '',
        'Responses.data': ''
    } 
    
    for filename, default_value in files.items():
        file_path = os.path.join(TempDirPath, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_value)

def safe_file_write(filepath, content):
    try:
        with open(filepath, "w", encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")
        return False

def safe_file_read(filepath):
    try:
        with open(filepath, "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""

def SetMicrophoneStatus(Command):
    return safe_file_write(os.path.join(TempDirPath, "Mic.data"), Command)

def GetMicrophoneStatus():
    return safe_file_read(os.path.join(TempDirPath, "Mic.data"))

def SetAssistantStatus(Status):
    return safe_file_write(os.path.join(TempDirPath, "Status.data"), Status)

def GetAssistantStatus():
    return safe_file_read(os.path.join(TempDirPath, "Status.data"))

def ShowTextToScreen(Text):
    return safe_file_write(os.path.join(TempDirPath, "Responses.data"), Text)

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    if not os.path.exists(Path):
        print(f"Warning: Image file not found: {Path}")
    return Path

def TempDirectoryPath(Filename): 
    Path = rf'{TempDirPath}\{Filename}'
    return Path

def ShowTextToScreen (Text):
    with open(rf"{TempDirPath}\Responses.data", "w", encoding='utf-8') as file:
        file.write(Text)


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction) # No text interaction
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QScrollBar:vertical {
                border: none;
                background: black; 
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, 
            QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        layout.setSizeConstraint (QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground (text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        # Replace VLC initialization with new method
        self.instance = create_vlc_instance()
        self.media_player = self.instance.media_player_new()
        
        # Update the video widget setup with larger height
        self.video_widget = QLabel()
        self.video_widget.setFixedSize(480, 350)  # Increased height from 270 to 350
        self.video_widget.setStyleSheet("background-color: black;")
        self.video_widget.setAlignment(Qt.AlignCenter)
        
        gif_path = GraphicsDirectoryPath('jarvis-gif-final.gif')
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(480, 350))
            self.movie.setSpeed(120)  # Set speed to 120% of original
            self.video_widget.setMovie(self.movie)
            self.movie.start()
        else:
            print(f"Error: GIF file not found: {gif_path}")
        
        # Create a container widget for the video and status label
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Add video and label to container
        container_layout.addWidget(self.video_widget, alignment=Qt.AlignRight)
        
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px;")
        self.label.setAlignment(Qt.AlignRight)
        container_layout.addWidget(self.label)
        
        # Add container to main layout
        layout.addWidget(container, alignment=Qt.AlignRight | Qt.AlignBottom)
        layout.setSpacing(-10)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.chat_text_edit.viewport().installEventFilter(self)

        # Add timer for file operations
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)  # Check every 100ms instead of 5ms

        self.toggled = True  # Initialize toggle state

    def ensure_playing(self):
        state = self.media_player.get_state()
        if state == vlc.State.Ended or state == vlc.State.Stopped or state == vlc.State.NothingSpecial:
            self.media_player.set_position(0)
            self.media_player.play()

    def loadMessages(self):
        global old_chat_message
        
        messages = safe_file_read(os.path.join(TempDirPath, "Responses.data"))
        
        if messages and messages != old_chat_message:
            self.addMessage(message=messages, color='White')
            old_chat_message = messages

    def SpeechRecogText(self):
        status = safe_file_read(os.path.join(TempDirPath, "Status.data"))
        self.label.setText(status)

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                new_pixmap = pixmap.scaled(width, height)
                self.icon_label.setPixmap(new_pixmap)
            else:
                print(f"Error: Could not load image: {path}")
        else:
            print(f"Error: Image file not found: {path}")

    def toggle_icon(self, event=None):
        self.toggled = not self.toggled  # Toggle state first
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('mute.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic_on.png'), 60, 60)
            MicButtonClosed()

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.mediaPlayer.setPosition(0)
            self.mediaPlayer.play()

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin (10)
        formatm.setLeftMargin (10)
        format.setForeground (QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat (formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)



class InitialScreen(QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width() 
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        
        self.instance = create_vlc_instance()
        self.media_player = self.instance.media_player_new()
        
        self.video_widget = QLabel()
        # Use 80% of screen width instead of full width
        gif_width = int(screen_width * 0.65)  # 80% of screen width
        max_video_height = int(gif_width / 16 * 9) + 240
        self.video_widget.setFixedSize(gif_width, max_video_height)
        self.video_widget.setStyleSheet("background-color: black;")
        self.video_widget.setAlignment(Qt.AlignCenter)
        
        gif_path = GraphicsDirectoryPath('jarvis-gif-final.gif')
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(gif_width, max_video_height))
            self.movie.setSpeed(120)  # Set speed to 120% of original
            self.video_widget.setMovie(self.movie)
            self.movie.start()
        else:
            print(f"Error: GIF file not found: {gif_path}")
        
        # Update layout settings
        content_layout.addWidget(self.video_widget, 0, Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)  # Adjust margins if needed
        
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap (new_pixmap)
        self.icon_label.setFixedSize(150,150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True  # Initialize toggle state
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, -200, 0, 0)  # Adjust top margin to move video up
        content_layout.addSpacing(30)  # Reduce space between video and mic icon
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        # Add timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)  # Check every 100ms

    def ensure_playing(self):
        state = self.media_player.get_state()
        if state == vlc.State.Ended or state == vlc.State.Stopped or state == vlc.State.NothingSpecial:
            self.media_player.set_position(0)
            self.media_player.play()

    def SpeechRecogText(self):
        status = safe_file_read(os.path.join(TempDirPath, "Status.data"))
        self.label.setText(status)

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                new_pixmap = pixmap.scaled(width, height)
                self.icon_label.setPixmap(new_pixmap)
            else:
                print(f"Error: Could not load image: {path}")
        else:
            print(f"Error: Image file not found: {path}")

    def toggle_icon(self, event=None):
        self.toggled = not self.toggled  # Toggle state first
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('mute.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic_on.png'), 60, 60)
            MicButtonClosed()

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.mediaPlayer.setPosition(0)  # Reset to beginning
            self.mediaPlayer.play()  # Play again


class MessageScreen (QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("home-button.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home") 
        home_button.setStyleSheet ("height: 40px; line-height:40px; background-color: white; color: black")
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("messages.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet ("height:40px; line-height: 40px; background-color: white; color: black")
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('minus.png')) 
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('minimize2.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('expand.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat (True)
        self.maximize_button.setStyleSheet ("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape (QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f" {Assistantname.capitalize()} AI ")
        title_label.setStyleSheet ("color: black; font-size: 18px;; background-color: white")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch (1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent (self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        
        if layout is not None:
            layout.addWidget(message_screen)
            
        self.current_screen=message_screen



    def showInitialScreen(self):
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt. FramelessWindowHint)
        self.initUI()
        self.installEventFilter(self)

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget (stacked_widget)

    def closeEvent(self, event):
        # Clean up media players
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'media_player'):
                widget.media_player.stop()
        # Stop all GIF animations
        for widget in self.findChildren(QLabel):
            if hasattr(widget, 'movie') and widget.movie():
                widget.movie().stop()
        event.accept()

    def eventFilter(self, obj, event):
        if event.type() == event.WindowStateChange:
            # Resume video playback when window is restored
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'media_player'):
                    widget.media_player.play()
            # Resume GIF animations when window is restored
            for widget in self.findChildren(QLabel):
                if hasattr(widget, 'movie') and widget.movie():
                    widget.movie().start()
        return super().eventFilter(obj, event)




def GraphicalUserInterface():
    # Initialize required files
    initialize_files()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()