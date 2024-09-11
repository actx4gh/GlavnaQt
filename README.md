GlavnaQt: A Basic UI Framework for PyQt6 Applications
=====================================================

**GlavnaQt** is a framework for building PyQt6 desktop applications with a focus on structured layout management, event handling, and status bar control. It provides essential building blocks for managing user interfaces in desktop applications.

Key Components
--------------

### Layout Management:

The `LayoutManager` is used to organize UI sections such as top bars, sidebars, and main content panels. This manager supports vertical and horizontal splitters to divide the screen into multiple areas. It offers a straightforward way to structure an application's layout.

### Status Bar Management:

The `StatusBarManager` offers a simple solution for managing a status bar, including a status label and a basic progress indicator. It's designed to cover most use cases where a status bar is needed, though it focuses on simple configurations.

### Event Handling:

An event bus is included to manage communication between components. Events such as status updates or UI transitions can be broadcast across components. The event system enables decoupling, making it easier to manage application-wide events.

### UI Transitions:

The `perform_transition` method enables transitions between different UI configurations. This is useful for switching between layouts or different states in an application.

Limitations
-----------

### Limited Flexibility:

GlavnaQt is well-suited for applications with simple, predefined layouts. For applications that require more dynamic or highly interactive interfaces, customization options may be limited.

### Basic Configuration System:

The configuration system allows for defining fonts, window sizes, and section alignments, but does not support advanced interaction models or highly customizable layouts.

### Status Bar Constraints:

The status bar management focuses on basic status label updates and a busy indicator. More advanced features, like multi-part status bars, are not included out of the box but can be extended with custom implementations.

Basic Usage
-----------

### Setting Up the Main Window:

Use the `MainWindow` class to initialize the main window for your application. This will serve as the base for all UI components.

python