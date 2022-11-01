import json

import requests
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from framework import Challenge, Ctf

SERVER = "http://localhost:5000/"

Builder.load_string("""
<CtfListScreen>:
    ctflist: ctflist
    GridLayout:
        cols: 1
        GridLayout: 
            id: ctflist
        GridLayout:
            rows: 1
            Button:
                text: "Second"
                on_release: app.root.current = 'second'
            Button:
                text: "create-ctf"
                on_release: app.root.current = 'create-ctf'

<SecondScreen>:
    GridLayout:
        cols: 1
        Label: 
            text: "second screen!"
        GridLayout:
            rows: 1
            Button:
                text: "Main"
                on_release: app.root.current = 'main-panel'
            Button:
                text: "create-ctf"
                on_release: app.root.current = 'create-ctf'

<CreateCtfScreen>:
    GridLayout:
        cols: 1
        Label:
            text: "Create Ctf Here"
        GridLayout:
            rows: 1
            Button:
                text: "Cancel"
                on_release: app.root.current = 'main-panel'
            Button:
                text: "Validate"
                on_release: app.root.current = 'main-panel'
""")

class CtfListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        ctflist = ObjectProperty(None)

        requests.get(SERVER + "reset")
        res = requests.get(SERVER + "list")
        ctfs = res.json()["ctfs"]
  
        self.cols = 1
        for ctf in ctfs.values():
            b1 = Button(text=ctf["name"])
            ctflist.add_widget(b1)

class SecondScreen(Screen):
    pass

class CreateCtfScreen(Screen):
    pass

class CtfScreenManager(ScreenManager):
    pass

class CtfApp(App):
    def build(self):
        manager = ScreenManager()
        manager.add_widget(CtfListScreen(name="main-panel"))
        manager.add_widget(SecondScreen(name="second"))
        manager.add_widget(CreateCtfScreen(name="create-ctf"))
        return manager

if __name__ == "__main__":
    CtfApp().run()
