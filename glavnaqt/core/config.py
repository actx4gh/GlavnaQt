import os
import platform

from PyQt6.QtCore import Qt

LOGGER_NAME = 'glavnaqt'
LOG_FILE_NAME = f'{LOGGER_NAME}.log'
APP_NAME = LOGGER_NAME
PLATFORM_NAME = platform.system()
LOG_LEVEL = "INFO"

# Alignment constants for UI components
ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
ALIGN_RIGHT = Qt.AlignmentFlag.AlignRight
ALIGN_TOP = Qt.AlignmentFlag.AlignTop
ALIGN_BOTTOM = Qt.AlignmentFlag.AlignBottom
ALIGN_VCENTER = Qt.AlignmentFlag.AlignVCenter
ALIGN_HCENTER = Qt.AlignmentFlag.AlignHCenter
ALIGN_JUSTIFY = Qt.AlignmentFlag.AlignJustify
ALIGN_ABSOLUTE = Qt.AlignmentFlag.AlignAbsolute
ALIGN_LEADING = Qt.AlignmentFlag.AlignLeading
ALIGN_TRAILING = Qt.AlignmentFlag.AlignTrailing
ALIGN_HORZ_MASK = Qt.AlignmentFlag.AlignHorizontal_Mask
ALIGN_VERT_MASK = Qt.AlignmentFlag.AlignVertical_Mask

ALIGNMENT_NAMES_REVERSE_LOOKUP = {
    Qt.AlignmentFlag.AlignCenter: 'ALIGN_CENTER',
    Qt.AlignmentFlag.AlignLeft: 'ALIGN_LEFT',
    Qt.AlignmentFlag.AlignRight: 'ALIGN_RIGHT',
    Qt.AlignmentFlag.AlignTop: 'ALIGN_TOP',
    Qt.AlignmentFlag.AlignBottom: 'ALIGN_BOTTOM',
    Qt.AlignmentFlag.AlignVCenter: 'ALIGN_VCENTER',
    Qt.AlignmentFlag.AlignHCenter: 'ALIGN_HCENTER',
    Qt.AlignmentFlag.AlignJustify: 'ALIGN_JUSTIFY',
    Qt.AlignmentFlag.AlignAbsolute: 'ALIGN_ABSOLUTE',
    Qt.AlignmentFlag.AlignLeading: 'ALIGN_LEADING',
    Qt.AlignmentFlag.AlignTrailing: 'ALIGN_TRAILING',
    Qt.AlignmentFlag.AlignHorizontal_Mask: 'ALIGN_HORZ_MASK',
    Qt.AlignmentFlag.AlignVertical_Mask: 'ALIGN_VERT_MASK',
}


def _get_default_config_dir():
    system = PLATFORM_NAME # Use the platform_name attribute

    if system == 'Darwin':  # macOS
        config_dir = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
    elif system == 'Linux' or 'CYGWIN' in system:  # Linux and Cygwin
        config_dir = os.path.expanduser(f"~/.config/{APP_NAME}")
    elif system == 'Windows':  # Windows
        config_dir = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)
    else:
        raise RuntimeError(f"Unsupported OS: {system}")
    return config_dir


CONFIG_DIR = _get_default_config_dir()


class UIConfiguration:
    def __init__(self,
                 font_face="Helvetica",
                 font_size=12,
                 splitter_handle_width=5,
                 window_size=(640, 480),
                 window_position=(100, 100),
                 collapsible_sections=None,
                 enable_status_bar_manager=False):
        self.font_face = font_face
        self.font_size = font_size
        self.splitter_handle_width = splitter_handle_width
        self.window_size = window_size
        self.window_position = window_position
        self.enable_status_bar_manager = enable_status_bar_manager

        self.collapsible_sections = collapsible_sections or {}

        if "main_content" not in self.collapsible_sections:
            self.collapsible_sections["main_content"] = {
                "text": "Main Content",
                "alignment": ALIGN_CENTER
            }

    def __eq__(self, other):
        if not isinstance(other, UIConfiguration):
            return False
        return (self.font_face == other.font_face and
                self.font_size == other.font_size and
                self.splitter_handle_width == other.splitter_handle_width and
                self.window_size == other.window_size and
                self.window_position == other.window_position and
                self.enable_status_bar_manager == other.enable_status_bar_manager and
                self.collapsible_sections == other.collapsible_sections)

    def get_section_widget(self, section_name):
        """
        Returns the custom widget for the given section, if any.
        """
        return self.collapsible_sections.get(section_name, {}).get("widget")

    def update_collapsible_section(self, section_name, text=None, alignment=ALIGN_CENTER, widget=None,
                                   status_label=None):
        self.collapsible_sections[section_name] = {
            "text": text,
            "alignment": alignment,
            "widget": widget,
        }
        if status_label:
            self.collapsible_sections[section_name].update({"status_label": status_label})

    def get_section_alignment(self, section_name):
        return self.collapsible_sections.get(section_name, {}).get("alignment", ALIGN_CENTER)

    def replace_alignment_constants(self, data=None):
        """
        Recursively replaces alignment objects in the dictionary with their respective constant var names and
        returns a string representation of the dictionary without quotes around the constant variable names.

        Args:
            data (dict): The nested dictionary containing UI configuration.
                        If None, operates on the instance's `collapsible_sections`.

        Returns:
            str: A string representation of the dictionary with alignment constants replaced by their variable names.
        """
        if data is None:
            data = self.collapsible_sections

        def replace_and_format(d):
            if isinstance(d, dict):
                return '{' + ', '.join(f'{repr(key)}: {replace_and_format(value)}' for key, value in d.items()) + '}'
            elif isinstance(d, tuple):
                return f'({", ".join(map(replace_and_format, d))})'
            elif isinstance(d, Qt.AlignmentFlag):
                return ALIGNMENT_NAMES_REVERSE_LOOKUP[d]
            else:
                return repr(d)

        return replace_and_format(data)

    def __repr__(self):
        return f"UIConfiguration({self.replace_alignment_constants()})"


# Singleton instance of UIConfiguration
config = UIConfiguration()

# Expose only the singleton instance for external use
__all__ = ['config']
