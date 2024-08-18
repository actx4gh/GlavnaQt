import logging

from PyQt6.QtCore import QTimer

logger = logging.getLogger(__name__)


def perform_transition(mainWin, start_config, end_config):
    """
    Performs a UI transition between two configurations with a delay.

    Args:
        mainWin (QMainWindow): The main window instance where the transition occurs.
        start_config (UIConfiguration): The initial configuration to apply.
        end_config (UIConfiguration): The final configuration to apply after a delay.
    """

    logger.debug(f'Applying start configuration: {start_config.replace_alignment_constants()}')

    # Check if the current UI state matches the start_config
    if mainWin.ui_config == start_config:
        logger.debug("Skipping redundant start_config application")
    else:
        mainWin.update_ui(start_config.collapsible_sections)

    QTimer.singleShot(5000, lambda: apply_end_config(mainWin, end_config))


def apply_end_config(mainWin, end_config):
    """
    Applies the end configuration after the delay and logs it.

    Args:
        mainWin (QMainWindow): The main window instance where the transition occurs.
        end_config (UIConfiguration): The final configuration to apply.
    """
    # Log the end configuration being applied
    logger.debug(f'Applying end configuration: {end_config.replace_alignment_constants()}')
    mainWin.update_ui(end_config.collapsible_sections)
