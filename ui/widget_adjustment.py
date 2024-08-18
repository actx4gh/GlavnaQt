import logging
import time

from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QLabel

from ui.font_scaling import calculate_scaling_factor
from ui.helpers import get_qlabel, apply_font

logger = logging.getLogger(__name__)


def adjust_widget_dimension(widget, dimension, padding_factor, is_width=True, log_required=False):
    """
    Adjusts the width or height of a widget based on the calculated dimension and padding.

    Args:
        widget (QWidget): The widget to adjust.
        dimension (int): The base dimension to adjust from.
        padding_factor (float): The factor by which to increase the dimension.
        is_width (bool, optional): If True, adjusts width; otherwise, adjusts height. Defaults to True.
        log_required (bool, optional): If True, logs detailed adjustment information. Defaults to False.
    """
    padding = max(2, int(dimension * padding_factor))
    required_dimension = dimension + padding

    if is_width:
        widget.setFixedWidth(required_dimension)
        if log_required:
            logger.debug(
                f"Adjusted width to {required_dimension}px based on calculated text width with dynamic padding.")
    else:
        widget.setFixedHeight(required_dimension)
        if log_required:
            logger.debug(
                f"Adjusted height to {required_dimension}px based on calculated text height with dynamic padding.")


def adjust_font_and_widget_sizes(ui_instance):
    """
    Dynamically adjusts the font sizes, widths, and heights of widgets based on the window size.

    Args:
        ui_instance (QMainWindow): The main window instance containing the UI components.
    """
    current_time = time.time()
    log_required = should_log_adjustment(ui_instance, current_time)

    if log_required:
        ui_instance.last_resize_log_time = current_time

    window_width = ui_instance.width()
    scaling_factor = calculate_scaling_factor_based_on_window(ui_instance, window_width, log_required)

    # Adjusting bars and sidebars
    top_bar_font_size = adjust_bar_height(ui_instance, "top_bar", scaling_factor, log_required)
    status_bar_font_size = adjust_bar_height(ui_instance, "status_bar", scaling_factor, log_required)
    left_sidebar_font_size = adjust_sidebar_width(ui_instance, "left_sidebar", scaling_factor, log_required)
    right_sidebar_font_size = adjust_sidebar_width(ui_instance, "right_sidebar", scaling_factor, log_required)

    # Apply similar logic to the main content panel
    main_content_font_size = adjust_main_content_font_size(ui_instance, scaling_factor, log_required)

    # Apply the smallest font size across all widgets
    apply_smallest_font_size(ui_instance,
                             [top_bar_font_size, status_bar_font_size, left_sidebar_font_size, right_sidebar_font_size,
                              main_content_font_size], log_required)

    if log_required:
        logging.debug("Completed adjust_font_and_widget_sizes")


def should_log_adjustment(ui_instance, current_time):
    """
    Determines if logging is required for the adjustment process.

    Args:
        ui_instance (QMainWindow): The main window instance.
        current_time (float): The current time in seconds.

    Returns:
        bool: True if logging is required, otherwise False.
    """
    return not ui_instance.is_initialized or (
            current_time - ui_instance.last_resize_log_time > ui_instance.resize_log_threshold)


def calculate_scaling_factor_based_on_window(ui_instance, window_width, log_required):
    """
    Calculates the scaling factor based on the current window width.

    Args:
        ui_instance (QMainWindow): The main window instance.
        window_width (int): The current width of the window.
        log_required (bool): Whether detailed logging is required.

    Returns:
        float: The scaling factor based on the window width.
    """
    if log_required:
        logging.debug(f"Window width: {window_width}px")
    scaling_factor = window_width / ui_instance.ui_config.window_size[0]
    if log_required:
        logging.debug(f"Scaling factor: {scaling_factor}")
    return scaling_factor


def adjust_bar_height(ui_instance, label_name, scaling_factor, log_required):
    """
    Adjusts the height of a bar (top or status) based on the scaling factor.

    Args:
        ui_instance (QMainWindow): The main window instance.
        label_name (str): The name of the QLabel representing the bar.
        scaling_factor (float): The scaling factor for adjustment.
        log_required (bool): Whether detailed logging is required.

    Returns:
        int: The new font size of the bar, or None if the bar is not found.
    """
    bar = get_qlabel(ui_instance, label_name)
    if bar is None:
        return None

    font_metrics = QFontMetrics(bar.font())
    text_height = font_metrics.height()

    if log_required:
        logging.debug(f"[{label_name}] Text height: {text_height}px")

    adjust_widget_dimension(bar, text_height, padding_factor=0.1, is_width=False, log_required=log_required)

    new_font_size = calculate_scaling_factor(ui_instance.width(), bar.text(), text_height,
                                             ui_instance.ui_config.font_face,
                                             max_font_size=ui_instance.ui_config.font_size, log_required=log_required)

    apply_font_size_to_widget(bar, new_font_size, log_required, label_name)

    adjust_splitter_handle_width(ui_instance, label_name, scaling_factor, log_required)

    return new_font_size


