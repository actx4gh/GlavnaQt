from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QSizePolicy, QFrame

# Constants for common size policies
EXPANDING_FIXED = (QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
FIXED_EXPANDING = (QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
EXPANDING_EXPANDING = (QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
FIXED_FIXED = (QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


class PanelLabel(QLabel):
    """
    A QLabel subclass for creating labeled panels with custom styling and size policies.

    Args:
        text (str): The text to display on the label.
        name (str): The object name for the label (useful for styling and identification).
        size_policy (tuple): A tuple containing the QSizePolicy for the horizontal and vertical dimensions.
        font_name (str, optional): The font family to use. Defaults to "Helvetica".
        font_size (int, optional): The font size in points. Defaults to 12.
        alignment (Qt.AlignmentFlag, optional): The alignment of the text within the label. Defaults to Qt.AlignmentFlag.AlignCenter.
        frame_shape (QFrame.Shape, optional): The shape of the frame surrounding the label. Defaults to QFrame.Shape.NoFrame.
    """

    def __init__(self, text: str, name: str, size_policy: tuple, font_name="Helvetica", font_size=12,
                 alignment=Qt.AlignmentFlag.AlignCenter, frame_shape=QFrame.Shape.NoFrame):
        super().__init__(text)
        self.setObjectName(name)
        self.setFont(QFont(font_name, font_size))
        self.setAlignment(alignment)
        self.setFrameShape(frame_shape)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("padding: 0px; margin: 0px;")
        self.setSizePolicy(size_policy[0], size_policy[1])
