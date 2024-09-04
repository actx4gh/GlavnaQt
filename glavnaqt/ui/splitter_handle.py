from PyQt6.QtGui import QMouseEvent, QCursor
from PyQt6.QtWidgets import QSplitterHandle, QSplitter, QMainWindow
from PyQt6.QtCore import Qt

from glavnaqt.core import logger


class CollapsibleSplitterHandle(QSplitterHandle):
    """
    A custom handle for a splitter that supports collapsing and expanding sections
    and dynamically adjusts its width based on QMainWindow size.

    Attributes:
        identifier (str): A unique identifier for the splitter handle, used for logging and identifying handles.
        initial_handle_width (int): The initial width of the handle for calculating resizing.
        original_window_width (int): The initial width of the QMainWindow for scaling calculations.
        original_window_height (int): The initial height of the QMainWindow for scaling calculations.
        main_window (QMainWindow): A reference to the QMainWindow containing the splitter handle.
    """

    def __init__(self, orientation, parent: QSplitter, identifier=None):
        """
        Initializes the custom splitter handle with the specified orientation and parent.

        Args:
            orientation (Qt.Orientation): The orientation of the splitter (horizontal or vertical).
            parent (QSplitter): The parent splitter widget of the handle.
            identifier (str, optional): A unique identifier for the splitter handle. Defaults to None.
        """
        super().__init__(orientation, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: black; padding: 0px; margin: 0px")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.identifier = identifier
        self.initial_handle_width = parent.handleWidth()  # Fetch the handle width from the parent
        self.setHandleWidth(self.initial_handle_width)

        # Initialize main window reference to None
        self.original_window_width = None
        self.original_window_height = None
        self.main_window = None

        # Find and store the initial dimensions of the QMainWindow
        self._initialize_main_window_dimensions()

        logger.debug(f'Custom splitter handle initialized for {identifier}')


    def _initialize_main_window_dimensions(self):
        """
        Initializes the main window reference and its dimensions.
        """
        if not self.main_window:
            self.main_window = self._find_main_window()
        if self.main_window and not all((self.original_window_width, self.original_window_height)):
            self.original_window_width = self.main_window.initial_window_size[0]
            self.original_window_height = self.main_window.initial_window_size[1]

    def resizeEvent(self, event):
        """
        Overrides the resize event to dynamically adjust handle width based on QMainWindow size.

        Args:
            event: The resize event to handle.
        """
        super().resizeEvent(event)
        self._adjust_handle_width()

    def _adjust_handle_width(self):
        """
        Adjusts the handle width dynamically based on the QMainWindow's size.
        """
        if not all((self.original_window_width, self.original_window_height)):
            self._initialize_main_window_dimensions()
        if self.main_window and all((self.original_window_width, self.original_window_height)):
            # Calculate scaling factors based on the original and current size of the QMainWindow
            current_width = self.main_window.width()
            current_height = self.main_window.height()
            scaling_factor = min(current_width / self.original_window_width, current_height / self.original_window_height)

            # Calculate the new handle width based on the scaling factor
            new_handle_width = max(min(int(self.initial_handle_width * scaling_factor), self.initial_handle_width), 1)

            parent_splitter = self.parent()
            if isinstance(parent_splitter, QSplitter):
                current_handle_width = parent_splitter.handleWidth()  # Get handle width from parent splitter
                if new_handle_width != current_handle_width:  # Only set if there's a change
                    self.setHandleWidth(new_handle_width)
                    logger.debug(f"{self.identifier} splitter handle resized to {new_handle_width}px based on QMainWindow size")

    def _find_main_window(self):
        """
        Finds the QMainWindow parent of this widget, if any.

        Returns:
            QMainWindow or None: The QMainWindow parent or None if not found.
        """
        widget = self.parent()
        while widget:
            if isinstance(widget, QMainWindow):
                return widget
            widget = widget.parent()
        return None

    def setHandleWidth(self, width):
        """
        Set the handle width for the splitter.

        Args:
            width (int): The new width for the splitter handle.
        """
        if isinstance(self.parent(), QSplitter):
            self.parent().setHandleWidth(width)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press events on the splitter handle, forwarding the event to the parent if applicable.

        Args:
            event (QMouseEvent): The mouse event to handle.
        """
        try:
            parent = self.parent()
            logger.debug(f'{self.identifier} splitter handle mouse press event. Parent: {parent}')
            if self.identifier and parent:
                if hasattr(parent, 'handle_mousePressEvent'):
                    parent.handle_mousePressEvent(event, self)
                else:
                    logger.error(f'Parent does not have handle_mousePressEvent method. Parent: {parent}')
            else:
                logger.error(f'Parent is None or identifier is missing for {self.identifier}')
        except Exception as e:
            logger.error(f'Error in mousePressEvent for {self.identifier}: {e}')
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Overrides the default mouse move event to disable dragging the splitter.

        Args:
            event (QMouseEvent): The mouse event to handle.
        """
        logger.debug(f'{self.identifier} splitter handle mouse move event overridden to disable dragging')
        pass  # Disable dragging by overriding the event without implementation
