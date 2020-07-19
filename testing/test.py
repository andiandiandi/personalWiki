import logging
import sys
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MyEventHandler(PatternMatchingEventHandler):
    def on_moved(self, event):
        print("moved",event)

    def on_created(self, event):
        print("created",event)

    def on_deleted(self, event):
        print("deleted",event)

    def on_modified(self, event):
        print("modified",event)


path = "C:\\Users\\Andre\\Desktop\\nowiki"

event_handler = MyEventHandler(patterns=['*.md', '*.txt'],
                               ignore_directories=True)
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()