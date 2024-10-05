from PyQt6.QtCore import Qt

from confumo import Confumo

LOGGER_NAME = 'glavnaqt'
LOG_FILE_NAME = f'{LOGGER_NAME}.log'
APP_NAME = LOGGER_NAME
LOG_LEVEL = "INFO"


class UIConfiguration(Confumo):
    """Subclass of BaseConfiguration that handles all UI-related configuration."""

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

    def __init__(self, app_name=APP_NAME, additional_args=None):
        if additional_args is None:
            additional_args = []
            # Add the --cycle-configs argument
        additional_args.extend([
            {'flags': ['--cycle-configs'],
             'kwargs': {'action': 'store_true', 'help': 'Enable cycling through configurations'}}
        ])
        super().__init__(app_name=app_name, additional_args=additional_args)
        self.font_face = "Helvetica"
        self.font_size = 12
        self.splitter_handle_width = 5
        self.window_size = (640, 480)
        self.window_position = (100, 100)
        self.enable_status_bar_manager = False
        self.collapsible_sections = {
            "main_content": {
                "text": "Main Content",
                "alignment": Qt.AlignmentFlag.AlignCenter
            }
        }

    def initialize(self):
        """Call this method when you need to explicitly initialize glavnaqt."""
        self._setup_module_attributes()
        _ = self.config  # Accessing config will trigger lazy initialization

    def get_section_widget(self, section_name):
        """
        Returns the custom widget for the given section, if any.
        """
        return self.collapsible_sections.get(section_name, {}).get("widget")

    def update_collapsible_section(self, section_name, text=None, alignment=Qt.AlignmentFlag.AlignCenter, widget=None,
                                   status_label=None):
        self.collapsible_sections[section_name] = {
            "text": text,
            "alignment": alignment,
            "widget": widget,
        }
        if status_label:
            self.collapsible_sections[section_name].update({"status_label": status_label})

    def get_section_alignment(self, section_name):
        return self.collapsible_sections.get(section_name, {}).get("alignment", Qt.AlignmentFlag.AlignCenter)

    def replace_alignment_constants(self, data=None):
        """Recursively replaces alignment objects with their constant var names."""
        if data is None:
            data = self.collapsible_sections

        def replace_and_format(d):
            if isinstance(d, dict):
                return '{' + ', '.join(f'{repr(key)}: {replace_and_format(value)}' for key, value in d.items()) + '}'
            elif isinstance(d, tuple):
                return f'({", ".join(map(replace_and_format, d))})'
            elif isinstance(d, Qt.AlignmentFlag):
                return self.ALIGNMENT_NAMES_REVERSE_LOOKUP[d]
            else:
                return repr(d)

        return replace_and_format(data)

    def __repr__(self):
        return f"UIConfigurationSingleton({self.replace_alignment_constants()})"

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

UIConfiguration.get_instance()