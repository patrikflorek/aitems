# aitems/demo/dragndrop.py

"""
Demo App
========

Demonstrates scrollable drag'n'drop items list widget functionality. 
"""

from kivy.lang.builder import Builder

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from aitems.dragndrop.list import ScrollableDragNDropListContainer


Builder.load_string(
    """
<DemoScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDLabel:
            text: "Space above"
            text_size: self.size
            halign: "center"
            size_hint_y: None
            height: "42dp"
            canvas:
                Color: 
                    rgba: 0, .6, .3, .3
                Rectangle:
                    pos: self.pos
                    size: self.size
        
        RelativeLayout:  
            id: container  # The scrollable drag'n'drop items list will be mounted here.

        MDLabel:
            text: "Space below"
            text_size: self.size
            halign: "center"
            size_hint_y: None
            height: "42dp"
            canvas.before:
                Color: 
                    rgba: 0, .6, .3, .3
                Rectangle:
                    pos: self.pos
                    size: self.size
"""
)


class DemoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Widget instantiation
        md_list_item_class_name = "OneLineRightIconListItem"
        list_container = ScrollableDragNDropListContainer(md_list_item_class_name)

        # Provide the widget with an array of dicts (depending on the md_list_item class)
        sample_list_data = [
            {"text": "1. Ganymede"},
            {"text": "2. Callisto"},
            {"text": "3. Io"},
            {"text": "4. Europa"},
            {"text": "5. Himalia"},
            {"text": "6. Amalthea"},
            {"text": "7. Thebe"},
            {"text": "8. Elara"},
            {"text": "9. Carme"},
            {"text": "10. Lysithea"},
            {"text": "11. Ananke"},
            {"text": "12. Adrastea"},
            {"text": "13. Themisto"},
            {"text": "14. Megaclite"},
            {"text": "15. Kalyke"},
            {"text": "16. Harpalyke"},
            {"text": "17. Aoede"},
            {"text": "18. Helike"},
        ]

        list_container.set_list_data(list_data=sample_list_data)

        # Mount the widget to a screen
        self.ids.container.add_widget(list_container)

        # Get the array from the widget
        print("Returned list data:")
        print(list_container.get_list_data())

        # Get the order of the array/list items
        print("Original items order:")
        original_list_order = list_container.get_items_order()
        print(original_list_order)

        # Change the order of items by providing a permutation of the original items indices
        print("New list order:")
        new_list_order = [10, 6, 8, 14, 7, 13, 11, 0, 17, 2, 16, 12, 15, 5, 4, 1, 9, 3]
        list_container.set_items_order(new_list_order)
        print(list_container.get_items_order())


class DemoApp(MDApp):
    def build(self):
        return DemoScreen()


if __name__ == "__main__":
    DemoApp().run()
