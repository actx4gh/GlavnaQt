import logging
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class ResizeSignal(QObject):
    """
    Custom signal class for handling resize events in the application.
    """
    resized = pyqtSignal()


def setup_event_handling(main_window, resize_signal):
    """
    Sets up event handling for the main window, specifically connecting resize signals and timers.

    Args:
        main_window (QMainWindow): The main window instance where the resize signal will be connected.
        resize_signal (ResizeSignal): An instance of ResizeSignal to emit signals on resize events.
    """
    # Connect the resize signal to the main window's resize timeout handler
    main_window.resize_signal = resize_signal
    main_window.resize_signal.resized.connect(main_window.on_resize_timeout)

    # Set up a single-shot timer to manage delayed resize signals
    main_window.resize_timer = QTimer()
    main_window.resize_timer.setSingleShot(True)
    main_window.resize_timer.timeout.connect(lambda: main_window.resize_signal.resized.emit())

    logger.debug("Resize signal connected and ready to emit on resize event.")


def handle_resize_event(main_window, event):
    """
    Handles the window resize event, managing the suppression of logging and controlling the resize timer.

    Args:
        main_window (QMainWindow): The main window instance receiving the resize event.
        event (QResizeEvent): The resize event to handle.
    """
    if not hasattr(main_window, 'suppress_logging'):
        main_window.suppress_logging = False

    if main_window.suppress_logging:
        # Stop and restart the timer for real-time updates if logging is suppressed
        if main_window.resize_timer.isActive():
            main_window.resize_timer.stop()
        main_window.resize_timer.start(50)  # Reduced delay for faster response
    else:
        logger.debug("Entered handle_resize_event.")
        main_window.resize_signal.resized.emit()

        if main_window.resize_timer.isActive():
            logger.debug("Stopping active resize timer.")
            main_window.resize_timer.stop()

        logger.debug("Starting resize signal timer.")
        main_window.resize_timer.start(50)  # Reduced delay for faster response

        logger.debug("Exiting handle_resize_event.")
