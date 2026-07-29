<<<<<<< HEAD
# nyxplayer.py - 26.0.4
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl

class NyxPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. Setup Media Core
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7) # Ensure it's not muted by default
        
        # 2. Setup Video Surface
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        
        # 3. UI Construction
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.video_widget)

        self.video_widget.raise_()
        self.video_widget.show()
            
        controls = QHBoxLayout()
        self.play_btn = QPushButton("▶")
        self.play_btn.setStyleSheet("background: #1a1d23; color: #00ff7f; border: 1px solid #2d5a27;")
        self.play_btn.clicked.connect(self.toggle_play)
        # 1. Update the slider as the video moves
        self.player.positionChanged.connect(self._update_position)

        # 2. Update the slider's range based on video length
        self.player.durationChanged.connect(self._update_duration)

        # 3. Watch for the end of the video to reset the button
        self.player.mediaStatusChanged.connect(self._handle_status)

        # 4. Make the slider actually "seek" when you move it
        self.slider.sliderMoved.connect(self._set_position)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.slider)
        layout.addLayout(controls)

        # 4. Diagnostics Listener
        self.player.errorOccurred.connect(lambda e, s: print(f"NyxPlayer Error: {s}"))
        self.player.mediaStatusChanged.connect(self._status_logger)

    def _status_logger(self, status):
        # This will print in your terminal so we can see where it's stuck
        status_names = {0: "NoMedia", 1: "Loading", 2: "Loaded", 3: "Stalled", 4: "Buffering", 6: "EndOfMedia", 7: "InvalidMedia"}
        print(f"NyxPlayer Status: {status_names.get(status.value, status)}")

    def load_media(self, url_str):
        # Force conversion to QUrl
        url = QUrl(url_str)
        if not url.scheme(): # If it's a local path like "C:/video.mp4"
            url = QUrl.fromLocalFile(url_str)
        
        print(f"NyxPlayer Loading: {url.toString()}")
        self.player.setSource(url)
        
    def _update_position(self, position):
        # This moves the slider as the video plays
        self.slider.setValue(position)

    def _update_duration(self, duration):
        # This sets the slider max to the video length (in milliseconds)
        self.slider.setRange(0, duration)

    def _set_position(self, position):
        # This allows you to "scrub" through the video
        self.player.setPosition(position)

    def _handle_status(self, status):
        # If the video reaches the end (EndOfMedia is status 6)
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_btn.setText("↺") # Change to restart icon
            # Optional: self.player.stop()
            
    def toggle_play(self):
        state = self.player.playbackState()
        status = self.player.mediaStatus()
        
        from PyQt6.QtMultimedia import QMediaPlayer
        
        # If finished, restart from beginning
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()
            self.play_btn.setText("⏸")
        elif state == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("▶")
        else:
            self.player.play()
            self.play_btn.setText("⏸")
=======
# nyxplayer.py - 26.0.4
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl

class NyxPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. Setup Media Core
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7) # Ensure it's not muted by default
        
        # 2. Setup Video Surface
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        
        # 3. UI Construction
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.video_widget)

        self.video_widget.raise_()
        self.video_widget.show()
            
        controls = QHBoxLayout()
        self.play_btn = QPushButton("▶")
        self.play_btn.setStyleSheet("background: #1a1d23; color: #00ff7f; border: 1px solid #2d5a27;")
        self.play_btn.clicked.connect(self.toggle_play)
        # 1. Update the slider as the video moves
        self.player.positionChanged.connect(self._update_position)

        # 2. Update the slider's range based on video length
        self.player.durationChanged.connect(self._update_duration)

        # 3. Watch for the end of the video to reset the button
        self.player.mediaStatusChanged.connect(self._handle_status)

        # 4. Make the slider actually "seek" when you move it
        self.slider.sliderMoved.connect(self._set_position)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.slider)
        layout.addLayout(controls)

        # 4. Diagnostics Listener
        self.player.errorOccurred.connect(lambda e, s: print(f"NyxPlayer Error: {s}"))
        self.player.mediaStatusChanged.connect(self._status_logger)

    def _status_logger(self, status):
        # This will print in your terminal so we can see where it's stuck
        status_names = {0: "NoMedia", 1: "Loading", 2: "Loaded", 3: "Stalled", 4: "Buffering", 6: "EndOfMedia", 7: "InvalidMedia"}
        print(f"NyxPlayer Status: {status_names.get(status.value, status)}")

    def load_media(self, url_str):
        # Force conversion to QUrl
        url = QUrl(url_str)
        if not url.scheme(): # If it's a local path like "C:/video.mp4"
            url = QUrl.fromLocalFile(url_str)
        
        print(f"NyxPlayer Loading: {url.toString()}")
        self.player.setSource(url)
        
    def _update_position(self, position):
        # This moves the slider as the video plays
        self.slider.setValue(position)

    def _update_duration(self, duration):
        # This sets the slider max to the video length (in milliseconds)
        self.slider.setRange(0, duration)

    def _set_position(self, position):
        # This allows you to "scrub" through the video
        self.player.setPosition(position)

    def _handle_status(self, status):
        # If the video reaches the end (EndOfMedia is status 6)
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_btn.setText("↺") # Change to restart icon
            # Optional: self.player.stop()
            
    def toggle_play(self):
        state = self.player.playbackState()
        status = self.player.mediaStatus()
        
        from PyQt6.QtMultimedia import QMediaPlayer
        
        # If finished, restart from beginning
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()
            self.play_btn.setText("⏸")
        elif state == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("▶")
        else:
            self.player.play()
            self.play_btn.setText("⏸")
>>>>>>> 73795b21a814b97de410b539d20b65656c9596cc
