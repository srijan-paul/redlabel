#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedLabel - Modern Image Annotation Tool

ARCHITECTURE OVERVIEW:
=====================

RedLabel is built using PyQt5 and follows a Model-View-Controller pattern:

MAIN COMPONENTS:
- MainWindow: Primary application window and controller
- Canvas: Drawing surface for image display and annotation interaction
- LabelFile: Data model for saving/loading annotations in multiple formats
- I/O Modules: Format-specific readers/writers (PASCAL VOC, YOLO, CreateML)

DATA FLOW:
1. User opens image directory or file
2. Image loaded and displayed on Canvas
3. User creates/edits bounding boxes via Canvas interactions
4. Shapes are stored in MainWindow state and Canvas
5. Annotations saved to file using appropriate I/O module

SUPPORTED FORMATS:
- PASCAL VOC (XML): Standard computer vision annotation format
- YOLO (TXT): Dark framework format with normalized coordinates  
- CreateML (JSON): Apple's machine learning annotation format

KEY CLASSES:
- MainWindow: Main application logic, UI management, file operations
- Canvas: Interactive drawing surface, shape manipulation, user interactions
- Shape: Geometric primitives for bounding boxes and labels
- LabelFile: Unified interface for annotation persistence
- Settings: Application configuration management

The application uses a plugin-style architecture for annotation formats,
making it easy to add new import/export capabilities.

