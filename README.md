
# GlavnaQt

**GlavnaQt** is a Qt-based GUI library written in Python using PyQt6. It provides a customizable and dynamic user interface framework that simplifies the development of desktop applications. The library includes features such as collapsible panels, adjustable fonts, scalable widgets, and an integrated status bar manager, making it a versatile choice for building modern desktop applications.

## Features

- **Collapsible Splitters**: Easily create and manage splitters that can be collapsed or expanded based on user interaction.
- **Dynamic Font Scaling**: Automatically adjusts the font sizes of labels and widgets based on the window size or specific dimensions.
- **Customizable Status Bar**: Manage and update a status bar with custom messages and tooltips.
- **Panel Labels**: Create labeled panels with custom styling and size policies.
- **Widget Adjustment**: Dynamically adjusts the width, height, and font sizes of widgets to ensure a consistent and responsive UI layout.
- **Transitions**: Perform UI transitions between different configurations with a delay, allowing for smooth changes in the interface.

## Installation

### Prerequisites

- Python 3.7+
- PyQt6

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/actx4gh/GlavnaQt.git
   cd GlavnaQt
   ```

2. **Install Dependencies**

   You can install the required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Example**

   To see GlavnaQt in action, you can run the provided example script:

   ```bash
   python example.py
   ```

## Usage

### Creating a Main Window with Collapsible Splitters

The core of GlavnaQt revolves around creating a `MainWindow` that manages collapsible splitters and customizable panels.

```python
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.config import UIConfiguration

app = QApplication([])

# Define your UI configuration
ui_config = UIConfiguration(
    font_face="Helvetica",
    font_size=13,
    splitter_handle_width=5,
    window_size=(800, 600),
    window_position=(100, 100),
    enable_status_bar_manager=True,
    collapsible_sections={
        'top': {'text': 'Top Bar', 'alignment': UIConfiguration.ALIGN_CENTER},
        'bottom': {'text': 'Status Bar', 'alignment': UIConfiguration.ALIGN_CENTER},
        'left': {'text': 'Left Sidebar', 'alignment': UIConfiguration.ALIGN_CENTER},
        'right': {'text': 'Right Sidebar', 'alignment': UIConfiguration.ALIGN_CENTER},
        'main_content': {'text': 'Main Content', 'alignment': UIConfiguration.ALIGN_CENTER},
    }
)

# Create and show the main window
main_window = MainWindow(ui_config)
main_window.show()

app.exec()
```

### Customizing Panels

You can create custom panels by using the `PanelLabel` class, which allows you to define size policies, fonts, and alignment.

```python
from ui.panel import PanelLabel, EXPANDING_FIXED
from PyQt6.QtCore import Qt

# Example of creating a custom panel
custom_panel = PanelLabel(
    text="Custom Panel",
    name="custom_panel",
    size_policy=EXPANDING_FIXED,
    font_name="Arial",
    font_size=14,
    alignment=Qt.AlignmentFlag.AlignCenter,
    frame_shape=QFrame.Shape.Box
)
```

### Managing the Status Bar

The `StatusBarManager` class provides an easy way to update and manage the status bar of your application.

```python
from ui.status_bar_manager import StatusBarManager

# Assuming 'main_window' is an instance of MainWindow
status_manager = StatusBarManager(main_window)

# Update the status bar text
status_manager.update_status_bar("Application Loaded Successfully")
```

### Performing UI Transitions

Transitions between different UI states can be performed using the `perform_transition` function.

```python
from ui.transitions import perform_transition
from core.config import UIConfiguration

# Define start and end configurations
start_config = UIConfiguration(
    font_face="Helvetica",
    font_size=13,
    window_size=(800, 600)
)
end_config = UIConfiguration(
    font_face="Arial",
    font_size=16,
    window_size=(1024, 768)
)

# Perform the transition
perform_transition(main_window, start_config, end_config)
```

## Contributing

Contributions to GlavnaQt are welcome! If you find a bug or have a feature request, please open an issue on GitHub. If you'd like to contribute code, please fork the repository and submit a pull request.

### Steps to Contribute

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear and descriptive messages.
4. Push your changes to your fork.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- Thanks to the developers of PyQt6 for providing a robust framework for building Python GUIs.
- Inspired by various open-source GUI libraries that make desktop application development more accessible.
