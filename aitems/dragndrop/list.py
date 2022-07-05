# aitems/dragndrop/list.py

"""
Scrollable Drag'n'Drop List
===========================

This widget combines and extends the functionality of ScrollView and MDList.
It expects to be only one scrollable drag'n'drop list on a screen. 

"""

from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout

from dragndrop.item import DraggableListItem


Builder.load_string(
    """
#:import dp kivy.metrics.dp

<ScrollableDragNDropListContainer>:
    scroll_view: scroll_view
    items_list: items_list
    md_list_item_height: 0
    ScrollView:
        id: scroll_view
        MDList:
            id: items_list
            padding: [0, dp(8), 0, root.md_list_item_height + dp(8)] # Make some space for scrolling and/or dragged item placing
"""
)


SCROLL_DISTANCE = dp(20)
CHECK_SCROLL_INTERVAL = 0.1


class ScrollableDragNDropListContainer(FloatLayout):
    """
    Allows a list item to be dragged within the list area and
    scrolls the list when the item si above the top or below the bottom
    of the list.
    """

    scroll_view = ObjectProperty()
    items_list = ObjectProperty()

    def __init__(self, md_list_item_class_name, **kwargs):
        super(ScrollableDragNDropListContainer, self).__init__(**kwargs)
        self._md_list_item_class_name = md_list_item_class_name

        self._scroll_event = None

        self.dragged_item = None
        self.dragging = False

    def get_list_data(self):
        list_data = [w.item_data for w in self.items_list.children][::-1]
        return list_data

    def _set_md_list_item_height(self, dt):
        self.md_list_item_height = (
            0
            if not self.items_list.children
            else self.items_list.children[0].md_list_item.height
        )

    def set_list_data(self, list_data):
        self.items_list.clear_widgets()
        for i, item_data in enumerate(list_data):
            item = DraggableListItem(
                item_index=i,
                item_data=item_data,
                md_list_item_class_name=self._md_list_item_class_name,
            )
            self.items_list.add_widget(item)

        # We don't know the height of a list item until the list is built
        Clock.schedule_once(self._set_md_list_item_height)

    def get_items_order(self):
        indices = [w.original_index for w in self.items_list.children][::-1]
        return indices

    def set_items_order(self, indices):
        orig_order_list_items = sorted(
            [x for x in self.items_list.children], key=lambda x: x.original_index
        )

        self.items_list.clear_widgets()

        for i, index in enumerate(indices):
            orig_order_list_items[index].current_index = i
            self.items_list.add_widget(orig_order_list_items[index])

    def _set_items_list_touch_limits(self):
        """Sets top and bottom touch limits."""

        if self.items_list.height <= self.scroll_view.height:
            _, items_list_to_window_y = self.items_list.to_window(0, self.items_list.y)
            self.touch_top_limit = (
                items_list_to_window_y
                + self.items_list.height
                - self.md_list_item_height * 3 // 2
            )
            self.touch_bottom_limit = (
                items_list_to_window_y + self.md_list_item_height // 2 + dp(8)
            )
        else:
            _, scroll_view_to_window_y = self.scroll_view.to_window(
                0, self.scroll_view.y
            )
            self.touch_top_limit = (
                scroll_view_to_window_y
                + self.scroll_view.height
                - self.md_list_item_height * 3 // 2
            )
            self.touch_bottom_limit = (
                scroll_view_to_window_y - self.md_list_item_height // 2 + dp(16)
            )

    def _start_drag(self):
        self._set_items_list_touch_limits()
        if self.dragged_item is not None:
            # Place dragged item on the same place on the screen.
            original_pos = self.dragged_item.to_window(*self.dragged_item.pos)
            self.items_list.remove_widget(self.dragged_item)
            self.add_widget(self.dragged_item)
            self.dragged_item.pos = self.to_widget(*original_pos)

            self.dragging = True

    def _cancel_scroll(self):
        if self.dragged_item is not None:
            self.dragged_item.list_scrolling = False

        if self._scroll_event is not None:
            self._scroll_event.cancel()
            self._scroll_event = None

    def _is_scrolling(self, direction):
        return (
            self.dragged_item is not None
            and self.dragged_item.list_scrolling
            and (direction == "up" or self.scroll_view.scroll_y < 1.0)
            and (direction == "down" or self.scroll_view.scroll_y > 0.0)
        )

    def _do_scroll(self, direction):
        """Manages scrolling when a drag touch is outside an area restricted
        by top and bottom touch limits."""

        if self.dragged_item is None or not self._is_scrolling(direction):
            self._cancel_scroll()
        else:
            scroll_dx, scroll_dy = self.scroll_view.convert_distance_to_scroll(
                0, SCROLL_DISTANCE
            )
            if direction == "down":
                scroll_y = self.scroll_view.scroll_y + scroll_dy
                self.scroll_view.scroll_y = min(scroll_y, 1.0)
            elif direction == "up":
                scroll_y = self.scroll_view.scroll_y - scroll_dy
                self.scroll_view.scroll_y = max(scroll_y, 0.0)

            if self._scroll_event is None:
                self._scroll_event = Clock.create_trigger(
                    lambda dt: self._do_scroll(direction), CHECK_SCROLL_INTERVAL
                )

            self._scroll_event()

    def _cancel_drag(self):
        self._cancel_scroll()

        if self.dragged_item is not None:
            self.dragged_item.dragged = False

            self.remove_widget(self.dragged_item)

            items_list_index = (
                len(self.items_list.children) - self.dragged_item.current_index
            )

            self.items_list.add_widget(self.dragged_item, items_list_index)

            self.dragged_item = None

        self.dragging = False

        for item in self.items_list.children:
            item.spacer_expanded = False

    def _insert_dragged_item(self):
        """Inserts the dragged item to the position of an expanded list item
        or at the end of the list if no item is expanded."""
        expanded_item_current_index = next(
            (w.current_index for w in self.items_list.children if w.spacer_expanded),
            len(self.items_list.children) + 1,
        )

        self.remove_widget(self.dragged_item)

        if expanded_item_current_index > self.dragged_item.current_index:
            self.items_list.add_widget(
                self.dragged_item,
                len(self.items_list.children) - expanded_item_current_index + 1,
            )
        else:
            self.items_list.add_widget(
                self.dragged_item,
                len(self.items_list.children) - expanded_item_current_index,
            )

        for i, item in enumerate(self.items_list.children[::-1]):
            item.current_index = i

        if self.scroll_view.scroll_y == 0.0:
            (
                delta_scroll_x,
                delta_scroll_y,
            ) = self.scroll_view.convert_distance_to_scroll(0, self.md_list_item_height)
            self.scroll_view.scroll_y = delta_scroll_y

        self.dragged_item = None
        self._cancel_drag()

    def on_touch_move(self, touch):
        self.dragged_item = touch.ud.get("dragged_item", None)
        if self.dragged_item is None:
            # This is not a drag touch
            return super(ScrollableDragNDropListContainer, self).on_touch_move(touch)

        if not self.dragging:
            # Start dragging
            self._start_drag()
            return super(ScrollableDragNDropListContainer, self).on_touch_move(touch)

        # Manage the items list scrolling

        if touch.y <= self.touch_top_limit and touch.y >= self.touch_bottom_limit:
            # No scrolling if touch is in the list area.
            self.dragged_item.list_scrolling = False
            return super(ScrollableDragNDropListContainer, self).on_touch_move(touch)

        if self.scroll_view.height >= self.items_list.height:
            # No need to scroll when scroll view and items list have the same height.
            return False

        if self.dragged_item.list_scrolling:
            # List is already scrolling, there is nothing more to do
            return True

        if touch.y > self.touch_top_limit:
            # Touch is above the list.
            if self.scroll_view.scroll_y < 1.0:
                # List starts scrolling down.
                self.dragged_item.list_scrolling = True
                self._do_scroll("down")

                # Let children know that the list starts scrolling.
                return super(ScrollableDragNDropListContainer, self).on_touch_move(
                    touch
                )

            # List is scrolling and children should not care.
            return True

        if touch.y < self.touch_bottom_limit:
            # Touch is below the list.
            if self.scroll_view.scroll_y > 0.0:
                # List starts scrolling up.
                self.dragged_item.list_scrolling = True
                self._do_scroll("up")

                return super(ScrollableDragNDropListContainer, self).on_touch_move(
                    touch
                )

            # List is scrolling and children should not care.
            return True

        # Never
        return False

    def on_touch_up(self, touch):
        if "dragged_item" not in touch.ud:
            return super(ScrollableDragNDropListContainer, self).on_touch_up(touch)

        if self.dragged_item is None or self.dragged_item != touch.ud["dragged_item"]:
            # Something went wrong.
            self._cancel_drag()
            return super(ScrollableDragNDropListContainer, self).on_touch_up(touch)

        if self.dragged_item.list_scrolling:
            # Restore the list if it was scrolling.
            self._cancel_drag()
            return True

        if not self.collide_point(*touch.pos):
            # Restore the list if the touch is finished outside the container.
            self._cancel_drag()
            return False

        # Insert the dragged item to desired position.
        self._insert_dragged_item()

        return True
