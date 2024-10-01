import time

from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QStatusBar

from glavnaqt.core import logger
from glavnaqt.ui.font_scaling import calculate_scaling_factor
from glavnaqt.ui.helpers import apply_font


class WidgetAdjuster:
    def __init__(self, layout_manager):
        self.scaling_factor = None
        self.layout_manager = layout_manager

    def adjust_font_and_widget_sizes(self, original_window_width, font_face, font_size):
        current_time = time.time()
        log_required = self._should_log_adjustment(self.layout_manager, current_time)
        top_bar_font_size = None
        status_bar_font_size = None
        left_sidebar_font_size = None
        right_sidebar_font_size = None
        if log_required:
            self.layout_manager.last_resize_log_time = current_time

        current_window_width = self.layout_manager.get_central_widget().width()
        self.scaling_factor = self._calculate_scaling_factor_based_on_window(original_window_width,
                                                                             current_window_width,
                                                                             log_required)

        if "top" in self.layout_manager.current_config.collapsible_sections:
            top_bar_font_size = self._adjust_bar_height("top", log_required, font_face, font_size)
        if "bottom" in self.layout_manager.current_config.collapsible_sections:
            status_bar_font_size = self._adjust_bar_height("bottom", log_required, font_face, font_size)
        if "left" in self.layout_manager.current_config.collapsible_sections:
            left_sidebar_font_size = self._adjust_sidebar_width("left", log_required, font_face, font_size)
        if "right" in self.layout_manager.current_config.collapsible_sections:
            right_sidebar_font_size = self._adjust_sidebar_width("right", log_required, font_face, font_size)

        # Apply similar logic to the main content panel
        main_content_font_size = self._adjust_main_content_font_size(log_required, font_face,
                                                                     font_size)

        # Apply the smallest font size across all widgets
        self._apply_smallest_font_size([top_bar_font_size, status_bar_font_size, left_sidebar_font_size,
                                        right_sidebar_font_size,
                                        main_content_font_size], log_required)

    def _adjust_widget_dimension(self, widget, dimension, padding_factor, is_width=True, log_required=False):
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

    def _should_log_adjustment(self, layout_manager, current_time):
        return not layout_manager.is_initialized or (
                current_time - layout_manager.last_resize_log_time > layout_manager.resize_log_threshold)

    def _calculate_scaling_factor_based_on_window(self, original_window_width, current_window_width, log_required):
        if log_required:
            logger.debug(
                f"Original window width: {original_window_width}px, Current window width: {current_window_width}")
        scaling_factor = current_window_width / original_window_width
        if log_required:
            logger.debug(f"Scaling factor: {scaling_factor}")
        return scaling_factor

    def set_bar_height_to_text_height(self, primary, status_bar=None, status_label=None):
        # Calculate text height based on the font
        font_metrics = QFontMetrics(primary.font())
        text_height = font_metrics.height()
        if status_bar:
            padding_factor = 0.4
        else:
            padding_factor = 0.2
        self._adjust_widget_dimension(status_bar or primary, text_height, padding_factor=padding_factor,
                                      is_width=False)
        if status_bar:
            status_label.setFixedHeight(text_height)
        return text_height

    def get_widgets_for_section(self, section_name):
        status_bar = status_label = None
        primary = self.layout_manager.current_widgets[f"{section_name}_widget"]
        if isinstance(primary, QStatusBar):
            status_bar = primary
            primary = status_label = self.layout_manager.current_widgets["status_label"]
        widgets = {'primary': primary, 'status_bar': status_bar, 'status_label': status_label}
        return widgets

    def _adjust_bar_height(self, section_name, log_required=False, font_face=None, max_font_size=None):
        new_font_size = None
        widgets = self.get_widgets_for_section(section_name)
        primary, status_bar, status_label = widgets.values()
        if primary is None:
            return None

        text_height = self.set_bar_height_to_text_height(primary, status_bar, status_label)
        # Calculate text height based on the font

        if max_font_size:
            new_font_size = self._calculate_new_font_size(section_name, primary, text_height, font_face, max_font_size,
                                                          log_required)
        if new_font_size:
            return new_font_size

    def _calculate_new_font_size(self, section_name, bar, text_height, font_face, max_font_size, log_required):
        # Scale the font size to fit the window dimensions
        new_font_size = calculate_scaling_factor(self.layout_manager.get_central_widget().width(), bar.text(),
                                                 text_height,
                                                 font_face,
                                                 max_font_size=max_font_size,
                                                 log_required=log_required)

        self._apply_font_size_to_widget(bar, new_font_size, log_required, section_name)

        return new_font_size

    def _adjust_sidebar_width(self, section_name, log_required, font_face, font_size):
        widgets = self.get_widgets_for_section(section_name)
        primary, status_bar, status_label = widgets.values()
        if primary is None:
            return None

        initial_width = getattr(self.layout_manager, f'initial_{section_name}_widget_width', None)
        if initial_width is None:
            return None

        new_sidebar_width = int(initial_width * self.scaling_factor)
        new_sidebar_width = min(new_sidebar_width, initial_width)

        if log_required:
            logger.debug(f"[{section_name}] New sidebar width after scaling: {new_sidebar_width}px")

        if new_sidebar_width != initial_width:
            self._adjust_widget_dimension(primary, new_sidebar_width, padding_factor=0.1, is_width=True,
                                          log_required=log_required)

        new_font_size = calculate_scaling_factor(new_sidebar_width, primary.text(), new_sidebar_width, font_face,
                                                 font_size,
                                                 log_required=log_required)

        self._apply_font_size_to_widget(primary, new_font_size, log_required, section_name)

        return new_font_size

    def _adjust_main_content_font_size(self, log_required, font_face, font_size):
        main_content_widget = self.layout_manager.current_widgets["main_content_widget"]
        if main_content_widget is None:
            logger.debug("[main_content] Main content widget not found.")
            return None

        try:
            if hasattr(main_content_widget, 'text') and callable(getattr(main_content_widget, 'text', None)):
                main_content_text_width = main_content_widget.fontMetrics().boundingRect(
                    main_content_widget.text()).width()
                if log_required:
                    logger.debug(f"[main_content] Text width: {main_content_text_width}px")
                return calculate_scaling_factor(main_content_widget.width(), main_content_widget.text(),
                                                main_content_widget.width(), font_face, font_size,
                                                log_required=log_required)
            else:
                # Skip font adjustment for non-text widgets
                return None
        except RuntimeError as e:
            logger.error(f"Error accessing main content widget: {e}")
            return None

    def _apply_font_size_to_widget(self, widget, font_size, log_required, section_name):
        if widget is None:
            logger.error(f"[{section_name}] Widget is None, cannot apply font size.")
            return

        # Check if the current font size is different from the desired font size
        current_font_size = widget.font().pixelSize()
        if current_font_size != font_size:
            apply_font(widget.font(), font_size, widget)
            if section_name in ("bottom", "top"):
                self._adjust_bar_height(section_name, log_required)

    def _apply_smallest_font_size(self, font_sizes, log_required):
        smallest_font_size = min(filter(None, font_sizes)) if any(
            font_sizes) else self.layout_manager.current_config.font_size

        for section_name in ["top", "bottom", "left", "right", "main_content"]:
            widget = self.layout_manager.current_widgets.get(f'{section_name}_widget')
            if isinstance(widget, QStatusBar):
                widget = self.layout_manager.current_widgets.get("status_label")
            if widget:
                self._apply_font_size_to_widget(widget, smallest_font_size, log_required, section_name)
