from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame

from glavnaqt.core import config
from glavnaqt.core.event_bus import create_or_get_shared_event_bus
from glavnaqt.ui.panel import EXPANDING_FIXED, EXPANDING_EXPANDING


class StatusBarUpdateWorker(QThread):
    status_updated = pyqtSignal(str, str)  # Signal to emit updated status text and tooltip

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        status_text = self.kwargs.get('text', 'Default Status Text')
        tooltip_text = status_text
        self.status_updated.emit(status_text, tooltip_text)


class StatusBarManager:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus or create_or_get_shared_event_bus()
        self.status_bar = None
        self.status_label = None
        self.worker = None
        self.event_bus.subscribe('initialize_status_bar', self.initialize_status_bar)
        self.event_bus.subscribe('status_update', self.update_status_bar)
        self.event_bus.subscribe('clear_status_bar', self.clear_status_bar)

    def initialize_status_bar(self, status_bar, status_label, initial_text="Status Bar Initialized"):
        self.status_bar = status_bar
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.status_bar.setStyleSheet("border: 0px; padding: 0px")
        self.status_bar.setObjectName("status_bar")
        self.status_bar.setSizePolicy(*EXPANDING_FIXED)

        self.status_label = status_label
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.status_label.setObjectName("status_label")
        self.status_label.setFont(QFont(config.config.font_face))
        self.status_label.setFrameShape(QFrame.Shape.NoFrame)
        self.status_label.setContentsMargins(0, 0, 0, 0)
        self.status_label.setStyleSheet("padding: 0px; margin: 0px; border: 0px;")
        self.status_label.setSizePolicy(*EXPANDING_EXPANDING)
        self.status_bar.setSizeGripEnabled(False)
        self.status_label.setToolTip(initial_text)
        self.status_bar.addPermanentWidget(self.status_label, 1)
        self.start_worker(text='Status Bar Initialized')

    def start_worker(self, *args, **kwargs):
        # Start the worker thread to perform the status update in the background
        self.worker = StatusBarUpdateWorker(*args, **kwargs)
        self.worker.status_updated.connect(self.update_status_bar)
        self.worker.start()

    def update_status_bar(self, text=None):
        if text is not None:
            self.status_label.setText(text)
            self.status_label.setToolTip(text)

    def clear_status_bar(self):
        if self.status_bar:
            self.status_bar.deleteLater()  # Schedule deletion of the status bar
            self.status_bar = None  # Clear the reference
        if self.status_label:
            self.status_label.deleteLater()  # Schedule deletion of the status label
            self.status_label = None  # Clear the reference
