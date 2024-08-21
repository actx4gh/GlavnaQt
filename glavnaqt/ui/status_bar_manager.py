# glavnaqt/ui/status_bar_manager.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QStatusBar, QFrame
from PyQt6.QtGui import QFont

from glavnaqt.ui.panel import EXPANDING_FIXED, EXPANDING_EXPANDING

class StatusBarManager:
    def __init__(self, main_window, initial_text="Ready"):
        self.main_window = main_window
        self.status_bar = QStatusBar(main_window)
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.status_bar.setStyleSheet("border: 0px; padding: 0px")
        self.status_bar.setObjectName("status_bar")
        self.status_bar.setSizePolicy(*EXPANDING_FIXED)

        self.status_label = QLabel(initial_text, main_window)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.status_label.setObjectName("status_bar")
        self.status_label.setFont(QFont(main_window.ui_config.font_face))
        self.status_label.setFrameShape(QFrame.Shape.NoFrame)
        self.status_label.setContentsMargins(0, 0, 0, 0)
        self.status_label.setStyleSheet("padding: 0px; margin: 0px;, border: 0px")
        self.status_label.setSizePolicy(*EXPANDING_EXPANDING)

        self.status_bar.addPermanentWidget(self.status_label, 1)
        self.status_bar.setSizeGripEnabled(False)
        self.main_window.setStatusBar(self.status_bar)

        # Set the width of the QStatusBar to match the main window's width
        self.status_bar.resize(self.main_window.width(), self.status_bar.height())
        self.status_bar.updateGeometry()
        self.main_window.updateGeometry()

    def update_status_bar(self, text=None):
        if text is not None:
            self.status_label.setText(text)
            self.status_label.setToolTip(text)

    def clear_status_bar(self):
        self.status_label.clear()
