from PyQt6.QtGui import QFontMetrics, QFont

from glavnaqt.core import logger


def calculate_scaling_factor(parent_width, actual_text, initial_text_width, font_face, max_font_size, min_font_size=3,
                             log_required=False):
    """
    Calculates the appropriate font size scaling factor based on the parent width.

    Args:
        parent_width (int): The width of the parent widget.
        actual_text (str): The text to be displayed.
        initial_text_width (int): The initial width of the text with the default font size.
        font_face (str): The font family name to use.
        max_font_size (int): The maximum allowable font size.
        min_font_size (int, optional): The minimum allowable font size. Defaults to 3.
        log_required (bool, optional): If True, detailed logging is performed. Defaults to False.

    Returns:
        int: The calculated font size.
    """
    scaling_factor = parent_width / initial_text_width
    new_size = max_font_size * scaling_factor

    if new_size < min_font_size:
        new_size = min_font_size
    elif new_size > max_font_size:
        new_size = max_font_size

    if log_required:
        logger.debug(f"Initial calculated font size: {new_size}px")

    iteration_count = 0
    max_iterations = 50
    tolerance = 3

    last_size_adjustment_direction = None

    while iteration_count < max_iterations:
        font = QFont(font_face)
        font.setPixelSize(int(new_size))
        font_metrics = QFontMetrics(font)
        predicted_text_width = font_metrics.boundingRect(actual_text).width()

        if log_required:
            logger.debug(
                f"Iteration {iteration_count} - Font Size: {new_size}px, Predicted Text Width: {predicted_text_width}px")

        if abs(predicted_text_width - parent_width) <= tolerance:
            break

        if predicted_text_width > parent_width:
            if last_size_adjustment_direction == 'increase':
                break
            new_size -= 0.5
            last_size_adjustment_direction = 'decrease'
        else:
            if last_size_adjustment_direction == 'decrease':
                break
            new_size += 0.5
            last_size_adjustment_direction = 'increase'

        if new_size < min_font_size:
            new_size = min_font_size
            break
        elif new_size > max_font_size:
            new_size = max_font_size
            break

        iteration_count += 1

    if log_required:
        logger.debug(
            f"Final Font Size: {new_size}px, Final Predicted Width: {predicted_text_width}px, Parent Width: {parent_width}px")

    return int(new_size)
