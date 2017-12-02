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
        self.frame.pack()

        # Canvas widget
        self.canvas = Tk.Canvas(self.frame,
                                width=cfg.DASH_IMAGE_WIDTH,
                                height=cfg.DASH_IMAGE_HEIGHT)
        self.canvas.pack()

        # Prepare items on the canvas
        self.canvas_image = self.canvas.create_image(0, 0, anchor=Tk.NW)

        #font = tkFont.Font(size=12)
        #self.canvas_status = self.canvas.create_text(1, 1, anchor=Tk.NW,
        #                                             font=font, fill='green')

        # Dashboard state
        self.running = threading.Event()

        #self.fps = 0.0
        #self.fps_monitor = Monitor(self.fps_update, self.STATUS_UPDATE_PERIOD)

        # OpenCV image to display on Canvas
        self.image = None
        self.new_image = False

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

    def update(self):
        if not self.running.is_set():
            return

        # Update FPS
        #fps = 'FPS: %.1f' % self.fps
        #self.canvas.itemconfig(self.canvas_status, text=fps)

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

        #self.fps_monitor.increment()
