import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from glavnaqt.core.config import UIConfiguration
from glavnaqt.core import logger
from glavnaqt.core.config_manager import all_configurations
from glavnaqt.core.thread_manager import ThreadManager
from glavnaqt.ui.main_window import MainWindow
from glavnaqt.ui.status_bar_manager import StatusBarManager
from glavnaqt.ui.transitions import perform_transition

config = UIConfiguration.get_instance()
def schedule_transition(main_window, config_i, config_j, delay):
    """Schedules a transition between two configurations with a delay."""
    QTimer.singleShot(delay, lambda: perform_transition(main_window, config_i, config_j))


def cycle_configs(main_window, configurations):
    """Cycles through all configurations to apply them to the main window."""
    total_configs = len(configurations)
    transition_time = 10000  # 10 seconds total for each transition
    index = 0
    cyclequit = False
    for i in range(total_configs):
        if cyclequit:
            break
        for j in range(total_configs):
            if i != j:  # Skip self-transitions
                # Create separate configuration instances
                config.collapsible_sections = convert_to_dict_config(configurations[i])
                ui_config_i = config.copy()

                config.collapsible_sections = convert_to_dict_config(configurations[j])
                ui_config_j = config.copy()

                schedule_transition(main_window, ui_config_i, ui_config_j, index * transition_time)
                index += 1
                # if index >= 1:
                # cyclequit = True
                # break


def convert_to_dict_config(config_list):
    """Converts a list of section names into a UI configuration dictionary."""
    # Default configuration with all sections and additional UI properties
    default_config = {
        "top": {"text": "Top Bar", "alignment": config.ALIGN_CENTER},
        "bottom": {"text": "Status Bar", "alignment": config.ALIGN_CENTER},
        "left": {"text": "Left Sidebar", "alignment": config.ALIGN_CENTER},
        "right": {"text": "Right Sidebar", "alignment": config.ALIGN_CENTER},
        "main_content": {"text": "Main Content", "alignment": config.ALIGN_CENTER}
    }

    # Filter out sections that are not in the provided config_list
    filtered_sections = {section: default_config[section] for section in config_list if section in default_config}

    # Always include "main_content"
    filtered_sections["main_content"] = default_config["main_content"]

    return filtered_sections


def main():
    logger.debug('Starting application')

    app = QApplication(sys.argv)

    # Access values directly from the config object
    log_level = config.log_level
    cycle_configs_enabled = config.cycle_configs  # Check if cycling configs is enabled

    # Create and show the main window
    thread_manager = ThreadManager()
    _ = StatusBarManager(thread_manager=thread_manager)
    main_window = MainWindow(thread_manager=thread_manager)
    main_window.show()

    if cycle_configs_enabled:
        # If --cycle-configs is provided, cycle through all configurations
        configurations = all_configurations()
        cycle_configs(main_window, configurations)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
