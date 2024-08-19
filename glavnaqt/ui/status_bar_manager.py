from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QStatusBar


class StatusBarManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.status_bar = QStatusBar(main_window)

        # Default label - no text, ready for customization
        self.status_label = QLabel("", main_window)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.setSizeGripEnabled(False)
        self.main_window.setStatusBar(self.status_bar)

    def update_status_bar(self, text=None):
        # Allows setting the status text; if None, it will not change the current text
        if text is not None:
            self.status_label.setText(text)
            self.status_label.setToolTip(text)

    def clear_status_bar(self):
        # Clears the status bar text
        self.status_label.clear()