This file now uses a modular architecture with separate mixins for:
- Core functionality (MainWindowCore)
- UI initialization (MainWindowUIMixin)
- Actions and menus (MainWindowActionsMixin)
- File operations (MainWindowFileOpsMixin)
- Canvas operations (MainWindowCanvasMixin)
- YOLO inference (MainWindowYOLOMixin)
"""
import argparse
import codecs
import os
import sys

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    # needed for py3+qt4
    # Ref:
    # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
    # http://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

# Import the modular components
from gui.main_window_core import MainWindowCore
from gui.main_window_ui import MainWindowUIMixin
from gui.main_window_actions import MainWindowActionsMixin
from gui.main_window_file_ops import MainWindowFileOpsMixin
from gui.main_window_canvas import MainWindowCanvasMixin
from gui.main_window_yolo import MainWindowYOLOMixin

# Import required libs
from libs.resources import *
from libs.constants import *
from libs.utils import *

__appname__ = 'RedLabel'


class MainWindow(MainWindowCore, MainWindowUIMixin, MainWindowActionsMixin, 
                MainWindowFileOpsMixin, MainWindowCanvasMixin, MainWindowYOLOMixin):
    """Main application window combining all functionality through mixins."""

    def __init__(self, default_filename=None, default_prefdef_class_file=None, default_save_dir=None):
        """Initialize the main window with optional default settings."""
        # Initialize the core functionality first
        super(MainWindow, self).__init__(default_filename, default_prefdef_class_file, default_save_dir)
        
        # Setup UI components
        self.init_ui_components()
        
        # Setup actions and menus
        self.init_actions_and_menus()
        
        # Apply settings and complete initialization
        self._finalize_initialization(default_filename)

    def _finalize_initialization(self, default_filename):
        """Apply final settings and complete application initialization."""
        # Initialize application state that wasn't set in core
        self.file_path = ustr(default_filename) if default_filename else None
        
        # Handle recent files compatibility between Qt4/Qt5
        if self.settings.get(SETTING_RECENT_FILES):
            if have_qstring():
                recent_file_qstring_list = self.settings.get(SETTING_RECENT_FILES)
                self.recent_files = [ustr(i) for i in recent_file_qstring_list]
            else:
                self.recent_files = recent_file_qstring_list = self.settings.get(SETTING_RECENT_FILES)

        # Restore window geometry and position
        self.restore_window_geometry(self.settings)
        
        # Apply saved colors and canvas settings
        self.apply_color_settings(self.settings)
        
        # Setup advanced mode if enabled
        def xbool(x):
            if isinstance(x, QVariant):
                return x.toBool()
            return bool(x)

        if xbool(self.settings.get(SETTING_ADVANCE_MODE, False)):
            self.actions.advancedMode.setChecked(True)
            self.toggle_advanced_mode()

        # Initialize UI and load initial file if specified
        self.complete_ui_setup(default_filename)

    def set_format(self, save_format):
        """Set the current annotation format (PASCAL VOC, YOLO, or CreateML)."""
        from libs.labelFile import LabelFileFormat
        from libs.pascal_voc_io import XML_EXT
        from libs.yolo_io import TXT_EXT
        from libs.create_ml_io import JSON_EXT
        from libs.labelFile import LabelFile
        
        if save_format == FORMAT_PASCALVOC:
            self.actions.save_format.setText(FORMAT_PASCALVOC)
            self.actions.save_format.setIcon(new_icon("format_voc"))
            self.label_file_format = LabelFileFormat.PASCAL_VOC
            LabelFile.suffix = XML_EXT
        elif save_format == FORMAT_YOLO:
            self.actions.save_format.setText(FORMAT_YOLO)
            self.actions.save_format.setIcon(new_icon("format_yolo"))
            self.label_file_format = LabelFileFormat.YOLO
            LabelFile.suffix = TXT_EXT
        elif save_format == FORMAT_CREATEML:
            self.actions.save_format.setText(FORMAT_CREATEML)
            self.actions.save_format.setIcon(new_icon("format_createml"))
            self.label_file_format = LabelFileFormat.CREATE_ML
            LabelFile.suffix = JSON_EXT

    def change_format(self):
        """Cycle through annotation formats: PASCAL VOC -> YOLO -> CreateML -> PASCAL VOC."""
        from libs.labelFile import LabelFileFormat
        
        if self.label_file_format == LabelFileFormat.PASCAL_VOC:
            self.set_format(FORMAT_YOLO)
        elif self.label_file_format == LabelFileFormat.YOLO:
            self.set_format(FORMAT_CREATEML)
        elif self.label_file_format == LabelFileFormat.CREATE_ML:
            self.set_format(FORMAT_PASCALVOC)
        else:
            raise ValueError('Unknown label file format.')
        self.set_dirty()

    def show_tutorial_dialog(self, browser='default', link=None):
        """Open tutorial or documentation link in specified browser."""
        import webbrowser as wb
        import shutil
        
        if link is None:
            link = self.screencast

        if browser.lower() == 'default':
            wb.open(link, new=2)
        elif browser.lower() == 'chrome' and self.os_name == 'Windows':
            # Special handling for Chrome on Windows due to webbrowser module limitations
            if shutil.which(browser.lower()):
                wb.register('chrome', None, wb.BackgroundBrowser('chrome'))
            else:
                # Fallback to common Chrome installation path
                chrome_path = "D:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                if os.path.isfile(chrome_path):
                    wb.register('chrome', None, wb.BackgroundBrowser(chrome_path))
            try:
                wb.get('chrome').open(link, new=2)
            except:
                # Fallback to default browser if Chrome registration fails
                wb.open(link, new=2)
        elif browser.lower() in wb._browsers:
            wb.get(browser.lower()).open(link, new=2)

    def show_default_tutorial_dialog(self):
        """Show default tutorial dialog."""
        self.show_tutorial_dialog(browser='default')

    def show_info_dialog(self):
        """Show application information dialog."""
        from libs.__init__ import __version__
        msg = u'Name:{0} \nApp Version:{1} \n{2} '.format(__appname__, __version__, sys.version_info)
        QMessageBox.information(self, u'Information', msg)

    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts."""
        self.show_tutorial_dialog(browser='default', link='https://github.com/srijan-paul/RedLabel#keyboard-shortcuts')

    def reset_all(self):
        """Reset all settings and restart application."""
        self.settings.reset()
        self.close()
        process = QProcess()
        process.startDetached(os.path.abspath(__file__))

    def discard_changes_dialog(self):
        """Show discard changes dialog."""
        yes, no, cancel = QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel
        msg = u'You have unsaved changes, would you like to save them and proceed?\nClick "No" to undo all changes.'
        return QMessageBox.warning(self, u'Attention', msg, yes | no | cancel)


def inverted(color):
    """Return inverted color."""
    return QColor(*[255 - v for v in color.getRgb()])


def read(filename, default=None):
    """Read image file."""
    try:
        reader = QImageReader(filename)
        reader.setAutoTransform(True)
        return reader.read()
    except:
        return default


def get_main_app(argv=None):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    if not argv:
        argv = []
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(new_icon("app"))
    # Tzutalin 201705+: Accept extra agruments to change predefined class file
    argparser = argparse.ArgumentParser()
    argparser.add_argument("image_dir", nargs="?")
    argparser.add_argument("class_file",
                           default=os.path.join(os.path.dirname(__file__), "data", "predefined_classes.txt"),
                           nargs="?")
    argparser.add_argument("save_dir", nargs="?")
    args = argparser.parse_args(argv[1:])

    args.image_dir = args.image_dir and os.path.normpath(args.image_dir)
    args.class_file = args.class_file and os.path.normpath(args.class_file)
    args.save_dir = args.save_dir and os.path.normpath(args.save_dir)

    # Usage : redlabel.py image classFile saveDir
    win = MainWindow(args.image_dir,
                     args.class_file,
                     args.save_dir)
    win.show()
    return app, win


def main():
    """construct main app and run it"""
    app, _win = get_main_app(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
