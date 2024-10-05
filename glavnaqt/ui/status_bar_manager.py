from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QProgressBar, QSizePolicy

from glavnaqt.core.config import UIConfiguration
from glavnaqt.core.event_bus import create_or_get_shared_event_bus


class StatusBarManager(QObject):
    status_updated = pyqtSignal(str, str)  # Signal to emit updated status text and tooltip

    def __init__(self, thread_manager, event_bus=None):
        super().__init__()
        self.ui_config = UIConfiguration.get_instance()
        self.thread_manager = thread_manager
        self.event_bus = event_bus or create_or_get_shared_event_bus()
        self.status_bar = None
        self.status_label = None
        self.busy_indicator = None  # Busy indicator using QProgressBar
        self.event_bus.subscribe('initialize_status_bar', self.initialize_status_bar)
        self.event_bus.subscribe('status_update', self.update_status_bar_event)
        self.event_bus.subscribe('clear_status_bar', self.clear_status_bar)
        self.event_bus.subscribe('show_busy', self.start_busy_indicator)
        self.event_bus.subscribe('hide_busy', self.stop_busy_indicator)

        # Connect the signal to the slot
        self.status_updated.connect(self.update_status_bar)

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
        self.status_label.setFont(QFont(self.ui_config.font_face))
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
        self.busy_indicator.setStyleSheet("padding-right: 4px; padding-bottom: 0px")
        self.busy_indicator.setVisible(False)  # Initially hidden

        # Set the minimum width for the busy indicator and allow it to resize appropriately
        self.busy_indicator.setMinimumWidth(5)
        self.busy_indicator.setMaximumWidth(50)
        self.busy_indicator.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.status_bar.addPermanentWidget(self.busy_indicator, 0)  # Set stretch factor to 0 (fixed size)
        self.start_worker(text=initial_text)

    def start_busy_indicator(self):
        if self.busy_indicator:
            self.busy_indicator.setVisible(True)

    def stop_busy_indicator(self):
        if self.busy_indicator:
            self.busy_indicator.setVisible(False)

    def start_worker(self, *args, **kwargs):
        """
        Start a background task using the ThreadManager.

        :param args: Arguments to pass to the background task.
        :param kwargs: Keyword arguments to pass to the background task.
        """
        self.thread_manager.submit_task(self._process_status_update, *args, **kwargs)

    def _process_status_update(self, *args, **kwargs):
        """
        Background task that processes the status update.

        :param args: Arguments passed from start_worker.
        :param kwargs: Keyword arguments passed from start_worker.
        """
        status_text = kwargs.get('text', 'Default Status Text')
        tooltip_text = status_text

        # Emit the signal to update the GUI in the main thread
        self.status_updated.emit(status_text, tooltip_text)

    def update_status_bar(self, text=None, tooltip=None):
        """
        Slot to update the status bar GUI elements in the main thread.

        :param text: The text to display in the status bar.
        :param tooltip: The tooltip text for the status bar.
        """
        if self.status_label:
            self.status_label.setText(text or '')
            self.status_label.setToolTip(tooltip or text or '')

    def update_status_bar_event(self, text=None):
        """
        Event handler for 'status_update' events from the event bus.

        :param text: The text to display in the status bar.
        """
        if text is not None:
            self.start_worker(text=text)

    def clear_status_bar(self):
        """
        Clear and delete the status bar and its components.
        """
        if self.status_bar:
            self.status_bar.deleteLater()  # Schedule deletion of the status bar
            self.status_bar = None  # Clear the reference
        if self.status_label:
            self.status_label.deleteLater()  # Schedule deletion of the status label
            self.status_label = None  # Clear the reference
