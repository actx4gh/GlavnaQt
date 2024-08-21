from PyQt6.QtWidgets import QSplitter


class SectionWidget:
    def __init__(self, section_name):
        self.section_name = section_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if not hasattr(instance, '_section_map'):
            instance._section_map = {}
        # Return both splitter and widget as a tuple
        return instance._section_map.get(self.section_name, (None, None))

    def __set__(self, instance, value):
        if not hasattr(instance, '_section_map'):
            instance._section_map = {}

        # Determine what was provided (splitter, widget, or both)
        if isinstance(value, QSplitter):
            splitter = value
            widget = instance._section_map.get(self.section_name, [None, None])[1]
        elif isinstance(value, tuple):
            splitter, widget = value
        else:  # Assume it's a widget
            splitter, _ = instance._section_map.get(self.section_name, [None, None])
            widget = value

        # Initialize a flag to determine if we need to update _section_map at the end
        update_map = True

        # Update or set the widget and splitter as needed
        if splitter is not None and widget is not None:
            found_index = None
            for i in range(splitter.count()):
                if isinstance(splitter.widget(i), QSplitter) and not isinstance(widget, QSplitter):
                    continue
                existing_widget = splitter.widget(i)
                # Compare using a reliable attribute or method, like object reference or widget name
                if existing_widget == widget and existing_widget.objectName() == widget.objectName():
                    instance._section_map[self.section_name] = [splitter, widget]
                    return  # Early exit; no further updates needed
                elif existing_widget.objectName() == widget.objectName():
                    found_index = i
                    break

            if found_index is not None:
                # Replace the existing widget
                splitter.replaceWidget(found_index, widget)
            else:
                # If the widget isn't found, add it
                splitter.addWidget(widget)

        elif splitter is not None and widget is None:
            instance._section_map[self.section_name] = [splitter, None]
            update_map = False  # No need to update again at the end

        elif splitter is None and widget is not None:
            instance._section_map[self.section_name] = [None, widget]
            update_map = False  # No need to update again at the end

        # Update the section_map only if both splitter and widget are None or if needed
        if update_map:
            instance._section_map[self.section_name] = [splitter, widget]
