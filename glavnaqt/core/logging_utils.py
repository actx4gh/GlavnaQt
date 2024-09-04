from glavnaqt.core import logger
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSplitter, QLabel



def log_widget_hierarchy(widget, level=0, visited=None, visual_mapping=True):
    """
    Logs the hierarchy and properties of widgets starting from the given widget.
    Optionally logs the hierarchy in a visual mapping format.

    Args:
        widget (QWidget): The root widget to start logging from.
        level (int, optional): The indentation level for nested widgets. Defaults to 0.
        visited (set, optional): Set of widget IDs that have already been logged. Defaults to None.
        visual_mapping (bool, optional): Whether to log the hierarchy in a visual mapping format. Defaults to False.
    """
    if visited is None:
        visited = set()

    widget_id = id(widget)

    if widget_id in visited:
        return  # Skip already logged widgets

    visited.add(widget_id)

    indent = "    " * level

    # Determine visibility status
    visibility_status = "Visible" if widget.isVisible() else "Hidden"

    if visual_mapping:
        # If visual mapping is enabled, log hierarchy in a tree-like structure with minimal info and visibility
        logger.debug(f"{indent}{'|   ' * (level-1)}{'└── ' if level > 0 else ''}{widget.objectName() or 'Unnamed'} "
                     f"(ID: {hex(widget_id)}) [{visibility_status}]")
    else:
        # Log detailed widget information
        width = widget.geometry().width()
        height = widget.geometry().height()
        size_policy = widget.sizePolicy()
        size_hint = widget.sizeHint()

        logger.debug(f"{indent}Widget: {widget.objectName() or 'Unnamed'}, Type: {type(widget).__name__}, "
                     f"Width: {width}px, Height: {height}px, ID: {hex(widget_id)}, Visibility: {visibility_status}")
        logger.debug(f"{indent}    SizePolicy: Horizontal: {size_policy.horizontalPolicy()}, "
                     f"Vertical: {size_policy.verticalPolicy()}")
        logger.debug(f"{indent}    SizeHint: {size_hint.width()}px x {size_hint.height()}px")

        # Log margins if available
        if hasattr(widget, 'getContentsMargins'):
            left_margin, top_margin, right_margin, bottom_margin = widget.getContentsMargins()
            logger.debug(f"{indent}    Margins: Left: {left_margin}px, Right: {right_margin}px, "
                         f"Top: {top_margin}px, Bottom: {bottom_margin}px")
        else:
            logger.debug(f"{indent}    Margins: Not available for {type(widget).__name__}")

        # Log padding using Qt's layout method, if widget has a layout
        if widget.layout() is not None:
            layout = widget.layout()
            margins = layout.contentsMargins()
            logger.debug(f"{indent}    Layout Padding: Left: {margins.left()}px, Right: {margins.right()}px, "
                         f"Top: {margins.top()}px, Bottom: {margins.bottom()}px")
        else:
            logger.debug(f"{indent}    Padding: Not available for {type(widget).__name__}")

        # Check for alignment
        if isinstance(widget, QLabel) or hasattr(widget, 'alignment'):
            alignment = widget.alignment()
            alignment_str = alignment_to_string(alignment)
            logger.debug(f"{indent}    Alignment: {alignment_str}")

        # Log text if widget is a QLabel
        if isinstance(widget, QLabel):
            logger.debug(f"{indent}    Text: {widget.text()}")

        # Check for layout information
        if widget.layout() is not None:
            layout = widget.layout()
            margins = layout.contentsMargins()
            logger.debug(f"{indent}    Layout: {type(layout).__name__}, Spacing: {layout.spacing()}, "
                         f"ContentsMargins: Left: {margins.left()}px, Right: {margins.right()}px, "
                         f"Top: {margins.top()}px, Bottom: {margins.bottom()}px")

        # Check for splitters
        if isinstance(widget, QSplitter):
            orientation = "Horizontal" if widget.orientation() == Qt.Orientation.Horizontal else "Vertical"
            logger.debug(f"{indent}    Splitter Orientation: {orientation}")

    # Recursively log child widgets in the correct order
    if widget.layout() is not None:
        for i in range(widget.layout().count()):
            child = widget.layout().itemAt(i).widget()
            if child is not None:
                log_widget_hierarchy(child, level + 1, visited, visual_mapping)
    else:
        for child in widget.findChildren(QWidget):
            log_widget_hierarchy(child, level + 1, visited, visual_mapping)



def alignment_to_string(alignment):
    """
    Converts the alignment flag to a human-readable string.
    """
    alignments = []
    if alignment & Qt.AlignmentFlag.AlignLeft:
        alignments.append("AlignLeft")
    if alignment & Qt.AlignmentFlag.AlignRight:
        alignments.append("AlignRight")
    if alignment & Qt.AlignmentFlag.AlignHCenter:
        alignments.append("AlignHCenter")
    if alignment & Qt.AlignmentFlag.AlignTop:
        alignments.append("AlignTop")
    if alignment & Qt.AlignmentFlag.AlignBottom:
        alignments.append("AlignBottom")
    if alignment & Qt.AlignmentFlag.AlignVCenter:
        alignments.append("AlignVCenter")
    if alignment & Qt.AlignmentFlag.AlignCenter:
        alignments.append("AlignCenter")

    return " | ".join(alignments) if alignments else "AlignNone"
