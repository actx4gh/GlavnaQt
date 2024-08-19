import logging

from PyQt6.QtWidgets import QLabel

logger = logging.getLogger(__name__)


def initialize_geometries(ui_window):
    """
    Initializes and logs the geometries of key UI components.

    Args:
        ui_window (QMainWindow): The main window instance containing the UI components.
    """
    if ui_window.main_content_widget:
        ui_window.initial_main_content_width = ui_window.main_content_widget.width()
        logger.debug(f"Initial main content width: {ui_window.initial_main_content_width}px")

    if ui_window.left_splitter and ui_window.left_splitter.count() > 0:
        ui_window.initial_left_sidebar_width = ui_window.left_splitter.widget(0).width()
        logger.debug(f"Initial left sidebar width: {ui_window.initial_left_sidebar_width}px")

    if ui_window.right_splitter and ui_window.right_splitter.count() > 0:
        ui_window.initial_right_sidebar_width = ui_window.right_splitter.widget(1).width()
        logger.debug(f"Initial right sidebar width: {ui_window.initial_right_sidebar_width}px")

    top_bar = ui_window.findChild(QLabel, "top_bar")
    if top_bar:
        ui_window.initial_top_bar_height = top_bar.height()
        logger.debug(f"Initial top bar height: {ui_window.initial_top_bar_height}px")

    status_bar = ui_window.findChild(QLabel, "status_bar")
    if status_bar:
        ui_window.initial_status_bar_height = status_bar.height()
        logger.debug(f"Initial status bar height: {ui_window.initial_status_bar_height}px")
