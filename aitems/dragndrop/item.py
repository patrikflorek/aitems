# aitems/dragndrop/item.py

from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import (
    IconRightWidget,
    OneLineAvatarIconListItem,
    OneLineRightIconListItem,
    TwoLineAvatarIconListItem,
    TwoLineRightIconListItem,
    ThreeLineAvatarIconListItem,
    ThreeLineRightIconListItem,
)


Builder.load_string(
    """
<DragHandle>:
    icon: "menu"

<Spacer@Widget>:
    size_hint_y: None

<DraggableListItem>:
    orientation: "vertical"
    adaptive_height: True
    spacer_expanded: False
    dragged: False
    md_list_item: None
    
    Spacer:
        height: 0 if root.md_list_item is None or not root.spacer_expanded \
            else root.md_list_item.height
"""
)


class DragHandle(IconRightWidget):
    """
    Starts dragging of an item it belongs to. A ScrollView widget containing
    the items list determines maximum distance the touch can move within
    an interval so the drag can start.
    """

    def __init__(self, item, **kwargs):
        super(DragHandle, self).__init__(**kwargs)
        self._item = item

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud["dragged_item"] = self._item
            return True

        return False


class DraggableListItem(MDBoxLayout):
    """
    This is a draggable/expandable list item.
    """

    spacer_expanded = BooleanProperty(False)
    list_scrolling = BooleanProperty(False)

    def __init__(self, item_index, item_data, md_list_item_class_name, **kwargs):
        super(DraggableListItem, self).__init__(**kwargs)
        # Original and current indices refer to indices of list data array
        self.original_index = item_index
        self.current_index = self.original_index

        self.item_data = item_data

        # Enclosed MDList item classes have to be able to incorporate IRightBody widget (DragHandle instance)
        md_list_item_class = globals()[md_list_item_class_name]
        self.md_list_item = md_list_item_class(**item_data)
        drag_handle = DragHandle(self)
        self.md_list_item.add_widget(drag_handle)
        self.add_widget(self.md_list_item)

    def on_touch_move(self, touch):
        self.dragged = False

        if "dragged_item" not in touch.ud:
            return False

        dragged_item = touch.ud["dragged_item"]
        if self == dragged_item:
            if self.list_scrolling:
                return False

            # Item is dragged within the touch limits.
            self.dragged = True
            self.y = touch.y - self.height // 2
        else:
            if not touch.ud["dragged_item"].list_scrolling:
                # Expand an item if it is below the dragged item.
                window_x, window_y = dragged_item.to_window(*dragged_item.pos)
                self.spacer_expanded = self.collide_point(
                    *self.to_widget(window_x, window_y)
                )
            else:
                self.spacer_expanded = False

        return False