def adjust_sidebar_width(ui_instance, label_name, scaling_factor, log_required):
    """
    Adjusts the width of a sidebar based on the scaling factor.

    Args:
        ui_instance (QMainWindow): The main window instance.
        label_name (str): The name of the QLabel representing the sidebar.
        scaling_factor (float): The scaling factor for adjustment.
        log_required (bool): Whether detailed logging is required.

    Returns:
        int: The new font size of the sidebar, or None if the sidebar is not found.
    """
    bar = get_qlabel(ui_instance, label_name)
    if bar is None:
        logging.error(f"Label {label_name} not found; skipping adjustment.")
        return None

    initial_width = get_initial_sidebar_width(ui_instance, label_name)
    if initial_width is None:
        logging.warning(f"No initial width found for {label_name}; skipping adjustment.")
        return None

    new_sidebar_width = int(initial_width * scaling_factor)

    if log_required:
        logging.debug(f"[{label_name}] New sidebar width after scaling: {new_sidebar_width}px")

    adjust_widget_dimension(bar, new_sidebar_width, padding_factor=0.1, is_width=True, log_required=log_required)

    adjust_splitter_handle_width(ui_instance, label_name, scaling_factor, log_required)

    new_font_size = calculate_scaling_factor(new_sidebar_width, bar.text(), new_sidebar_width,
                                             ui_instance.ui_config.font_face,
                                             max_font_size=ui_instance.ui_config.font_size, log_required=log_required)

    apply_font_size_to_widget(bar, new_font_size, log_required, label_name)

    return new_font_size


def adjust_main_content_font_size(ui_instance, scaling_factor, log_required):
    """
    Adjusts the font size of the main content widget based on the scaling factor.

    Args:
        ui_instance (QMainWindow): The main window instance.
        scaling_factor (float): The scaling factor for adjustment.
        log_required (bool): Whether detailed logging is required.

    Returns:
        int: The new font size for the main content widget.
    """
    main_content_widget = ui_instance.main_content_widget
    main_content_text_width = main_content_widget.fontMetrics().boundingRect(main_content_widget.text()).width()

    if log_required:
        logging.debug(f"[main_content] Text width: {main_content_text_width}px")

    return calculate_scaling_factor(main_content_widget.width(), main_content_widget.text(),
                                    main_content_widget.width(),
                                    ui_instance.ui_config.font_face, max_font_size=ui_instance.ui_config.font_size,
                                    log_required=log_required)


def apply_font_size_to_widget(widget, font_size, log_required, label_name):
    """
    Applies the given font size to the widget and logs the change if required.

    Args:
        widget (QWidget): The widget to apply the font size to.
        font_size (int): The font size to apply.
        log_required (bool): Whether detailed logging is required.
        label_name (str): The name of the QLabel (used for logging).
    """
    apply_font(widget.font(), font_size, widget)
    if log_required:
        logging.debug(f"[{label_name}] New font size: {font_size}px")


def adjust_splitter_handle_width(ui_instance, label_name, scaling_factor, log_required):
    """
    Adjusts the splitter handle width based on the scaling factor.

    Args:
        ui_instance (QMainWindow): The main window instance.
        label_name (str): The name of the QLabel representing the sidebar or bar.
        scaling_factor (float): The scaling factor for adjustment.
        log_required (bool): Whether detailed logging is required.
    """
    if label_name in ["top_bar", "status_bar", "left_sidebar", "right_sidebar"]:
        splitter_handle = (ui_instance.top_splitter if label_name == "top_bar" else
                           ui_instance.bottom_splitter if label_name == "status_bar" else
                           ui_instance.left_splitter if label_name == "left_sidebar" else
                           ui_instance.right_splitter)
        if splitter_handle:
            new_handle_width = max(min(int(ui_instance.ui_config.splitter_handle_width * scaling_factor),
                                       ui_instance.ui_config.splitter_handle_width), 1)
            splitter_handle.setHandleWidth(new_handle_width)
            if log_required:
                logging.debug(f"[{label_name}] Scaled splitter handle width: {new_handle_width}px")


def get_initial_sidebar_width(ui_instance, label_name):
    """
    Retrieves the initial width of the sidebar based on its label name.

    Args:
        ui_instance (QMainWindow): The main window instance.
        label_name (str): The name of the sidebar (e.g., "left_sidebar" or "right_sidebar").

    Returns:
        int: The initial width of the sidebar or None if the sidebar does not exist.
    """
    if label_name == "left_sidebar":
        return getattr(ui_instance, 'initial_left_sidebar_width', None)
    elif label_name == "right_sidebar":
        return getattr(ui_instance, 'initial_right_sidebar_width', None)
    return None


def apply_smallest_font_size(ui_instance, font_sizes, log_required):
    """
    Applies the smallest font size among the provided sizes to all relevant widgets.

    Args:
        ui_instance (QMainWindow): The main window instance.
        font_sizes (list of int): The list of font sizes to consider.
        log_required (bool): Whether detailed logging is required.
    """
    smallest_font_size = min(filter(None, font_sizes)) if any(font_sizes) else ui_instance.ui_config.font_size
    if log_required:
        logging.debug(f"Smallest font size: {smallest_font_size}px")

    for widget_name in ["top_bar", "status_bar", "left_sidebar", "right_sidebar", "main_content"]:
        widget = ui_instance.findChild(QLabel, widget_name)
        if widget:
            apply_font_size_to_widget(widget, smallest_font_size, log_required, widget_name)
