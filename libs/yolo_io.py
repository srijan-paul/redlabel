#!/usr/bin/env python
# -*- coding: utf8 -*-
import codecs
import os

from libs.constants import DEFAULT_ENCODING

TXT_EXT = '.txt'
ENCODE_METHOD = DEFAULT_ENCODING

class YOLOWriter:

    def __init__(self, folder_name, filename, img_size, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False

    def add_bnd_box(self, x_min, y_min, x_max, y_max, name, difficult):
        bnd_box = {'xmin': x_min, 'ymin': y_min, 'xmax': x_max, 'ymax': y_max}
        bnd_box['name'] = name
        bnd_box['difficult'] = difficult
        self.box_list.append(bnd_box)

    def bnd_box_to_yolo_line(self, box, class_list=[]):
        x_min = box['xmin']
        x_max = box['xmax']
        y_min = box['ymin']
        y_max = box['ymax']

        x_center = float((x_min + x_max)) / 2 / self.img_size[1]
        y_center = float((y_min + y_max)) / 2 / self.img_size[0]

        w = float((x_max - x_min)) / self.img_size[1]
        h = float((y_max - y_min)) / self.img_size[0]

        # PR387
        box_name = box['name']
        if box_name not in class_list:
            class_list.append(box_name)

        class_index = class_list.index(box_name)

        return class_index, x_center, y_center, w, h

    def save(self, class_list=[], target_file=None):

        out_file = None  # Update yolo .txt
        out_class_file = None   # Update class list .txt

        if target_file is None:
            out_file = open(
            self.filename + TXT_EXT, 'w', encoding=ENCODE_METHOD)
            classes_file = os.path.join(os.path.dirname(os.path.abspath(self.filename)), "classes.txt")
            out_class_file = open(classes_file, 'w')

        else:
            out_file = codecs.open(target_file, 'w', encoding=ENCODE_METHOD)
            classes_file = os.path.join(os.path.dirname(os.path.abspath(target_file)), "classes.txt")
            out_class_file = open(classes_file, 'w')


        for box in self.box_list:
            class_index, x_center, y_center, w, h = self.bnd_box_to_yolo_line(box, class_list)
            # print (classIndex, x_center, y_center, w, h)
            out_file.write("%d %.6f %.6f %.6f %.6f\n" % (class_index, x_center, y_center, w, h))

        # print (classList)
        # print (out_class_file)
        for c in class_list:
            out_class_file.write(c+'\n')

        out_class_file.close()
        out_file.close()



class YoloReader:

    def __init__(self, file_path, image, class_list_path=None):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.file_path = file_path

        if class_list_path is None:
            dir_path = os.path.dirname(os.path.realpath(self.file_path))
            self.class_list_path = os.path.join(dir_path, "classes.txt")
        else:
            self.class_list_path = class_list_path

        # print (file_path, self.class_list_path)

        try:
            with open(self.class_list_path, 'r') as classes_file:
                self.classes = classes_file.read().strip('\n').split('\n')
                # Remove empty strings from classes list
                self.classes = [cls for cls in self.classes if cls.strip()]
        except FileNotFoundError:
            self.classes = []
            self._missing_classes_file = True
        except Exception as e:
            self.classes = []
            self._classes_file_error = str(e)

        # print (self.classes)

        img_size = [image.height(), image.width(),
                    1 if image.isGrayscale() else 3]

        self.img_size = img_size

        self.verified = False
        # try:
        self.parse_yolo_format()
        # except:
        #     pass

    def get_shapes(self):
        return self.shapes

    def add_shape(self, label, x_min, y_min, x_max, y_max, difficult):

        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.shapes.append((label, points, None, None, difficult))

    def yolo_line_to_shape(self, class_index, x_center, y_center, w, h):
        class_idx = int(class_index)
        
        # Handle case where class index is out of range
        if class_idx >= len(self.classes):
            # Store error info for GUI layer to handle
            if not hasattr(self, '_class_errors'):
                self._class_errors = []
            self._class_errors.append(f"Class index {class_idx} not found (max: {len(self.classes) - 1})")
            # Use a fallback label
            label = f"unknown_class_{class_idx}"
        else:
            label = self.classes[class_idx]

        x_min = max(float(x_center) - float(w) / 2, 0)
        x_max = min(float(x_center) + float(w) / 2, 1)
        y_min = max(float(y_center) - float(h) / 2, 0)
        y_max = min(float(y_center) + float(h) / 2, 1)

        x_min = round(self.img_size[1] * x_min)
        x_max = round(self.img_size[1] * x_max)
        y_min = round(self.img_size[0] * y_min)
        y_max = round(self.img_size[0] * y_max)

        return label, x_min, y_min, x_max, y_max

    def parse_yolo_format(self):
        try:
            with open(self.file_path, 'r') as bnd_box_file:
                for line_num, bndBox in enumerate(bnd_box_file, 1):
                    line = bndBox.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    try:
                        parts = line.split(' ')
                        if len(parts) != 5:
                            if not hasattr(self, '_format_errors'):
                                self._format_errors = []
                            self._format_errors.append(f"Line {line_num}: expected 5 values, got {len(parts)}")
                            continue
                            
                        class_index, x_center, y_center, w, h = parts
                        label, x_min, y_min, x_max, y_max = self.yolo_line_to_shape(class_index, x_center, y_center, w, h)

                        # Caveat: difficult flag is discarded when saved as yolo format.
                        self.add_shape(label, x_min, y_min, x_max, y_max, False)
                    except ValueError as e:
                        if not hasattr(self, '_parse_errors'):
                            self._parse_errors = []
                        self._parse_errors.append(f"Line {line_num}: {str(e)}")
                        continue
                    except Exception as e:
                        if not hasattr(self, '_parse_errors'):
                            self._parse_errors = []
                        self._parse_errors.append(f"Line {line_num}: {str(e)}")
                        continue
        except IOError as e:
            print(f"Error: Could not read YOLO annotation file {self.file_path}: {e}")
            raise

    def get_errors(self):
        """Get all errors encountered during parsing."""
        errors = []
        
        if hasattr(self, '_missing_classes_file'):
            errors.append(f"Classes file not found: {self.class_list_path}")
            
        if hasattr(self, '_classes_file_error'):
            errors.append(f"Could not read classes file: {self._classes_file_error}")
            
        if hasattr(self, '_class_errors'):
            errors.extend(self._class_errors)
            
        if hasattr(self, '_format_errors'):
            errors.extend(self._format_errors)
            
        if hasattr(self, '_parse_errors'):
            errors.extend(self._parse_errors)
            
        return errors
