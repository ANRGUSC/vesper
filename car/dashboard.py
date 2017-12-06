import cv2
import threading
#import tkFont
import Tkinter as Tk

from PIL import Image
from PIL import ImageTk
from twisted.internet import reactor
from twisted.internet import tksupport

import sys
sys.path.append('../')

import config as cfg

from common import MyObject


class Dashboard(MyObject):
    """GUI for system interaction."""
    IMAGE_DEPTH = 3

    def __init__(self, master=None):
        if master is None:
            # Create root widget
            root = Tk.Tk()
            tksupport.install(root)
            self.master = root

        else:
            self.master = master

        self.master.protocol("WM_DELETE_WINDOW", self.exit)

        self.frame = Tk.Frame(master)
        self.frame.grid(row=0, column=0, stick=Tk.N)

        # Canvas widget
        self.canvas = Tk.Canvas(self.frame,
                                width=cfg.DASH_IMAGE_WIDTH,
                                height=cfg.DASH_IMAGE_HEIGHT)
        self.canvas.grid()

        # Prepare items on the canvas
        self.canvas_image = self.canvas.create_image(0, 0, anchor=Tk.NW)

        #font = tkFont.Font(size=12)
        #self.canvas_status = self.canvas.create_text(1, 1, anchor=Tk.NW,
        #                                             font=font, fill='green')

        self.listbox = Tk.Listbox(master, height=25, width=50)
        self.listbox.grid(row=0, column=1, sticky=Tk.N)

        # Dashboard state
        self.running = threading.Event()

        # OpenCV image to display on Canvas
        self.image = None
        self.new_image = False

        self.values = {}
        return

    def start(self):
        """Starts dashboard refreshes."""
        self.running.set()
        self.loop()
        return

    def stop(self):
        """Stops dashboard."""
        self.running.clear()
        return

    def exit(self):
        """Exits."""
        self.stop()

        if reactor.running:
            reactor.stop()

        return

    def loop(self):
        self.master.after(int(1000/cfg.DASH_REFRESH_RATE), self.update)
        return

    def list_add(self, key, value, indent=0):
        line = '  ' * indent

        if type(value) == dict:
            line += '%s: ' % (key)
            self.listbox.insert(Tk.END, line)

            for k, v in sorted(value.iteritems()):
                self.list_add(k, v, indent+1)

            return

        elif type(value) == set:
            line += '%s: ' % (key)
            self.listbox.insert(Tk.END, line)

            for v in sorted(value):
                self.list_add(None, v, indent+1)

            return

        elif type(value) == float:
            v = '%.6f' % value

        else:
            v = '%s' % value

        if not key is None:
            line += '%s: ' % (key)

        line += v

        self.listbox.insert(Tk.END, line)
        return

    def update(self):
        if not self.running.is_set():
            return

        # Refresh values in listbox
        self.listbox.delete(0, Tk.END)
        for key, value in sorted(self.values.iteritems()):
            self.list_add(key, value)

        # Refresh image if a new one is available
        if self.new_image:
            self.new_image = False

            image = self.image

            canvas_shape = (cfg.DASH_IMAGE_HEIGHT, cfg.DASH_IMAGE_WIDTH,
                     self.IMAGE_DEPTH)
            if not image.shape == canvas_shape:
                # Resize image
                print '*** RESIZING ***'
                fx = float(cfg.DASH_IMAGE_WIDTH)/image.shape[1]
                fy = float(cfg.DASH_IMAGE_HEIGHT)/image.shape[0]
                image = cv2.resize(image, (0, 0), fx=fx, fy=fy)

            # Convert image from OpenCV format to Tk format
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(Image.fromarray(img_rgb))

            self.canvas.itemconfig(self.canvas_image, image=img_tk)
            self.canvas.image = img_tk # reference to keep image alive

        self.loop()
        return

    def put_image(self, image):
        self.image = image
        self.new_image = True
        return

    def put_values(self, values):
        self.values = values
        return
