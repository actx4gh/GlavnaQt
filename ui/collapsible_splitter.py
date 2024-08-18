import logging
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QSplitter
from ui.splitter_handle import CollapsibleSplitterHandle

logger = logging.getLogger(__name__)

class CollapsibleSplitter(QSplitter):
    """
    A custom splitter widget that can collapse and expand sections based on user interaction.

    Attributes:
        is_collapsed (bool): Indicates whether the splitter is currently collapsed.
        identifier (str): A unique identifier for the splitter, used for logging and identifying splitters.
    """

    def __init__(self, orientation, parent=None, identifier="", handle_width=5):
        """
        Initializes the CollapsibleSplitter with the specified orientation and handle width.

        Args:
            orientation (Qt.Orientation): The orientation of the splitter (horizontal or vertical).
            parent (QWidget, optional): The parent widget of the splitter. Defaults to None.
            identifier (str, optional): A unique identifier for the splitter. Defaults to an empty string.
            handle_width (int, optional): The width of the splitter handle in pixels. Defaults to 5.
        """
        logger.debug(f'Initializing CollapsibleSplitter {identifier}')
        super().__init__(orientation, parent)
        self.setHandleWidth(handle_width)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: transparent; padding: 0px; margin: 0px;")
        self.splitterMoved.connect(self.on_splitter_moved)
        self.is_collapsed = False
        self.identifier = identifier
        logger.debug(f'Splitter {identifier} initialized with orientation {orientation}')
        logger.debug(f'Current stylesheet for {identifier}: {self.styleSheet()}')

    def adjust_handle_width(self, scaling_factor):
        """
        Dynamically adjusts the handle width based on a scaling factor.

        Args:
            scaling_factor (float): The factor by which to scale the handle width.
        """
        new_width = max(1, int(5 * scaling_factor))  # Scale from the base width of 5
        logger.debug(f'Adjusting handle width to {new_width} for {self.identifier}')
        self.setHandleWidth(new_width)

    def createHandle(self):
        """
        Creates and returns a custom handle for the splitter.

        Returns:
            CollapsibleSplitterHandle: The custom handle for the splitter.
        """
        logger.debug(f'Creating custom splitter handle for {self.identifier}')
        return CollapsibleSplitterHandle(self.orientation(), self, self.identifier)

    def handle_mousePressEvent(self, event: QMouseEvent, handle):
        """
        Handles mouse press events on the splitter handle, collapsing or expanding the splitter.

        Args:
            event (QMouseEvent): The mouse event to handle.
            handle (CollapsibleSplitterHandle): The splitter handle that was pressed.
        """
        try:
            logger.debug(f'Handling mouse press event for {self.identifier}: {event}')
            handle_index = self.indexOf(handle)
            logger.debug(f'{self.identifier} Handle index: {handle_index}')

            if handle_index == 1 and event.button() == Qt.MouseButton.LeftButton:
                if not self.is_collapsed:
                    self.collapse_splitter()
                else:
                    self.expand_splitter()
        except Exception as e:
            logger.error(f'Error handling mouse press event in {self.identifier}: {e}')

    def collapse_splitter(self):
        """
        Collapses the splitter based on its identifier.
        """
        collapse_sizes = {
            "top": [0, 1],
            "bottom": [1, 0],
            "left": [0, 1],
            "right": [1, 0],
        }
        if self.identifier in collapse_sizes:
            self.setSizes(collapse_sizes[self.identifier])
            self.is_collapsed = True
            logger.debug(f'{self.identifier} collapsed')

    def expand_splitter(self):
        """
        Expands the splitter to its default size.
        """
        self.setSizes([1, 1])
        self.is_collapsed = False
        logger.debug(f'{self.identifier} expanded')

    def on_splitter_moved(self, pos, index):
        """
        Called when the splitter is moved by the user. Adjusts the parent layout if necessary.

        Args:
            pos (int): The new position of the splitter.
            index (int): The index of the splitter handle that was moved.
        """
        logger.debug(f'{self.identifier} Splitter moved to position: {pos} at index: {index}')
        if self.parent():
            self.parent().adjust_layout()  # Trigger a layout adjustment in the parent (MainWindow)
