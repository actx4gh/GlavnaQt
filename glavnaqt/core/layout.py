import logging

logger = logging.getLogger(__name__)


def initialize_geometries(ui_window):
    """
    Initializes and logs the geometries of key UI components.

    Args:
        ui_window (QMainWindow): The main window instance containing the UI components.
    """
    # Access main content widget from the section_mapj
    _, main_content_widget = ui_window.main_content_section
    if main_content_widget:
        ui_window.initial_main_content_width = main_content_widget.width()
        logger.debug(f"Initial main content width: {ui_window.initial_main_content_width}px")

    # Access left sidebar and main content from the left splitter in the section_map
    left_splitter, left_sidebar = ui_window.left_section
    if left_sidebar and left_splitter and left_splitter.count() > 0:
        ui_window.initial_left_sidebar_width = left_sidebar.width()
        logger.debug(f"Initial left sidebar width: {ui_window.initial_left_sidebar_width}px")

    # Access right sidebar and main content from the right splitter in the section_map
    right_splitter, right_sidebar = ui_window.right_section
    if right_sidebar and right_splitter and right_splitter.count() > 1:
        ui_window.initial_right_sidebar_width = right_sidebar.width()
        logger.debug(f"Initial right sidebar width: {ui_window.initial_right_sidebar_width}px")

    # Access top bar from the section_map
    _, top_bar = ui_window.top_section
    if top_bar:
        ui_window.initial_top_bar_height = top_bar.height()
        logger.debug(f"Initial top bar height: {ui_window.initial_top_bar_height}px")

    # Access status bar from the section_map
    _, status_bar = ui_window.status_section
    if status_bar:
        ui_window.initial_status_bar_height = status_bar.height()
        logger.debug(f"Initial status bar height: {ui_window.initial_status_bar_height}px")
