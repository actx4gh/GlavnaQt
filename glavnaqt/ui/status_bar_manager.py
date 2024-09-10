from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QProgressBar, QSizePolicy

from glavnaqt.core import config
from glavnaqt.core.event_bus import create_or_get_shared_event_bus


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
        self.busy_indicator = None  # Busy indicator using QProgressBar
        self.worker = None
        self.event_bus.subscribe('initialize_status_bar', self.initialize_status_bar)
        self.event_bus.subscribe('status_update', self.update_status_bar)
        self.event_bus.subscribe('clear_status_bar', self.clear_status_bar)

    def initialize_status_bar(self, status_bar, status_label, initial_text="Status Bar Initialized"):
        self.status_bar = status_bar
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.status_bar.setStyleSheet("border: 0px; padding: 0px")
        self.status_bar.setObjectName("status_bar")

        # Status label takes most of the space
        self.status_label = status_label
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.status_label.setObjectName("status_label")
        self.status_label.setFont(QFont(config.config.font_face))
        self.status_label.setFrameShape(QFrame.Shape.NoFrame)
        self.status_label.setContentsMargins(0, 0, 0, 0)
        self.status_label.setStyleSheet("padding: 0px; margin: 0px; border: 0px;")
        self.status_bar.setSizeGripEnabled(False)
        self.status_label.setToolTip(initial_text)
        self.status_bar.addPermanentWidget(self.status_label, 1)  # Set stretch factor to 1

        # Busy indicator
        self.busy_indicator = QProgressBar(self.status_bar)
        self.busy_indicator.setObjectName('busy_indicator')
        self.busy_indicator.setMaximum(0)  # Indeterminate mode (busy state)
        self.busy_indicator.setStyleSheet("padding-right: 4px; padding-bottom: 2px")
        self.busy_indicator.setVisible(False)  # Initially hidden

        # Set the minimum width for the busy indicator and allow it to resize appropriately
        self.busy_indicator.setMinimumWidth(5)
        self.busy_indicator.setMaximumWidth(50)
        self.busy_indicator.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.status_bar.addPermanentWidget(self.busy_indicator, 0)  # Set stretch factor to 0 (fixed size)
        self.start_worker(text='Status Bar Initialized')

    def start_busy_indicator(self):
        if self.busy_indicator:
            self.busy_indicator.setVisible(True)

    def stop_busy_indicator(self):
        if self.busy_indicator:
            self.busy_indicator.setVisible(False)

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
