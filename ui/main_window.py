import logging
import time

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QMainWindow, QSplitter

from ui.collapsible_splitter import CollapsibleSplitter
from core.config import UIConfiguration
from core.event_handling import setup_event_handling, ResizeSignal, handle_resize_event
from ui.widget_adjustment import adjust_font_and_widget_sizes
from core.layout import initialize_geometries
from ui.helpers import apply_font
from ui.panel import PanelLabel, EXPANDING_FIXED, EXPANDING_EXPANDING, FIXED_EXPANDING
from ui.status_bar_manager import StatusBarManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for the UI, managing layout, splitters, and collapsible sections.

    Attributes:
        ui_config (UIConfiguration): Configuration object containing UI settings.
        is_initialized (bool): Flag indicating whether the UI has been fully initialized.
        main_content_widget (PanelLabel): The main content panel in the UI.
        suppress_logging (bool): Flag to suppress logging during certain operations.
        resize_signal (ResizeSignal): Custom signal for handling resize events.
        last_resize_size (QSize): The last recorded size of the window.
        size_change_threshold (int): Threshold for significant size changes to trigger layout adjustments.
        is_resizing (bool): Flag indicating whether the window is currently being resized.
        suppress_resize_event (bool): Flag to suppress the resize event handling.
        final_size_timer (QTimer): Timer for delaying final size logging after a resize event.
        last_resize_log_time (float): The last time a resize event was logged.
        resize_log_threshold (float): Minimum time between logging resize events.
        status_bar_manager (StatusBarManager): Manager for the status bar, if enabled.
    """

    def __init__(self, ui_config: UIConfiguration):
        """
        Initializes the MainWindow with the provided UI configuration.

        Args:
            ui_config (UIConfiguration): The configuration object containing UI settings.
        """
        logger.debug('Initializing MainWindow')
        super().__init__()

        self.ui_config = ui_config
        self.is_initialized = False
        self.main_content_widget = None
        self.suppress_logging = False
        self.resize_signal = ResizeSignal()
        self.last_resize_size = self.size()
        self.size_change_threshold = 10
        self.is_resizing = False
        self.suppress_resize_event = True
        self.final_size_timer = QTimer(self)
        self.final_size_timer.setSingleShot(True)
        self.final_size_timer.timeout.connect(self.log_final_size)
        self.last_resize_log_time = time.time()
        self.resize_log_threshold = 0.5

        self.setWindowTitle("Collapsible Splitters")
        self.setGeometry(*self.ui_config.window_position, *self.ui_config.window_size)

        self.top_splitter = None
        self.bottom_splitter = None
        self.left_splitter = None
        self.right_splitter = None
        self._status_bar_manager = None
        self.setup_ui(self.ui_config.collapsible_sections)
        setup_event_handling(self, self.resize_signal)
        self.setMinimumSize(100, 100)
        self.finalize_initialization()

    @property
    def status_bar_manager(self):
        """Lazily initializes and returns the StatusBarManager."""
        if self._status_bar_manager is None and self.ui_config.enable_status_bar_manager:
            self._status_bar_manager = StatusBarManager(self)
        return self._status_bar_manager

    def finalize_initialization(self):
        """
        Finalizes the initialization process by adjusting geometries after a short delay.
        """
        QTimer.singleShot(50, lambda: self.initialize_geometries_after_delay())

    def initialize_geometries_after_delay(self):
        """
        Initializes the geometries of the UI components after a delay to ensure proper layout.
        """
        initialize_geometries(self)
        self.adjust_layout()
        self.is_initialized = True
        logger.debug('MainWindow initialization complete')

    def setup_ui(self, collapsible_sections):
        """
        Sets up the UI by creating the necessary splitters and panels based on the collapsible sections.
        """
        self.central_widget = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(self.central_widget)

        vertical_splitter = self.central_widget

        # Handle the "top" section
        if "top" in collapsible_sections:
            self.top_splitter = self.create_splitter(Qt.Orientation.Vertical, "top")
            top_widget = PanelLabel(
                collapsible_sections["top"]["text"],
                "top_bar",
                EXPANDING_FIXED,
                font_name=self.ui_config.font_face,
                font_size=self.ui_config.font_size,
                alignment=self.ui_config.get_section_alignment("top")
            )
            apply_font(self.ui_config.font_face, self.ui_config.font_size, top_widget)
            self.top_splitter.addWidget(top_widget)
            main_content_splitter = self.create_main_content_splitter(collapsible_sections)
            self.top_splitter.addWidget(main_content_splitter)
            vertical_splitter.addWidget(self.top_splitter)
        else:
            main_content_splitter = self.create_main_content_splitter(collapsible_sections)
            vertical_splitter.addWidget(main_content_splitter)

        # Handle the "bottom" section
        if "bottom" in collapsible_sections:
            self.bottom_splitter = self.create_splitter(Qt.Orientation.Vertical, "bottom")
            self.bottom_splitter.addWidget(vertical_splitter)
            bottom_widget = PanelLabel(
                collapsible_sections["bottom"]["text"],
                "status_bar",
                EXPANDING_FIXED,
                font_name=self.ui_config.font_face,
                font_size=self.ui_config.font_size,
                alignment=self.ui_config.get_section_alignment("bottom")
            ) if not self.status_bar_manager else self.status_bar_manager.status_bar
            apply_font(self.ui_config.font_face, self.ui_config.font_size, bottom_widget)
            self.bottom_splitter.addWidget(bottom_widget)
            self.setCentralWidget(self.bottom_splitter)
        else:
            self.setCentralWidget(vertical_splitter)

    def update_ui(self, collapsible_sections):
        """
        Updates the UI layout based on new collapsible sections without tearing down the entire layout.
        The layout is adjusted in memory before being applied to the UI to avoid flickering.
        """
        logger.debug(f'Updating UI to {collapsible_sections}')

        # Clean up the current central widget and all child widgets
        if self.centralWidget():
            old_central_widget = self.centralWidget()
            self.setCentralWidget(None)
            old_central_widget.deleteLater()

        # Clear references to old splitters
        self.top_splitter = None
        self.bottom_splitter = None
        self.left_splitter = None
        self.right_splitter = None

        # Create a new temporary central widget
        temporary_central_widget = QSplitter(Qt.Orientation.Vertical)

        # Set up the UI within the temporary widget
        vertical_splitter = temporary_central_widget

        if "top" in collapsible_sections:
            top_splitter = self.create_splitter(Qt.Orientation.Vertical, "top")
            top_widget = PanelLabel(
                collapsible_sections["top"]["text"],
                "top_bar",
                EXPANDING_FIXED,
                font_name=self.ui_config.font_face,
                font_size=self.ui_config.font_size,
                alignment=self.ui_config.get_section_alignment("top")
            )
            apply_font(self.ui_config.font_face, self.ui_config.font_size, top_widget)
            top_splitter.addWidget(top_widget)
            main_content_splitter = self.create_main_content_splitter(collapsible_sections)
            top_splitter.addWidget(main_content_splitter)
            vertical_splitter.addWidget(top_splitter)
            self.top_splitter = top_splitter  # Store reference to prevent premature deletion
        else:
            main_content_splitter = self.create_main_content_splitter(collapsible_sections)
            vertical_splitter.addWidget(main_content_splitter)

        if "bottom" in collapsible_sections:
            bottom_splitter = self.create_splitter(Qt.Orientation.Vertical, "bottom")
            bottom_splitter.addWidget(vertical_splitter)
            bottom_widget = PanelLabel(
                collapsible_sections["bottom"]["text"],
                "status_bar",
                EXPANDING_FIXED,
                font_name=self.ui_config.font_face,
                font_size=self.ui_config.font_size,
                alignment=self.ui_config.get_section_alignment("bottom")
            ) if not self.status_bar_manager else self.status_bar_manager.status_bar
            apply_font(self.ui_config.font_face, self.ui_config.font_size, bottom_widget)
            bottom_splitter.addWidget(bottom_widget)
            temporary_central_widget = bottom_splitter
            self.bottom_splitter = bottom_splitter  # Store reference to prevent premature deletion

        # Replace the current central widget with the new one and adjust the layout
        self.setCentralWidget(temporary_central_widget)
        QTimer.singleShot(0, self.adjust_layout)

    def create_main_content_splitter(self, collapsible_sections):
        """
        Creates the main content splitter, which manages the layout of the central content and sidebars.

        Args:
            collapsible_sections (dict): Dictionary of sections that can be collapsed in the UI.

        Returns:
            QSplitter: The splitter managing the main content and sidebars.
        """
        horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.main_content_widget = PanelLabel(
            collapsible_sections["main_content"]["text"],
            "main_content",
            EXPANDING_EXPANDING,
            font_name=self.ui_config.font_face,
            font_size=self.ui_config.font_size,
            alignment=self.ui_config.get_section_alignment("main_content")
        )
        apply_font(self.ui_config.font_face, self.ui_config.font_size, self.main_content_widget)

        # Add the left sidebar if defined
        if "left" in collapsible_sections:
            self.left_splitter = self.create_splitter(Qt.Orientation.Horizontal, "left")
            left_sidebar_widget = PanelLabel(
                collapsible_sections["left"]["text"],
                "left_sidebar",
                FIXED_EXPANDING,
                font_name=self.ui_config.font_face,
                font_size=self.ui_config.font_size,
                alignment=self.ui_config.get_section_alignment("left")
            )
            apply_font(self.ui_config.font_face, self.ui_config.font_size, left_sidebar_widget)
            self.left_splitter.addWidget(left_sidebar_widget)
            self.left_splitter.addWidget(self.main_content_widget)
            horizontal_splitter.addWidget(self.left_splitter)
        else:
            horizontal_splitter.addWidget(self.main_content_widget)

        # Add the right sidebar if defined
        if "right" in collapsible_sections:
            self.right_splitter = self.create_splitter(Qt.Orientation.Horizontal, "right")
            self.right_splitter.addWidget(horizontal_splitter)
            right_sidebar_widget = PanelLabel(
                collapsible_sections["right"]["text"],
                "right_sidebar",
                FIXED_EXPANDING,
                font_name=self.ui_config.font_face,
                font_size=self.ui_config.font_size,
                alignment=self.ui_config.get_section_alignment("right")
            )
            apply_font(self.ui_config.font_face, self.ui_config.font_size, right_sidebar_widget)
            self.right_splitter.addWidget(right_sidebar_widget)
            return self.right_splitter

        return horizontal_splitter

    def create_splitter(self, orientation, identifier="default"):
        """
        Creates a collapsible splitter with the given orientation and identifier.

        Args:
            orientation (Qt.Orientation): The orientation of the splitter (horizontal or vertical).
            identifier (str): An identifier for the splitter, used for logging.

        Returns:
            CollapsibleSplitter: The created splitter.
        """
        logger.debug(f'Creating collapsible splitter for {identifier}')
        splitter = CollapsibleSplitter(orientation, identifier=identifier,
                                       handle_width=self.ui_config.splitter_handle_width)
        splitter.splitterMoved.connect(lambda pos, index: self.handle_splitter_movement(splitter, pos, index))
        return splitter

    def handle_splitter_movement(self, splitter, pos, index):
        """
        Handles the movement of a splitter, adjusting the layout accordingly.

        Args:
            splitter (CollapsibleSplitter): The splitter being moved.
            pos (int): The position of the splitter handle.
            index (int): The index of the splitter handle.
        """
        logger.debug(f'Handling splitter movement for {splitter.identifier} at position {pos} and index {index}')
        self.adjust_layout()

    def on_resize_timeout(self):
        """
        Callback function triggered when the resize timeout is reached, performing layout adjustments.
        """
        if not self.suppress_logging:
            logger.debug("Resize signal timeout reached, performing layout adjustments.")
        self.adjust_layout()
        if self.status_bar_manager:
            self.status_bar_manager.update_status_bar()

    def resizeEvent(self, event):
        """
        Handles the window resize event, adjusting the layout and logging as necessary.

        Args:
            event (QResizeEvent): The resize event.
        """
        if self.suppress_resize_event:
            self.suppress_resize_event = False
            return
        self.is_resizing = True
        current_time = time.time()
        if not self.is_initialized or (current_time - self.last_resize_log_time > self.resize_log_threshold):
            logger.debug(f"Resize event handled, new size: {self.size()}")
        self.suppress_logging = True
        handle_resize_event(self, event)
        super().resizeEvent(event)
        self.adjust_layout()
        if self.status_bar_manager:
            self.status_bar_manager.update_status_bar()
        self.suppress_logging = False
        self.final_size_timer.start(200)

    def adjust_layout(self):
        """
        Adjusts the layout of the window and its components, ensuring everything is resized appropriately.
        """
        log_required = not self.suppress_logging
        if log_required:
            logger.debug("Entered adjust_layout.")

        if not self.main_content_widget:
            logger.error("main_content_widget is not initialized. Layout adjustment cannot proceed.")
            return

        try:
            adjust_font_and_widget_sizes(self)
        except Exception as e:
            logging.error(f"Exception occurred during layout adjustment: {e}", exc_info=True)

        if log_required:
            logger.debug("Exiting adjust_layout.")

    def log_final_size(self):
        """
        Logs the final window size after a resize event, if the window is still being resized.
        """
        if self.is_resizing:
            logger.debug(f"Final window size after resize: {self.size()}")
            self.is_resizing = False
