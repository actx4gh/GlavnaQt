import logging
import time

from PyQt6.QtGui import QFontMetrics
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStatusBar, QSizePolicy

from glavnaqt.ui.font_scaling import calculate_scaling_factor
from glavnaqt.ui.helpers import apply_font

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

    # Adjusting bars and sidebars using the sectionwidget class vars
    top_bar_font_size = adjust_bar_height(ui_instance, "top", scaling_factor, log_required)
    status_bar_font_size = adjust_bar_height(ui_instance, "status", scaling_factor, log_required)
    left_sidebar_font_size = adjust_sidebar_width(ui_instance, "left", scaling_factor, log_required)
    right_sidebar_font_size = adjust_sidebar_width(ui_instance, "right", scaling_factor, log_required)

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


def adjust_bar_height(ui_instance, section_name, scaling_factor, log_required):
    splitter, bar = getattr(ui_instance, f'{section_name}_section')
    status_bar = None
    status_label = None
    padding_factor = 0.2
    if isinstance(bar, QStatusBar):  # Handling when StatusBarManager is used
        status_bar = ui_instance.status_bar_manager.status_bar
        status_label = ui_instance.status_bar_manager.status_label
        bar = status_label
        padding_factor = 0.4
    if bar is None:
        logger.debug(f"[{section_name}] Bar not found or not applicable.")
        return None

    # Calculate text height based on the font
    font_metrics = QFontMetrics(bar.font())
    text_height = font_metrics.height()

    if log_required:
        logging.debug(f"[{section_name}] Text height: {text_height}px")

    # Adjust widget height based on text height and dynamic padding
    adjust_widget_dimension(bar if not status_bar else status_bar, text_height, padding_factor=padding_factor, is_width=False,
                                            log_required=log_required)
    if status_bar:
        status_label.setFixedHeight(text_height)


    # Scale the font size to fit the window dimensions
    new_font_size = calculate_scaling_factor(ui_instance.width(), bar.text(), text_height,
                                             ui_instance.ui_config.font_face,
                                             max_font_size=ui_instance.ui_config.font_size, log_required=log_required)

    apply_font_size_to_widget(bar, new_font_size, log_required, section_name)

    # Adjust the splitter handle width for consistency
    adjust_splitter_handle_width(ui_instance, section_name, scaling_factor, log_required)

    return new_font_size


def adjust_sidebar_width(ui_instance, section_name, scaling_factor, log_required):
    """
    Adjusts the width of a sidebar based on the scaling factor.

    Args:
        ui_instance (QMainWindow): The main window instance.
        section_name (str): The section name
        scaling_factor (float): The scaling factor for adjustment.
        log_required (bool): Whether detailed logging is required.

    Returns:
        int: The new font size of the sidebar, or None if the sidebar is not found.
    """
    splitter, sidebar = getattr(ui_instance, f'{section_name}_section')
    if sidebar is None:
        logging.error(f"Sidebar {section_name} not found; skipping adjustment.")
        return None

    initial_width = getattr(ui_instance, f'initial_{section_name}_sidebar_width', None)
    if initial_width is None:
        logging.warning(f"No initial width found for {section_name}; skipping adjustment.")
        return None

    new_sidebar_width = int(initial_width * scaling_factor)

    if log_required:
        logging.debug(f"[{section_name}] New sidebar width after scaling: {new_sidebar_width}px")

    adjust_widget_dimension(sidebar, new_sidebar_width, padding_factor=0.1, is_width=True, log_required=log_required)

    adjust_splitter_handle_width(ui_instance, section_name, scaling_factor, log_required)

    new_font_size = calculate_scaling_factor(new_sidebar_width, sidebar.text(), new_sidebar_width,
                                             ui_instance.ui_config.font_face,
                                             max_font_size=ui_instance.ui_config.font_size, log_required=log_required)

    apply_font_size_to_widget(sidebar, new_font_size, log_required, section_name)

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
    _, main_content_widget = ui_instance.main_content_section
    if main_content_widget is None:
        logger.debug("[main_content] Main content widget not found.")
        return None

    try:
        if hasattr(main_content_widget, 'text') and callable(getattr(main_content_widget, 'text', None)):
            main_content_text_width = main_content_widget.fontMetrics().boundingRect(main_content_widget.text()).width()
            if log_required:
                logging.debug(f"[main_content] Text width: {main_content_text_width}px")
            return calculate_scaling_factor(main_content_widget.width(), main_content_widget.text(),
                                            main_content_widget.width(),
                                            ui_instance.ui_config.font_face,
                                            max_font_size=ui_instance.ui_config.font_size,
                                            log_required=log_required)
        else:
            logger.debug(f"[main_content] Widget {type(main_content_widget).__name__} does not have a text attribute.")
            # Skip font adjustment for non-text widgets
            return None
    except RuntimeError as e:
        logger.error(f"Error accessing main content widget: {e}")
        return None


def apply_font_size_to_widget(widget, font_size, log_required, section_name):
    """
    Applies the given font size to the widget and logs the change if required.

    Args:
        widget (QWidget): The widget to apply the font size to.
        font_size (int): The font size to apply.
        log_required (bool): Whether detailed logging is required.
        section_name (str): The section name (used for logging).
    """
    if widget is None:
        logger.error(f"[{section_name}] Widget is None, cannot apply font size.")
        return

    apply_font(widget.font(), font_size, widget)
    if log_required:
        logging.debug(f"[{section_name}] New font size: {font_size}px")


def adjust_splitter_handle_width(ui_instance, section_name, scaling_factor, log_required):
    """
    Adjusts the splitter handle width based on the scaling factor.

    Args:
        ui_instance (QMainWindow): The main window instance.
        section_name (str): The section name
        scaling_factor (float): The scaling factor for adjustment.
        log_required (bool): Whether detailed logging is required.
    """
    splitter, _ = getattr(ui_instance, f'{section_name}_section')
    if splitter:
        new_handle_width = max(min(int(ui_instance.ui_config.splitter_handle_width * scaling_factor),
                                   ui_instance.ui_config.splitter_handle_width), 1)
        splitter.setHandleWidth(new_handle_width)
        if log_required:
            logging.debug(f"[{section_name}] Scaled splitter handle width: {new_handle_width}px")


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

    for section_name in ["top", "status", "left", "right", "main_content"]:
        _, widget = getattr(ui_instance, f'{section_name}_section')
        if isinstance(widget, QStatusBar):
            widget = ui_instance.status_bar_manager.status_label
        if widget:
            apply_font_size_to_widget(widget, smallest_font_size, log_required, section_name)
