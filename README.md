
# Project Title

This project is a PyQt6-based graphical user interface (GUI) application, which includes a modular layout management system, status bar management, event-driven transitions, and customizable user interface (UI) configurations. It is designed to allow dynamic updates and transitions of the UI layout based on configuration changes.

## Features

- **Event-Driven UI Transitions**: Supports smooth UI transitions between different configurations using the event bus and timer-driven actions.
- **Dynamic Layout Management**: The layout manager dynamically handles collapsible sections like sidebars, top bars, and the main content area.
- **Status Bar Manager**: Provides an easy-to-use interface for managing and updating a status bar, including a busy indicator.
- **Customizable UI Configurations**: UI elements such as font face, size, and section visibility can be adjusted dynamically.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repository.git
   cd your-repository
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python example.py
   ```

## Usage

You can cycle through different UI configurations by running the application with the `--cycle-configs` argument:

```bash
python example.py --cycle-configs
```

The main window will automatically cycle through the predefined UI layouts after a set delay.

## Project Structure

- **`main_window.py`**: Defines the main window and handles dynamic layout updates.
- **`layout.py`**: Manages the layout of UI components including sidebars and main content.
- **`status_bar_manager.py`**: Controls the status bar and the busy indicator.
- **`event_bus.py`**: Implements a simple event bus for managing UI events.
- **`transitions.py`**: Handles smooth transitions between different UI configurations.

