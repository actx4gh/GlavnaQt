import logging
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QSplitter, QWidget, QVBoxLayout

from glavnaqt.core.logging_utils import log_widget_hierarchy
from glavnaqt.ui.collapsible_splitter import CollapsibleSplitter
from glavnaqt.ui.new_widget_adjustment import WidgetAdjuster
from glavnaqt.ui.panel import EXPANDING_EXPANDING, FIXED_EXPANDING
from .helpers import apply_font
from .panel import PanelLabel, EXPANDING_FIXED

logger = logging.getLogger(__name__)


class LayoutManager:
    """A class to manage individual layout configurations."""

    def __init__(self):
        self.current_widgets = {}
        self.is_initialized = False
        self.last_resize_log_time = time.time()
        self.resize_log_threshold = 0.5
        self.last_config = None
        self.widget_adjuster = None

    def create_widget(self):
        """Create a default widget if none is supplied."""
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        return widget

    def create_top_bar(self, config):
        top_widget = PanelLabel(
            config.collapsible_sections["top"].get("text"),
            "top_bar",
            EXPANDING_FIXED,
            font_name=config.font_face,
            font_size=config.font_size,
            alignment=config.collapsible_sections.get("top").get("alignment")
        )
        top_widget.setObjectName('top_widget')
        apply_font(config.font_face, config.font_size, top_widget)
        return top_widget

    def create_status_bar(self, config):
        bottom_widget = PanelLabel(
            f'{config.collapsible_sections["bottom"].get("text")}',
            "status_bar",
            EXPANDING_FIXED,
            font_name=config.font_face,
            font_size=config.font_size,
            alignment=config.collapsible_sections.get("bottom", {}).get("alignment")
        )
        bottom_widget.setObjectName("bottom_widget")
        apply_font(config.font_face, config.font_size, bottom_widget)
        return bottom_widget

    def get_geometries(self):
        return {k: {"w": v.width(), "h": v.height()} for k, v in self.current_widgets.items() if not isinstance(v, str)}

    def build_layout(self, config):
        self.clear_layout()
        # temp_window = QMainWindow()
        if not self.current_widgets.get("vertical_splitter"):
            self.current_widgets.update(
                {"vertical_splitter": QSplitter(Qt.Orientation.Vertical, objectName="vertical_splitter")})
        # temp_window.setCentralWidget(self.current_widgets["vertical_splitter"])
        main_content_splitter = self.create_main_content_splitter(config)
        if "top" in config.collapsible_sections:
            if "top_splitter" not in self.current_widgets:
                self.current_widgets.update(
                    {"top_splitter": self.create_splitter(Qt.Orientation.Vertical, "top_splitter",
                                                          config.splitter_handle_width, config, "top")})
            if config.collapsible_sections.get("top", {}).get("widget"):
                self.current_widgets["top_widget"] = config.collapsible_sections["top"]["widget"]
            elif "top_widget" not in self.current_widgets:
                self.current_widgets["top_widget"] = self.create_top_bar(config)
            self.current_widgets["top_splitter"].addWidget(self.current_widgets["top_widget"])
            self.current_widgets["top_splitter"].addWidget(main_content_splitter)
            self.current_widgets["vertical_splitter"].addWidget(self.current_widgets.get("top_splitter"))
        else:
            self.current_widgets.get("vertical_splitter").addWidget(main_content_splitter)

        if "bottom" in config.collapsible_sections:
            if "bottom_splitter" not in self.current_widgets:
                self.current_widgets.update(
                    {"bottom_splitter": self.create_splitter(Qt.Orientation.Vertical, "bottom_splitter",
                                                             config.splitter_handle_width, config, "bottom")})
            if config.collapsible_sections.get("bottom", {}).get("widget"):
                self.current_widgets.update({"bottom_widget": config.collapsible_sections["bottom"]["widget"]})
            elif "bottom_widget" not in self.current_widgets:
                self.current_widgets.update({"bottom_widget": self.create_status_bar(config)})

            self.current_widgets["bottom_splitter"].addWidget(self.current_widgets["vertical_splitter"])
            self.current_widgets["bottom_splitter"].addWidget(self.current_widgets["bottom_widget"])
            self.current_widgets.update({"central_widget": "bottom_splitter"})
        else:
            self.current_widgets.update({"central_widget": "vertical_splitter"})
        self.last_config = config
        QTimer.singleShot(25, lambda: self.initialize_geometries())

    def initialize_geometries(self):
        widget_dimensions = self.get_geometries()
        logger.debug(f'{widget_dimensions}')
        for widget_name, dims in widget_dimensions.items():
            width_attr = f"initial_{widget_name}_width"
            height_attr = f"initial_{widget_name}_height"

            if 'w' in dims and not getattr(self, width_attr, None):
                setattr(self, width_attr, dims['w'])
                logger.debug(f"Initial {widget_name} width: {dims['w']}px")

            if 'h' in dims and not getattr(self, height_attr, None):
                setattr(self, height_attr, dims['h'])
                logger.debug(f"Initial {widget_name} height: {dims['h']}px")

        if not self.is_initialized:
            self.widget_adjuster = WidgetAdjuster()
            self.adjust_layout(self.last_config.window_size[0], self.last_config.font_face, self.last_config.font_size)
            self.is_initialized = True

    #        self.is_initialized = True
    #    def initialize_geometries(self, window_size):
    #        #self.get_central_widget().resize(*window_size)
    #        if "main_content_widget" in self.current_widgets and not self.initial_main_content_width:
    #            self.initial_main_content_width = self.current_widgets["main_content_widget"].width()
    #            logger.debug(f"Initial main content width: {self.initial_main_content_width}px")
    #
    #        if "left_widget" in self.current_widgets and not self.initial_left_sidebar_width:
    #            self.initial_left_sidebar_width = self.current_widgets["left_widget"].width()
    #            logger.debug(f"Initial left sidebar width: {self.initial_left_sidebar_width}px")
    #
    #        if "right_widget" in self.current_widgets and not self.initial_right_sidebar_width:
    #            self.initial_right_sidebar_width = self.current_widgets["right_widget"].width()
    #            logger.debug(f"Initial right sidebar width: {self.initial_right_sidebar_width}px")
    #
    #        if "top_widget" in self.current_widgets and not self.initial_top_bar_height:
    #            self.initial_top_bar_height = self.current_widgets["top_widget"].height()
    #            logger.debug(f"Initial top bar height: {self.initial_top_bar_height}px")
    #
    #        if "bottom_widget" in self.current_widgets and not self.initial_status_bar_height:
    #            self.initial_status_bar_height = self.current_widgets["bottom_widget"].height()
    #            logger.debug(f"Initial bottom bar height: {self.initial_status_bar_height}px")
    #
    #        self.is_initialized = True

    def create_splitter(self, orientation, name, handle_width, config, identifier="default"):
        logger.debug(f'Creating collapsible splitter for {identifier}')
        splitter = CollapsibleSplitter(orientation, identifier=identifier,
                                       handle_width=handle_width)
        splitter.setObjectName(name)
        splitter.setContentsMargins(0, 0, 0, 0)  # Ensure no marginsa
        splitter.splitterMoved.connect(
            lambda pos, index: self.handle_splitter_movement(splitter, pos, index, config.window_size[0],
                                                             config.font_face,
                                                             config.font_size))
        return splitter

    def create_main_content(self, config):
        main_content_widget = PanelLabel(
            config.collapsible_sections.get("main_content").get("text"),
            "main_content_widget",
            EXPANDING_EXPANDING,
            font_name=config.font_face,
            font_size=config.font_size,
            alignment=config.collapsible_sections.get("main_content").get("alignment")
        )
        apply_font(config.font_face, config.font_size, main_content_widget)
        return main_content_widget

    def create_left_sidebar(self, config):
        left_sidebar_widget = PanelLabel(
            config.collapsible_sections["left"].get("text"),
            "left_sidebar_widget",
            FIXED_EXPANDING,
            font_name=config.font_face,
            font_size=config.font_size,
            alignment=config.collapsible_sections.get("left").get("alignment")
        )
        apply_font(config.font_face, config.font_size, left_sidebar_widget)
        return left_sidebar_widget

    def create_right_sidebar(self, config):
        right_sidebar_widget = PanelLabel(
            config.collapsible_sections.get("right", {}).get("text"),
            "right_sidebar_widget",
            FIXED_EXPANDING,
            font_name=config.font_face,
            font_size=config.font_size,
            alignment=config.collapsible_sections.get("right").get("alignment")
        )
        apply_font(config.font_face, config.font_size, right_sidebar_widget)
        return right_sidebar_widget

    def create_main_content_splitter(self, config):
        if not self.current_widgets.get("horizontal_splitter"):
            self.current_widgets.update(
                {"horizontal_splitter": QSplitter(Qt.Orientation.Horizontal, objectName="horizontal_splitter")})
        if config.collapsible_sections.get("main_content").get("widget"):
            self.current_widgets.update({"main_content_widget": config.collapsible_sections["main_content"]["widget"]})
        elif not self.current_widgets.get("main_content_widget"):
            self.current_widgets.update({"main_content_widget": self.create_main_content(config)})

        if "left" in config.collapsible_sections:
            if "left_splitter" not in self.current_widgets:
                self.current_widgets.update(
                    {"left_splitter": self.create_splitter(Qt.Orientation.Horizontal, "left_splitter",
                                                           config.splitter_handle_width, config, "left")})
            if config.collapsible_sections.get("left", {}).get("widget"):
                self.current_widgets.update({"left_widget": config.collapsible_sections["left"]["widget"]})
            elif "left_widget" not in self.current_widgets:
                self.current_widgets.update({"left_widget": self.create_left_sidebar(config)})
            self.current_widgets["left_splitter"].addWidget(self.current_widgets["left_widget"])
            self.current_widgets["left_splitter"].addWidget(self.current_widgets["main_content_widget"])
            self.current_widgets["horizontal_splitter"].addWidget(self.current_widgets["left_splitter"])
        else:
            self.current_widgets["horizontal_splitter"].addWidget(self.current_widgets["main_content_widget"])

        if "right" in config.collapsible_sections:
            if "right_splitter" not in self.current_widgets:
                self.current_widgets.update(
                    {"right_splitter": self.create_splitter(Qt.Orientation.Horizontal, "right_splitter",
                                                            config.splitter_handle_width, config, "right")})
            if config.collapsible_sections.get("right", {}).get("widget"):
                self.current_widgets.update({"right_widget": config.collapsible_sections["right"]["widget"]})
            elif "right_widget" not in self.current_widgets:
                self.current_widgets.update({"right_widget": self.create_right_sidebar(config)})
            self.current_widgets["right_splitter"].addWidget(self.current_widgets["horizontal_splitter"])
            self.current_widgets["right_splitter"].addWidget(self.current_widgets["right_widget"])
            return self.current_widgets["right_splitter"]

        return self.current_widgets["horizontal_splitter"]

    def clear_layout(self):
        """Clear the current layout but keep all widgets for potential reuse."""
        if "central_widget" in self.current_widgets:
            del self.current_widgets["central_widget"]
            for widget in self.current_widgets.values():
                widget.setParent(None)

    def get_central_widget(self):
        return self.current_widgets.get(self.current_widgets.get("central_widget"))

    def update_layout(self, config, current_window_size=None):
        self.clear_layout()
        self.build_layout(config)
        QTimer.singleShot(0, lambda: self.adjust_layout(current_window_size=current_window_size))

    def handle_splitter_movement(self, splitter, pos, index, window_width, font_face, font_size):
        logger.debug(f'Handling splitter movement for {splitter.identifier} at position {pos} and index {index}')
        self.adjust_layout(window_width, font_face, font_size)

    def adjust_layout(self, original_window_width=None, font_face=None, font_size=None, current_window_size=None):
        if not original_window_width:
            original_window_width = self.last_config.window_size[0]
        if current_window_size:
            self.get_central_widget().resize(*current_window_size)

        if not font_face:
            font_face = self.last_config.font_face
        if not font_size:
            font_size = self.last_config.font_size

        if not self.current_widgets.get("main_content_widget"):
            logger.error("main_content_widget is not initialized. Layout adjustment cannot proceed.")
            return
        try:
            self.widget_adjuster.adjust_font_and_widget_sizes(self, original_window_width, font_face, font_size)
        except Exception as e:
            logging.error(f"Exception occurred during layout adjustment: {e}", exc_info=True)

        if self.current_widgets.get("central_widget"):
            log_widget_hierarchy(self.get_central_widget())


class LayoutManagerFactory:
    """Factory to manage multiple independent layout managers."""

    def __init__(self):
        self.layout_managers = {}

    def create_layout_manager(self, identifier, layout_dict):
        """Create a new layout manager and store it with the given identifier."""
        if identifier not in self.layout_managers:
            self.layout_managers[identifier] = LayoutManager()
            self.layout_managers[identifier].build_layout(layout_dict)
        return self.layout_managers[identifier]

    def get_layout_manager(self, identifier):
        """Retrieve a layout manager by its identifier."""
        return self.layout_managers.get(identifier)

    def update_layout_manager(self, identifier, layout_dict):
        """Update the layout manager identified by the given identifier."""
        if identifier in self.layout_managers:
            self.layout_managers[identifier].update_layout(layout_dict)
