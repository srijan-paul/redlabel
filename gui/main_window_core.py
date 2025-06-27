#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core MainWindow functionality for RedLabel
"""
import os.path
import platform
import sys
from functools import partial

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.settings import Settings
from libs.stringBundle import StringBundle
from libs.constants import *
from libs.shape import Shape, DEFAULT_LINE_COLOR, DEFAULT_FILL_COLOR
from libs.utils import *
from libs.toolBar import ToolBar
from libs.ustr import ustr
from libs.yolo_inference import YOLOModelDetector, YOLOInferenceEngine
from libs.labelFile import LabelFileFormat

__appname__ = 'RedLabel'


class WindowMixin(object):
    """Mixin providing common window functionality for menu and toolbar creation."""

    def menu(self, title, actions=None):
        """Create a menu with the given title and optional actions."""
        menu = self.menuBar().addMenu(title)
        if actions:
            add_actions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        """Create a toolbar with the given title and optional actions."""
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            add_actions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar


class MainWindowCore(QMainWindow, WindowMixin):
    """Core MainWindow class with basic window management and state."""
    
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, default_filename=None, default_prefdef_class_file=None, default_save_dir=None):
        """Initialize the main window with optional default settings."""
        super(MainWindowCore, self).__init__()
        self.setWindowTitle(__appname__)

        # Initialize core application state
        self._init_core_state(default_save_dir, default_prefdef_class_file)

    def _init_core_state(self, default_save_dir, default_prefdef_class_file):
        """Initialize core application state and settings."""
        # Load settings
        self.settings = Settings()
        self.settings.load()
        settings = self.settings
        
        # System and localization
        self.os_name = platform.system()
        self.string_bundle = StringBundle.get_bundle()
        get_str = lambda str_id: self.string_bundle.get_string(str_id)
        self.get_str = get_str  # Store for use in other methods
        
        # File handling state
        self.default_save_dir = default_save_dir
        self.label_file_format = self.settings.get(SETTING_LABEL_FILE_FORMAT, LabelFileFormat.YOLO)
        self.m_img_list = []
        self.dir_name = None
        self.label_hist = []
        self.last_open_dir = None
        self.cur_img_idx = 0
        self.img_count = len(self.m_img_list)
        
        # Application state flags
        self.dirty = False
        self._no_selection_slot = False
        self._beginner = True
        self.screencast = "https://youtu.be/p0nR2YsCY_U"
        
        # Load predefined classes
        self.load_predefined_classes(default_prefdef_class_file)
        if self.label_hist:
            self.default_label = self.label_hist[0]
        else:
            print("Not find:/data/predefined_classes.txt (optional)")
        
        # Shape management
        self.items_to_shapes = {}
        self.shapes_to_items = {}
        self.prev_label_text = ''
        
        # YOLO inference components
        self.yolo_model_detector = YOLOModelDetector()
        self.yolo_inference_engine = YOLOInferenceEngine()
        self.yolo_worker = None
        self.selected_yolo_model = None

        # Initialize additional state variables
        self._init_additional_state()

    def _init_additional_state(self):
        """Initialize additional state variables used across modules."""
        self.image = QImage()
        self.file_path = None
        self.recent_files = []
        self.max_recent = 7
        self.line_color = None
        self.fill_color = None
        self.zoom_level = 100
        self.fit_window = False
        self.difficult = False
        self.zoom_mode = self.MANUAL_ZOOM
        self.image_data = None
        self.label_file = None
        self.lastLabel = None

    def load_predefined_classes(self, predefined_classes_file):
        """Load predefined class labels from file."""
        import codecs
        if predefined_classes_file is None:
            predefined_classes_file = 'data/predefined_classes.txt'

        if os.path.exists(predefined_classes_file) is True:
            with codecs.open(predefined_classes_file, 'r', 'utf8') as f:
                for line in f:
                    line = line.strip()
                    if self.label_hist is None:
                        self.label_hist = [line]
                    else:
                        self.label_hist.append(line)

    def restore_window_geometry(self, settings):
        """Restore window size and position from settings."""
        size = settings.get(SETTING_WIN_SIZE, QSize(600, 500))
        position = QPoint(0, 0)
        saved_position = settings.get(SETTING_WIN_POSE, position)
        
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop().availableGeometry(i).contains(saved_position):
                position = saved_position
                break
        
        self.resize(size)
        self.move(position)
        self.restoreState(settings.get(SETTING_WIN_STATE, QByteArray()))

    def apply_color_settings(self, settings):
        """Apply saved color settings to shapes and canvas."""
        save_dir = ustr(settings.get(SETTING_SAVE_DIR, None))
        self.last_open_dir = ustr(settings.get(SETTING_LAST_OPEN_DIR, None))
        
        if self.default_save_dir is None and save_dir is not None and os.path.exists(save_dir):
            self.default_save_dir = save_dir
            self.statusBar().showMessage('%s started. Annotation will be saved to %s' %
                                         (__appname__, self.default_save_dir))
            self.statusBar().show()

        Shape.line_color = self.line_color = QColor(settings.get(SETTING_LINE_COLOR, DEFAULT_LINE_COLOR))
        Shape.fill_color = self.fill_color = QColor(settings.get(SETTING_FILL_COLOR, DEFAULT_FILL_COLOR))
        if hasattr(self, 'canvas'):
            self.canvas.set_drawing_color(self.line_color)
        Shape.difficult = self.difficult

    # Utility methods used across modules
    def set_dirty(self):
        """Mark the current file as having unsaved changes."""
        self.dirty = True
        if hasattr(self, 'actions'):
            self.actions.save.setEnabled(True)

    def set_clean(self):
        """Mark the current file as having no unsaved changes."""
        self.dirty = False
        if hasattr(self, 'actions'):
            self.actions.save.setEnabled(False)
            self.actions.create.setEnabled(True)

    def queue_event(self, function):
        """Queue a function to be executed in the next event loop iteration."""
        QTimer.singleShot(0, function)

    def status(self, message, delay=5000):
        """Show a status message."""
        self.statusBar().showMessage(message, delay)

    def reset_state(self):
        """Reset application state when closing a file."""
        self.items_to_shapes.clear()
        self.shapes_to_items.clear()
        if hasattr(self, 'label_list'):
            self.label_list.clear()
        self.file_path = None
        self.image_data = None
        self.label_file = None
        if hasattr(self, 'canvas'):
            self.canvas.reset_state()
        if hasattr(self, 'label_coordinates'):
            self.label_coordinates.clear()
        if hasattr(self, 'combo_box'):
            self.combo_box.cb.clear()

    def current_item(self):
        """Get the currently selected item in the label list."""
        if hasattr(self, 'label_list'):
            items = self.label_list.selectedItems()
            if items:
                return items[0]
        return None

    def no_shapes(self):
        """Check if there are no shapes in the current image."""
        return not self.items_to_shapes

    def beginner(self):
        """Check if the application is in beginner mode."""
        return self._beginner

    def advanced(self):
        """Check if the application is in advanced mode."""
        return not self.beginner()

    def add_recent_file(self, file_path):
        """Add a file to the recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        elif len(self.recent_files) >= self.max_recent:
            self.recent_files.pop()
        self.recent_files.insert(0, file_path)

    def close(self):
        """Override close to handle cleanup."""
        if self.may_continue():
            super(MainWindowCore, self).close()

    def closeEvent(self, event):
        """Handle window close event."""
        if self.may_continue():
            settings = self.settings
            # Save settings before closing
            if self.recent_files:
                settings[SETTING_RECENT_FILES] = self.recent_files
            settings[SETTING_WIN_SIZE] = self.size()
            settings[SETTING_WIN_POSE] = self.pos()
            settings[SETTING_WIN_STATE] = self.saveState()
            settings[SETTING_LINE_COLOR] = self.line_color
            settings[SETTING_FILL_COLOR] = self.fill_color
            settings[SETTING_ADVANCE_MODE] = not self._beginner
            if hasattr(self, 'display_label_option'):
                settings[SETTING_PAINT_LABEL] = self.display_label_option.isChecked()
            if hasattr(self, 'auto_saving'):
                settings[SETTING_AUTO_SAVE] = self.auto_saving.isChecked()
            if hasattr(self, 'single_class_mode'):
                settings[SETTING_SINGLE_CLASS] = self.single_class_mode.isChecked()
            settings[SETTING_LABEL_FILE_FORMAT] = self.label_file_format
            settings.save()
            event.accept()
        else:
            event.ignore()

    def may_continue(self):
        """Check if it's safe to continue with an operation that might lose unsaved changes."""
        if not self.dirty:
            return True
        
        result = QMessageBox.question(
            self, 
            'Unsaved Changes',
            'You have unsaved changes. Continue anyway?',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No)
        
        if result == QMessageBox.Yes:
            return True
        elif result == QMessageBox.No:
            return self.save_file()
        else:
            return False
