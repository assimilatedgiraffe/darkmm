from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from math import pi, cos, sin

from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.textinput import *
from kivy.uix.relativelayout import *
from kivy.uix.label import *
from kivy.uix.listview import ListView, ListItemButton
from kivy.core.window import Window
from kivy.uix.button import Button

import xml.etree.ElementTree as etree

# parse xml from file
fullMapTree = etree.parse("test.mm")
parentMap = dict((c, p) for p in fullMapTree.getiterator() for c in p)  # map of parents
# warning: destructive, removes formatting
for el in fullMapTree.getiterator():
    if el.tag != 'node':
        parent = parentMap.get(el)
        if parent is not None:
            parent.remove(el)
selectedParent = fullMapTree.getroot()[0]  # parent of currently selected node
selectedIndex = 0  # currently selected node
selectedIndexList = [0, 0]


# print [El.get("TEXT") for El in mapRootNode]



class PathListView(StackLayout):
    """path list at top of window like ubuntu file manager"""

    def __init__(self, **kwargs):
        super(PathListView, self).__init__(**kwargs)
        child = fullMapTree.getroot()
        for i in selectedIndexList:
            child = child[i]
            btn = Button(text=child.get("TEXT"),
                         size_hint=(.15, 1),
                         text_size=self.size,
                         max_lines=3,
                         halign='left',
                         valign='middle')
            btn.bind(size=btn.setter('text_size'))
            self.add_widget(btn)


class Node(Button):
    """node for mindmap view"""

    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)
        # self.size = (100, 100)
        self.size_hint = (None, None)
        self.text_size = (150, None)
        self.halign = 'center'


class MindMapView(RelativeLayout):
    """mindmap view"""

    def __init__(self, **kwargs):
        super(MindMapView, self).__init__(**kwargs)
        # selected node in centre
        center_node = Node()
        center_node.text = selectedParent[selectedIndexList[-1]].get('TEXT')
        center_node.size = center_node.texture_size
        center_node.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.add_widget(center_node)

        # circle of child nodes
        n_nodes = len(selectedParent[selectedIndexList[-1]])
        for i, child in enumerate(selectedParent[selectedIndexList[-1]]):
            node = Node()
            node.text = child.get('TEXT')
            node.size = node.texture_size
            # calculate pos
            r = .3
            w = i * (2 * pi / n_nodes)
            x, y = (r * cos(w)) + .5, (r * sin(w)) + .5
            node.pos_hint = {'center_x': x, 'center_y': y}
            self.add_widget(node)


class TreeView(BoxLayout):
    """ Main middle col, parent selected n uncles left, child nodes on right """

    def __init__(self, **kwargs):
        super(TreeView, self).__init__(**kwargs)

        self.parent_and_uncles_list_adapter = ListAdapter(
            data=[El.get("TEXT") for El in parentMap[selectedParent]],
            selection_mode='single',
            allow_empty_selection=False,
            cls=ListItemButton)
        self.add_widget(ListView(adapter=self.parent_and_uncles_list_adapter))
        self.parent_and_uncles_list_adapter.get_view(selectedIndexList[-2]).trigger_action(duration=0)

        self.main_list_adapter = ListAdapter(
            data=[El.get("TEXT") for El in selectedParent],
            selection_mode='single',
            allow_empty_selection=False,
            cls=ListItemButton)
        self.add_widget(ListView(adapter=self.main_list_adapter))
        self.main_list_adapter.get_view(selectedIndexList[-1]).trigger_action(duration=0)

        child_list_adapter = ListAdapter(
            data=[El.get("TEXT") for El in selectedParent[selectedIndexList[-1]]],
            selection_mode='single',
            allow_empty_selection=True,
            cls=ListItemButton)
        self.add_widget(ListView(adapter=child_list_adapter))


class OverView(BoxLayout):
    """main window"""

    def __init__(self, **kwargs):
        super(OverView, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.add_widget(PathListView(size_hint=(1, .1)))
        self.add_widget(MindMapView(size_hint=(1, .9)))

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def refresh_UI(self):
        """cant find a better way to do this"""
        self.clear_widgets()
        print selectedParent.get('TEXT'), selectedIndexList
        self.add_widget(PathListView(size_hint=(1, .1)))
        self.add_widget(TreeView(size_hint=(1, .9)))

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        global selectedParent, selectedIndexList
        if keycode[1] == 'j':
            if len(selectedParent) > selectedIndexList[-1] + 1:
                selectedIndexList[-1] += 1
                self.refresh_UI()
            #            index = self.main_list_adapter.selection[0].index + 1
            #            new_selection = self.main_list_adapter.get_view(index)
            #            if new_selection and not new_selection.is_selected:
            #                new_selection.trigger_action(duration=0)
        elif keycode[1] == 'k':
            if selectedIndexList[-1] > 0:
                selectedIndexList[-1] -= 1
                self.refresh_UI()
        elif keycode[1] == 'h':
            if parentMap.get(parentMap[selectedParent]) is not None:
                selectedParent = parentMap[selectedParent]
                selectedIndexList.pop()
                self.refresh_UI()
        elif keycode[1] == 'l':
            if len(selectedParent[selectedIndexList[-1]]) is not 0:
                selectedParent = selectedParent[selectedIndexList[-1]]
                selectedIndexList.append(0)
                self.refresh_UI()
        return True


class MindMapApp(App):
    def loadFromFile(self):
        # parse xml from file
        tree = etree.parse("test.mm")
        mmap = tree.getroot()[0]

    def build(self):
        return OverView()


if __name__ == '__main__':
    MindMapApp().run()
