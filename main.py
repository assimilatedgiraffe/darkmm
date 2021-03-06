from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.textinput import *
from kivy.uix.relativelayout import *
from kivy.uix.label import *
from kivy.uix.listview import ListView, ListItemButton
from kivy.core.window import Window

import xml.etree.ElementTree as etree

# parse xml from file
fullMapTree = etree.parse("test.mm")
parentMap = dict((c, p) for p in fullMapTree.getiterator() for c in p) #map of parents
# warning: destructive, removes formatting
for el in fullMapTree.getiterator():
    if el.tag != 'node':
        parent = parentMap.get(el)
        if parent is not None:
            parent.remove(el)
selectedParent = fullMapTree.getroot()[0][2] # parent of currently selected node
selectedIndex = 0  # currently selected node
selectedIndexList = [0, 0, 0]
# print [El.get("TEXT") for El in mapRootNode]

class Node(TextInput):
    """node for mindmap view"""
    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)
        self.size = (100, 100)


class MindMap(Widget):
    """mindmap view"""
    def __init__(self, **kwargs):
        super(MindMap, self).__init__(**kwargs)
        nodes = [Node(), Node(), Node()]
        for i, node in enumerate(nodes):
            node.text = 'node ' + str(i)
            node.pos[0] = node.pos[0] + (i*100)
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

        self.add_widget(TreeView())

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def refresh_UI(self):
        """cant find a better way to do this"""
        self.clear_widgets()
        print selectedParent, selectedIndexList
        self.add_widget(TreeView())

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
        #parse xml from file
        tree = etree.parse("test.mm")
        mmap = tree.getroot()[0]

    def build(self):
        return OverView()


if __name__ == '__main__':
    MindMapApp().run()