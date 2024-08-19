import logging

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel

logger = logging.getLogger(__name__)


def get_qlabel(ui_instance, name):
    """
    Retrieves a QLabel by name from a given UI instance.

    Args:
        ui_instance (QWidget): The parent widget containing the QLabel.
        name (str): The object name of the QLabel to find.

    Returns:
        QLabel: The found QLabel, or None if not found.
    """
    return ui_instance.findChild(QLabel, name)


def apply_font(font_face, font_size, widget):
    font = QFont(font_face)
    font.setPixelSize(font_size)
    widget.setFont(font)
