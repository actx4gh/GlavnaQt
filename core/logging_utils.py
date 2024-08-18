import logging

from PyQt6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


def log_widget_hierarchy(widget, level=0):
    """
    Logs the hierarchy and properties of widgets starting from the given widget.

    Args:
        widget (QWidget): The root widget to start logging from.
        level (int, optional): The indentation level for nested widgets. Defaults to 0.
    """
    indent = "    " * level
    width = widget.geometry().width()
    size_policy = widget.sizePolicy()
    size_hint = widget.sizeHint()

    logger.debug(f"{indent}Widget: {widget.objectName() or 'Unnamed'}, Type: {type(widget).__name__}, Width: {width}px")
    logger.debug(
        f"{indent}    SizePolicy: Horizontal: {size_policy.horizontalPolicy()}, Vertical: {size_policy.verticalPolicy()}")
    logger.debug(f"{indent}    SizeHint: {size_hint.width()}px x {size_hint.height()}px")

    if hasattr(widget, 'getContentsMargins'):
        left_margin, top_margin, right_margin, bottom_margin = widget.getContentsMargins()
        logger.debug(
            f"{indent}    Margins: Left: {left_margin}px, Right: {right_margin}px, Top: {top_margin}px, Bottom: {bottom_margin}px")
    else:
        logger.debug(f"{indent}    Margins: Not available for {type(widget).__name__}")

    for child in widget.findChildren(QWidget):
        log_widget_hierarchy(child, level + 1)
