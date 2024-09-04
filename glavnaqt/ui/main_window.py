import logging
import time
from copy import deepcopy

from PyQt6.QtCore import QTimer, QEventLoop
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QLabel

from glavnaqt.core import config
from glavnaqt.core.event_bus import create_or_get_shared_event_bus
from glavnaqt.core.event_handling import setup_event_handling, ResizeSignal, handle_resize_event
from glavnaqt.ui.layout import LayoutManagerFactory

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):

    def __init__(self, event_bus=None):
        """
        Initializes the MainWindow with the provided UI configuration.
        """
        logger.debug('Initializing MainWindow')
        super().__init__()
        self.layout_manager_factory = LayoutManagerFactory()
        self.layout_manager = None
        self.ui_config = config.config
        self.event_bus = event_bus or create_or_get_shared_event_bus()
        self.suppress_logging = False
        self.resize_signal = ResizeSignal()
        setup_event_handling(self, self.resize_signal)
        self.last_resize_size = self.size()
        self.size_change_threshold = 10
        self.is_resizing = False
        self.suppress_resize_event = True
        self.final_size_timer = QTimer(self)
        self.final_size_timer.setSingleShot(True)
        self.final_size_timer.timeout.connect(self.log_final_size)
        self.last_resize_log_time = time.time()
        self.resize_log_threshold = 0.5
        self.is_fullscreen = False
        self.central_widget = None
        self.status_bar = None
        self.status_label = None
        self.last_layout_sections = None
        self.setWindowTitle("MainWindow")
        self.initial_window_size = self.ui_config.window_size
        self.initial_window_position = self.ui_config.window_position
        self.setGeometry(*self.initial_window_position, *self.initial_window_size)
        self._initialize_status_bar()
        self.resize_emission_args = {'event_type': 'status_update'}
        self.setMinimumSize(100, 100)
        self.layout_manager = self.layout_manager_factory.create_layout_manager("main", self.ui_config)
        self.setCentralWidget(self.layout_manager.get_central_widget())

    def _initialize_status_bar(self):
        if not self.status_bar and self.ui_config.enable_status_bar_manager and 'bottom' in self.ui_config.collapsible_sections:
            self.status_bar = QStatusBar(self)
            self.status_label = QLabel(parent=self.status_bar)
            self.event_bus.emit('initialize_status_bar', self.status_bar, self.status_label)
            self.ui_config.update_collapsible_section('bottom', widget=self.status_bar, status_label=self.status_label)

    def update_ui(self, config):
        """
        Updates the UI layout based on new collapsible sections without tearing down the entire layout.
        The layout is adjusted in memory before being applied to the UI to avoid flickering.
        """
        logger.debug(f'Updating UI to {config}')

        self._initialize_status_bar()
        self.layout_manager.update_layout(config, current_window_size=(self.width(), self.height()))
        self.setCentralWidget(self.layout_manager.get_central_widget())

    def on_resize_timeout(self):
        """
        Callback function triggered when the resize timeout is reached, performing layout adjustments.
        """
        if not self.suppress_logging:
            logger.debug("Resize signal timeout reached, performing layout adjustments.")
        self.layout_manager.adjust_layout()
        if self.status_bar:
            self.event_bus.emit('status_bar_update')

    def resizeEvent(self, event):
        # Preserve the existing resize handling logic
        if self.suppress_resize_event:
            self.suppress_resize_event = False
            return
        self.is_resizing = True
        current_time = time.time()
        if not self.layout_manager.is_initialized or (current_time - self.last_resize_log_time > self.resize_log_threshold):
            logger.debug(f"Resize event handled, new size: {self.size()}")

        self.suppress_logging = True
        handle_resize_event(self, event)
        super().resizeEvent(event)
        self.layout_manager.adjust_layout()
        self.event_bus.emit(**self.resize_emission_args)
        self.suppress_logging = False
        self.final_size_timer.start(200)

    def log_final_size(self):
        """
        Logs the final window size after a resize event, if the window is still being resized.
        """
        if self.is_resizing:
            logger.debug(f"Final window size after resize: {self.size()}")
            self.is_resizing = False

    def toggle_fullscreen_layout(self):
        """Toggle between full-screen and original layout."""
        if self.is_fullscreen:
            self.update_ui(self.layout_manager.last_config)
        else:
            config  = deepcopy(self.layout_manager.current_config)
            config.collapsible_sections = {'main_content': {"alignment": self.ui_config.collapsible_sections["main_content"]["alignment"]}}
            self.update_ui(config)
        self.is_fullscreen = not self.is_fullscreen
        logger.debug(f"UI toggled to {'fullscreen' if self.is_fullscreen else 'original'} layout.")
