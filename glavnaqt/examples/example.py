# Ensure that the parent directory of 'core' is in sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse
import logging

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from glavnaqt.core.logging_utils import log_widget_hierarchy
from glavnaqt.core.config import UIConfiguration  # Updated to directly import the class
from glavnaqt.core.config_manager import all_configurations
from glavnaqt.ui.main_window import MainWindow
from glavnaqt.ui.transitions import perform_transition

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def schedule_transition(mainWin, configurations, i, j, delay):
    # Assuming configurations[i] and configurations[j] are instances of UIConfiguration
    QTimer.singleShot(delay, lambda: perform_transition(mainWin, configurations[i], configurations[j]))


def cycle_configs(mainWin, configurations):
    total_configs = len(configurations)
    transition_time = 10000  # 10 seconds total for each transition
    index = 0
    for i in range(total_configs):
        for j in range(total_configs):
            if i != j:  # Skip self-transitions
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

                schedule_transition(mainWin, [ui_config_i, ui_config_j], 0, 1, index * transition_time)
                index += 1


def convert_to_dict_config(config_list):
    """
    Converts a list of section names into a UI configuration dictionary.

    Args:
        config_list (list): List of section names to include in the configuration.

    Returns:
        dict: A dictionary suitable for initializing a UIConfiguration instance.
    """
    # Default configuration with all sections and additional UI properties
    default_config = {
        "top": {"text": "Top Bar", "alignment": UIConfiguration.ALIGN_CENTER},
        "bottom": {"text": "Status Bar", "alignment": UIConfiguration.ALIGN_CENTER},
        "left": {"text": "Left Sidebar", "alignment": UIConfiguration.ALIGN_CENTER},
        "right": {"text": "Right Sidebar", "alignment": UIConfiguration.ALIGN_CENTER},
        "main_content": {"text": "Main Content", "alignment": UIConfiguration.ALIGN_CENTER}
    }

    # UI properties to ensure are always present
    ui_properties = {
        "font_face": "Helvetica",
        "font_size": 13,
        "splitter_handle_width": 5,
        "window_size": (1024, 768),
        "window_position": (150, 150),
        "enable_status_bar_manager": False,
    }

    # Filter out sections that are not in the provided config_list
    filtered_sections = {section: default_config[section] for section in config_list if section in default_config}

    # Always include "main_content"
    filtered_sections["main_content"] = default_config["main_content"]

    # Add UI properties to the configuration
    filtered_sections.update(ui_properties)

    return filtered_sections


if __name__ == '__main__':

    logging.debug('Starting application')

    # Argument parser to toggle cycling through configurations
    parser = argparse.ArgumentParser(description="Demo application for cycling through UI configurations.")
    parser.add_argument('--cycle-configs', action='store_true',
                        help="Cycle through all collapsible section configurations.")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Create a UIConfiguration instance with the default configuration
    ui_config = UIConfiguration(
        font_face="Helvetica",
        font_size=13,
        splitter_handle_width=5,
        window_size=(800, 600),
        window_position=(150, 150),
        enable_status_bar_manager=True,
        collapsible_sections={
            'main_content': {'text': 'Main Content', 'alignment': UIConfiguration.ALIGN_CENTER}
        }
    )

    # Optionally update some sections
    ui_config.update_collapsible_section('top', 'Top Bar', UIConfiguration.ALIGN_CENTER)
    ui_config.update_collapsible_section('bottom', 'Status Bar', UIConfiguration.ALIGN_CENTER)
    ui_config.update_collapsible_section('left', 'Left Sidebar', UIConfiguration.ALIGN_CENTER)
    ui_config.update_collapsible_section('right', 'Right Sidebar', UIConfiguration.ALIGN_CENTER)

    # Create and show the main window
    mainWin = MainWindow(ui_config)
    mainWin.show()

    if args.cycle_configs:
        # If --cycle-configs is provided, cycle through all configurations
        configurations = all_configurations()
        dict_configurations = [convert_to_dict_config(config) for config in configurations]
        QTimer.singleShot(0, lambda: cycle_configs(mainWin,
                                                   dict_configurations))  # Start cycling configs after the main window shows up

    sys.exit(app.exec())
