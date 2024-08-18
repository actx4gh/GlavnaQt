import logging
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QCursor
from PyQt6.QtWidgets import QSplitterHandle

logger = logging.getLogger(__name__)

class CollapsibleSplitterHandle(QSplitterHandle):
    """
    A custom handle for a splitter that supports collapsing and expanding sections.

    Attributes:
        identifier (str): A unique identifier for the splitter handle, used for logging and identifying handles.
    """

    def __init__(self, orientation, parent, identifier=None):
        """
        Initializes the custom splitter handle with the specified orientation and parent.

        Args:
            orientation (Qt.Orientation): The orientation of the splitter (horizontal or vertical).
            parent (QWidget): The parent widget of the handle.
            identifier (str, optional): A unique identifier for the splitter handle. Defaults to None.
        """
        super().__init__(orientation, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: black; padding: 0px; margin: 0px")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.identifier = identifier
        logger.debug(f'Custom splitter handle initialized for {identifier}')

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
