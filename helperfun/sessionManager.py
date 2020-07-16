from . import configManager
from . import pathManager
from . import wikiSettingsManager
from . import localApi

import imp
from . import socketio

import time
import threading
import json

_CONNECTIONSTRING = "http://127.0.0.1:9000"

imp.reload(configManager)
imp.reload(pathManager)
imp.reload(socketio)
imp.reload(wikiSettingsManager)
imp.reload(localApi)

connections = {}
_zombieCollector = None

def cleanup():
    print("cleaning up")
    for root_folder in connections:
        con = connections[root_folder]
        con.disconnect()
        

def add(root_folder):
    if not root_folder in connections:
        connections[root_folder] = Connection(root_folder)
        for c in connections:
            print("c",c)

    #if not _zombieCollector:
    #   run_zombieCollector()
    #elif not _zombieCollector.isAlive():
    #   run_zombieCollector()

    return connections[root_folder]


def remove(root_folder):
    if root_folder in connections:
        try:
            connections[root_folder].disconnect()
            connections[root_folder] = None
            del connections[root_folder]
        except:
            connections[root_folder] = None
            del connections[root_folder]

def createConnection(root_folder):
    return Connection(root_folder)

def hasProject(root_folder):
    return root_folder in connections

def connection(root_folder):
    if root_folder in connections:
         return connections[root_folder]
    return None


class Connection:
    def __init__(self,root_folder):
        self.root_folder = root_folder
        self.socket = socketio.Client(reconnection = True)
        self.socket.on("connect", self.connectedEvent)
        self.socket.on("disconnect", self.disconnectedEvent)
        self.socket.on("error", self.errorEvent)
        self.socket.on("project_initialized", self.projectInitializeResponse)
        self.socket.on("search_query", self.searchQueryResponse)

    def connect(self):
        if not self.socket.connected:
            self.socket.connect(_CONNECTIONSTRING)

    def disconnect(self):
        if self.socket.connected:
            print("disconnecting")
            self.socket.disconnect()

    def connectedEvent(self):
        print(self.socket.sid, "connected")

    def disconnectedEvent(self):
        print("disconnected")

    def projectInitializeResponse(self, jsondata):
        print("received projectInitializeResponse:", str(jsondata))

    def searchQueryResponse(self, jsondata):
        print("received searchQueryResponse:" + str(jsondata))
        #jsondata is no jsonstr
        d = json.loads(jsondata)
        l = []
        for entry in d:
            for s in d["span"]:
                i = {"path":d["path"],
                    "start":s["start"],
                    "span":s["span"]
                    }
                l.append(json.dumps(i))

        def on_done(index):
            item = json.loads(l[index])
            view = sublime.window.open_file(item["path"])
            while(view.is_loading()):
                time.sleep(0.5)
            sublime.window.active_view().run_command("goto_line", {"line": item["start"]} )

        sublime.show_quick_panel(jsondata[span], on_done)

    def isConnected(self):
        if self.socket:
            return self.socket.connected
        return False

    def errorEvent(self,data):
        print("error event:",data)

    def projectInitialize(self):
        jsondata = pathManager.path_to_dict(self.root_folder)
        d = {
            "root_folder": self.root_folder,
            "project_structure": jsondata
        }
        self.send("initialize_project",json.dumps(d))

    def searchQuery(self,searchQuery):
        self.send("search_query", json.dumps(searchQuery))

    def save(self,jsonfile):
        self.send("save_file",json.dumps(jsonfile))

    def sid(self):
        print(self.socket)
        print(self.socket.connected)
        print(self.socket.sid)

    def send(self,event,message):
        self.socket.emit(event,message)

############### threading section#################

def check_zombies_every_n_seconds():
    zombie_clear_interval = get_zombie_clear_interval()
    while connections:
        active_windows = [(window.id(),pathManager.root_folder(window)) for window in localApi.windows()]

        for con in list(connections.values()):
            #iterate over copy
            for id in list(con.window_ids):
                if (id,con.path) not in active_windows:
                    con.window_ids.remove(id)
                    print("removing from con:",id)

        to_remove = [k for k in connections.keys() if not connections[k].window_ids]
        for k in to_remove: 
            remove(k)
            print("removing",k)

        time.sleep(zombie_clear_interval)


def run_zombieCollector():
    global _zombieCollector
    _zombieCollector = threading.Thread(target=check_zombies_every_n_seconds, daemon=True)
    _zombieCollector.start()

def stop_zombieCollector():
    global _zombieCollector
    if not _zombieCollector:
        return

    _zombieCollector.join()


def get_zombie_clear_interval():
    sublime_settings        = wikiSettingsManager.get("session")
    clear_sessions_interval    = sublime_settings.get('clear_sessions_interval', 15)

    #only unsigned integers for saving-interval
    if clear_sessions_interval <= 0:
        clear_sessions_interval = 15

    return clear_sessions_interval