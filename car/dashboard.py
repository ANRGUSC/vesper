import cv2
import numpy as np
import os
import threading
#import tkFont
import Tkinter as Tk
import traceback

from PIL import Image
from PIL import ImageTk
from twisted.internet import reactor
from twisted.internet import tksupport

import config as cfg

from common import MyObject

## Objection detection imports
import sys
sys.path.append('./tfmodels/research')
sys.path.append('./tfmodels/research/object_detection')

from utils import label_map_util
from utils import visualization_utils as vis_util


TF_ODAPI_ROOT = './tfmodels/research/object_detection'


class Dashboard(MyObject):
    """GUI for system interaction."""
    IMAGE_DEPTH = 3

    PATH_TO_LABELS = os.path.join(TF_ODAPI_ROOT, 'data', 'mscoco_label_map.pbtxt')
    NUM_CLASSES = 90

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
        self.frame.grid(row=0, column=0, stick=Tk.N, rowspan=2)

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

        # Throughput/makespan entries
        self.frame2 = Tk.Frame(master)
        self.frame2.grid(row=1, column=1)

        self.throughput_entry = self.make_entry(self.frame2, 'Throughput', 0,
                                                '%0.2f' % cfg.T_o)
        self.makespan_entry = self.make_entry(self.frame2, 'Makespan', 1,
                                                '%0.2f' % cfg.M_o)

        self.set_button = Tk.Button(self.frame2, text='Set Constraints',
                                    command=self.set_constraints)
        self.set_button.grid(row=2, column=1)


        # Results window
        if cfg.SHOW_RESULTS:
            tl = Tk.Toplevel(self.master)

            self.result_canvas = Tk.Canvas(tl,
                                    width=cfg.DASH_IMAGE_WIDTH,
                                    height=cfg.DASH_IMAGE_HEIGHT)
            self.result_image = self.result_canvas.create_image(0, 0, anchor=Tk.NW)
            self.result_canvas.grid()

            self.load_label_map() # For displaying results

        # Dashboard state
        self.running = threading.Event()

        # OpenCV image to display on Canvas
        self.image = None
        self.new_image = False

        self.result = None
        self.new_result = False

        self.controller = None
        self.values = {}
        return

    def load_label_map(self):
        label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map,
                                                                    max_num_classes=self.NUM_CLASSES,
                                                                    use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        return

    def make_entry(self, parent, caption, row, text):
        """Creates an entry widget with label."""
        Tk.Label(parent, text=caption).grid(row=row, column=0, sticky=Tk.E)
        entry = Tk.Entry(parent)
        entry.grid(row=row, column=1)
        entry.insert(0, text)
        return entry

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
                fx = float(cfg.DASH_IMAGE_WIDTH)/image.shape[1]
                fy = float(cfg.DASH_IMAGE_HEIGHT)/image.shape[0]
                image = cv2.resize(image, (0, 0), fx=fx, fy=fy)

            # Convert image from OpenCV format to Tk format
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(Image.fromarray(img_rgb))

            self.canvas.itemconfig(self.canvas_image, image=img_tk)
            self.canvas.image = img_tk # reference to keep image alive

        if self.new_result:
            self.new_result = False

            image = self.result[0]
            (boxes, scores, classes, num) = self.result[1]

            vis_util.visualize_boxes_and_labels_on_image_array(
                image,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=2)

            canvas_shape = (cfg.DASH_IMAGE_HEIGHT, cfg.DASH_IMAGE_WIDTH,
                     self.IMAGE_DEPTH)
            if not image.shape == canvas_shape:
                # Resize image
                fx = float(cfg.DASH_IMAGE_WIDTH)/image.shape[1]
                fy = float(cfg.DASH_IMAGE_HEIGHT)/image.shape[0]
                image = cv2.resize(image, (0, 0), fx=fx, fy=fy)

            # Convert image from OpenCV format to Tk format
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(Image.fromarray(img_rgb))

            self.result_canvas.itemconfig(self.result_image, image=img_tk)
            self.result_canvas.image = img_tk # reference to keep image alive

        self.loop()
        return

    def put_image(self, image):
        self.image = image
        self.new_image = True
        return

    def put_result(self, result):
        if cfg.SHOW_RESULTS:
            self.result = result
            self.new_result = True
        return

    def put_values(self, values):
        self.values = values
        return

    def set_constraints(self):
        """Sets new throughput and makespan constraints."""

        try:
            throughput = float(self.throughput_entry.get())
            makespan = float(self.makespan_entry.get())

        except ValueError:
            self.log().warn(traceback.format_exc())
            return

        if self.controller:
            self.log().info('setting new constraints ' \
                            'throughput=%0.1f, makespan=%0.1f',
                            throughput, makespan)
            self.controller.set_constraints(throughput, makespan)

        return
