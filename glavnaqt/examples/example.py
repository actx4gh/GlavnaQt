# Ensure that the parent directory of 'core' is in sys.path
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from glavnaqt.core import logger
from glavnaqt.core import config
from glavnaqt.core.config_manager import all_configurations
from glavnaqt.core.config import UIConfiguration
from glavnaqt.ui.main_window import MainWindow
from glavnaqt.ui.status_bar_manager import StatusBarManager
from glavnaqt.ui.transitions import perform_transition

def schedule_transition(mainWin, config_i, config_j, delay):
    """Schedules a transition between two configurations with a delay."""
    QTimer.singleShot(delay, lambda: perform_transition(mainWin, config_i, config_j))


def cycle_configs(mainWin, configurations):
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
                ui_config_i = UIConfiguration(
                    font_face=configurations[i].get('font_face', 'Helvetica'),
                    font_size=configurations[i].get('font_size', 12),
                    splitter_handle_width=configurations[i].get('splitter_handle_width', 5),
                    window_size=configurations[i].get('window_size', (640, 480)),
                    window_position=configurations[i].get('window_position', (100, 100)),
                    enable_status_bar_manager=configurations[i].get('enable_status_bar_manager', False),
                    collapsible_sections=convert_to_dict_config(configurations[i])
                )

                ui_config_j = UIConfiguration(
                    font_face=configurations[j].get('font_face', 'Helvetica'),
                    font_size=configurations[j].get('font_size', 12),
                    splitter_handle_width=configurations[j].get('splitter_handle_width', 5),
                    window_size=configurations[j].get('window_size', (640, 480)),
                    window_position=configurations[j].get('window_position', (100, 100)),
                    enable_status_bar_manager=configurations[j].get('enable_status_bar_manager', False),
                    collapsible_sections=convert_to_dict_config(configurations[j])
                )

                schedule_transition(mainWin, ui_config_i, ui_config_j, index * transition_time)
                index += 1
                #if index >= 1:
                    #cyclequit = True
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

    # Argument parser to toggle cycling through configurations
    parser = argparse.ArgumentParser(description="Demo application for cycling through UI configurations.")
    parser.add_argument('--cycle-configs', action='store_true',
                        help="Cycle through all collapsible section configurations.")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Use the singleton config instance to configure the application
    config.config.font_face = "Helvetica"
    config.config.font_size = 13
    config.config.splitter_handle_width = 5
    config.config.window_size = (800, 600)
    config.config.window_position = (150, 150)
    config.config.enable_status_bar_manager = True
    config.config.update_collapsible_section('main_content', 'Main Content', config.ALIGN_CENTER)
    config.config.update_collapsible_section('top', 'Top Bar', config.ALIGN_CENTER)
    config.config.update_collapsible_section('bottom', 'Status Bar', config.ALIGN_CENTER)
    config.config.update_collapsible_section('left', 'Left Sidebar', config.ALIGN_CENTER)
    config.config.update_collapsible_section('right', 'Right Sidebar', config.ALIGN_CENTER)

    # Create and show the main window
    status_bar_manager = StatusBarManager()
    mainWin = MainWindow()
    mainWin.show()

    if args.cycle_configs:
        # If --cycle-configs is provided, cycle through all configurations
        configurations = all_configurations()
        dict_configurations = [convert_to_dict_config(config) for config in configurations]
        QTimer.singleShot(0, lambda: cycle_configs(mainWin,
                                                   dict_configurations))  # Start cycling configs after the main window shows up

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

