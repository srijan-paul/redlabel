#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions and menu creation for RedLabel MainWindow
"""
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

from libs.utils import *
from libs.constants import *
from libs.labelFile import LabelFileFormat


class MainWindowActionsMixin:
    """Mixin class for action and menu creation."""

    def init_actions_and_menus(self):
        """Initialize all actions and menu systems."""
        get_str = self.get_str
        action = partial(new_action, self)
        
        # Create file actions
        self._create_file_actions(action, get_str)
        
        # Create edit actions
        self._create_edit_actions(action, get_str)
        
        # Create view actions
        self._create_view_actions(action, get_str)
        
        # Create help actions
        self._create_help_actions(action, get_str)
        
        # Create zoom and light actions
        self._create_zoom_actions(action, get_str)
        self._create_light_actions(action, get_str)
        
        # Create shape actions
        self._create_shape_actions(action, get_str)
        
        # Create mode actions
        self._create_mode_actions(action, get_str)
        
        # Store actions and create menus
        self._store_actions_and_create_menus(get_str)

    def _create_file_actions(self, action, get_str):
        """Create file-related actions."""
        self.quit_action = action(get_str('quit'), self.close,
                                 'Ctrl+Q', 'quit', get_str('quitApp'))
        self.open_action = action(get_str('openFile'), self.open_file,
                                 'Ctrl+O', 'open', get_str('openFileDetail'))
        self.open_dir_action = action(get_str('openDir'), self.open_dir_dialog,
                                     'Ctrl+u', 'open', get_str('openDir'))
        self.change_save_dir_action = action(get_str('changeSaveDir'), self.change_save_dir_dialog,
                                            'Ctrl+r', 'open', get_str('changeSavedAnnotationDir'))
        self.open_annotation_action = action(get_str('openAnnotation'), self.open_annotation_dialog,
                                            'Ctrl+Shift+O', 'open', get_str('openAnnotationDetail'))
        self.copy_prev_bounding_action = action(get_str('copyPrevBounding'), self.copy_previous_bounding_boxes, 
                                               'Ctrl+v', 'copy', get_str('copyPrevBounding'))
        self.open_next_image_action = action(get_str('nextImg'), self.open_next_image,
                                            'd', 'next', get_str('nextImgDetail'))
        self.open_prev_image_action = action(get_str('prevImg'), self.open_prev_image,
                                            'a', 'prev', get_str('prevImgDetail'))
        self.verify_action = action(get_str('verifyImg'), self.verify_image,
                                   'space', 'verify', get_str('verifyImgDetail'))
        self.save_action = action(get_str('save'), self.save_file,
                                 'Ctrl+S', 'save', get_str('saveDetail'), enabled=False)
        
        # Save format action
        def get_format_meta(format):
            if format == LabelFileFormat.PASCAL_VOC:
                return '&PascalVOC', 'format_voc'
            elif format == LabelFileFormat.YOLO:
                return '&YOLO', 'format_yolo'
            elif format == LabelFileFormat.CREATE_ML:
                return '&CreateML', 'format_createml'

        self.save_format_action = action(get_format_meta(self.label_file_format)[0],
                                        self.change_format, 'Ctrl+Y',
                                        get_format_meta(self.label_file_format)[1],
                                        get_str('changeSaveFormat'), enabled=True)

        self.save_as_action = action(get_str('saveAs'), self.save_file_as,
                                    'Ctrl+Shift+S', 'save-as', get_str('saveAsDetail'), enabled=False)
        self.close_action = action(get_str('closeCur'), self.close_file, 
                                  'Ctrl+W', 'close', get_str('closeCurDetail'))
        self.delete_image_action = action(get_str('deleteImg'), self.delete_image, 
                                         'Ctrl+Shift+D', 'close', get_str('deleteImgDetail'))
        self.reset_all_action = action(get_str('resetAll'), self.reset_all, 
                                      None, 'resetall', get_str('resetAllDetail'))

    def _create_edit_actions(self, action, get_str):
        """Create edit-related actions."""
        self.create_action = action(get_str('crtBox'), self.create_shape,
                                   'w', 'new', get_str('crtBoxDetail'), enabled=False)
        self.delete_action = action(get_str('delBox'), self.delete_selected_shape,
                                   'Delete', 'delete', get_str('delBoxDetail'), enabled=False)
        self.copy_action = action(get_str('dupBox'), self.copy_selected_shape,
                                 'Ctrl+D', 'copy', get_str('dupBoxDetail'), enabled=False)
        self.edit_action = action(get_str('editLabel'), self.edit_label,
                                 'Ctrl+E', 'edit', get_str('editLabelDetail'), enabled=False)

    def _create_view_actions(self, action, get_str):
        """Create view-related actions."""
        self.hide_all_action = action(get_str('hideAllBox'), partial(self.toggle_polygons, False),
                                     'Ctrl+H', 'hide', get_str('hideAllBoxDetail'), enabled=False)
        self.show_all_action = action(get_str('showAllBox'), partial(self.toggle_polygons, True),
                                     'Ctrl+A', 'hide', get_str('showAllBoxDetail'), enabled=False)
        
        # Auto saving action
        self.auto_saving = QAction(get_str('autoSaveMode'), self)
        self.auto_saving.setCheckable(True)
        self.auto_saving.setChecked(self.settings.get(SETTING_AUTO_SAVE, False))
        
        # Single class mode
        self.single_class_mode = QAction(get_str('singleClsMode'), self)
        self.single_class_mode.setShortcut("Ctrl+Shift+S")
        self.single_class_mode.setCheckable(True)
        self.single_class_mode.setChecked(self.settings.get(SETTING_SINGLE_CLASS, False))
        
        # Display label option
        self.display_label_option = QAction(get_str('displayLabel'), self)
        self.display_label_option.setShortcut("Ctrl+Shift+P")
        self.display_label_option.setCheckable(True)
        self.display_label_option.setChecked(self.settings.get(SETTING_PAINT_LABEL, False))
        self.display_label_option.triggered.connect(self.toggle_paint_labels_option)

        # Draw squares option
        self.draw_squares_option = QAction(get_str('drawSquares'), self)
        self.draw_squares_option.setShortcut('Ctrl+Shift+R')
        self.draw_squares_option.setCheckable(True)
        self.draw_squares_option.setChecked(self.settings.get(SETTING_DRAW_SQUARE, False))
        self.draw_squares_option.triggered.connect(self.toggle_draw_square)

    def _create_help_actions(self, action, get_str):
        """Create help-related actions."""
        self.help_default_action = action(get_str('tutorialDefault'), self.show_default_tutorial_dialog, 
                                         None, 'help', get_str('tutorialDetail'))
        self.show_info_action = action(get_str('info'), self.show_info_dialog, 
                                      None, 'help', get_str('info'))
        self.show_shortcut_action = action(get_str('shortcut'), self.show_shortcuts_dialog, 
                                          None, 'help', get_str('shortcut'))

    def _create_zoom_actions(self, action, get_str):
        """Create zoom-related actions."""
        self.zoom_widget_action = QWidgetAction(self)
        self.zoom_widget_action.setDefaultWidget(self.zoom_widget)
        self.zoom_widget.setWhatsThis(
            u"Zoom in or out of the image. Also accessible with"
            " %s and %s from the canvas." % (format_shortcut("Ctrl+[-+]"),
                                           format_shortcut("Ctrl+Wheel")))
        self.zoom_widget.setEnabled(False)

        self.zoom_in_action = action(get_str('zoomin'), partial(self.add_zoom, 10),
                                    'Ctrl++', 'zoom-in', get_str('zoominDetail'), enabled=False)
        self.zoom_out_action = action(get_str('zoomout'), partial(self.add_zoom, -10),
                                     'Ctrl+-', 'zoom-out', get_str('zoomoutDetail'), enabled=False)
        self.zoom_org_action = action(get_str('originalsize'), partial(self.set_zoom, 100),
                                     'Ctrl+=', 'zoom', get_str('originalsizeDetail'), enabled=False)
        self.fit_window_action = action(get_str('fitWin'), self.set_fit_window,
                                       'Ctrl+F', 'fit-window', get_str('fitWinDetail'),
                                       checkable=True, enabled=False)
        self.fit_width_action = action(get_str('fitWidth'), self.set_fit_width,
                                      'Ctrl+Shift+F', 'fit-width', get_str('fitWidthDetail'),
                                      checkable=True, enabled=False)
        
        # Group zoom controls
        self.zoom_actions = (self.zoom_widget, self.zoom_in_action, self.zoom_out_action,
                            self.zoom_org_action, self.fit_window_action, self.fit_width_action)
        
        # Zoom scalers
        self.scalers = {
            self.FIT_WINDOW: self.scale_fit_window,
            self.FIT_WIDTH: self.scale_fit_width,
            self.MANUAL_ZOOM: lambda: 1,
        }

    def _create_light_actions(self, action, get_str):
        """Create light adjustment actions."""
        self.light_widget_action = QWidgetAction(self)
        self.light_widget_action.setDefaultWidget(self.light_widget)
        self.light_widget.setWhatsThis(
            u"Brighten or darken current image. Also accessible with"
            " %s and %s from the canvas." % (format_shortcut("Ctrl+Shift+[-+]"),
                                           format_shortcut("Ctrl+Shift+Wheel")))
        self.light_widget.setEnabled(False)

        self.light_brighten_action = action(get_str('lightbrighten'), partial(self.add_light, 10),
                                           'Ctrl+Shift++', 'light_lighten', get_str('lightbrightenDetail'), enabled=False)
        self.light_darken_action = action(get_str('lightdarken'), partial(self.add_light, -10),
                                         'Ctrl+Shift+-', 'light_darken', get_str('lightdarkenDetail'), enabled=False)
        self.light_org_action = action(get_str('lightreset'), partial(self.set_light, 50),
                                      'Ctrl+Shift+=', 'light_reset', get_str('lightresetDetail'), checkable=True, enabled=False)
        self.light_org_action.setChecked(True)

        # Group light controls
        self.light_actions = (self.light_widget, self.light_brighten_action,
                             self.light_darken_action, self.light_org_action)

    def _create_shape_actions(self, action, get_str):
        """Create shape-related actions."""
        self.color1_action = action(get_str('boxLineColor'), self.choose_color1,
                                   'Ctrl+L', 'color_line', get_str('boxLineColorDetail'))
        self.shape_line_color_action = action(get_str('shapeLineColor'), self.choose_shape_line_color,
                                             icon='color_line', tip=get_str('shapeLineColorDetail'), enabled=False)
        self.shape_fill_color_action = action(get_str('shapeFillColor'), self.choose_shape_fill_color,
                                             icon='color', tip=get_str('shapeFillColorDetail'), enabled=False)

    def _create_mode_actions(self, action, get_str):
        """Create mode-related actions."""
        self.advanced_mode_action = action(get_str('advancedMode'), self.toggle_advanced_mode,
                                          'Ctrl+Shift+A', 'expert', get_str('advancedModeDetail'),
                                          checkable=True)
        self.create_mode_action = action(get_str('crtBox'), self.set_create_mode,
                                        'w', 'new', get_str('crtBoxDetail'), enabled=False)
        self.edit_mode_action = action(get_str('editBox'), self.set_edit_mode,
                                      'Ctrl+J', 'edit', get_str('editBoxDetail'), enabled=False)

    def _store_actions_and_create_menus(self, get_str):
        """Store actions in a struct and create menus."""
        # Store actions for further handling
        self.actions = Struct(
            save=self.save_action, save_format=self.save_format_action, saveAs=self.save_as_action, 
            open=self.open_action, close=self.close_action, resetAll=self.reset_all_action, 
            deleteImg=self.delete_image_action,
            lineColor=self.color1_action, create=self.create_action, delete=self.delete_action, 
            edit=self.edit_action, copy=self.copy_action,
            createMode=self.create_mode_action, editMode=self.edit_mode_action, 
            advancedMode=self.advanced_mode_action,
            shapeLineColor=self.shape_line_color_action, shapeFillColor=self.shape_fill_color_action,
            zoom=self.zoom_widget_action, zoomIn=self.zoom_in_action, zoomOut=self.zoom_out_action, 
            zoomOrg=self.zoom_org_action,
            fitWindow=self.fit_window_action, fitWidth=self.fit_width_action,
            zoomActions=self.zoom_actions,
            lightBrighten=self.light_brighten_action, lightDarken=self.light_darken_action, 
            lightOrg=self.light_org_action,
            lightActions=self.light_actions,
            fileMenuActions=(
                self.open_action, self.open_dir_action, self.save_action, self.save_as_action, 
                self.close_action, self.reset_all_action, self.quit_action),
            beginner=(), advanced=(),
            editMenu=(self.edit_action, self.copy_action, self.delete_action,
                     None, self.color1_action, self.draw_squares_option),
            beginnerContext=(self.create_action, self.edit_action, self.copy_action, self.delete_action),
            advancedContext=(self.create_mode_action, self.edit_mode_action, self.edit_action, 
                           self.copy_action, self.delete_action, self.shape_line_color_action, 
                           self.shape_fill_color_action),
            onLoadActive=(
                self.close_action, self.create_action, self.create_mode_action, self.edit_mode_action),
            onShapesPresent=(self.save_as_action, self.hide_all_action, self.show_all_action))

        # Create menus
        self._create_menus(get_str)

    def _create_menus(self, get_str):
        """Create all menus and populate them with actions."""
        # Label list context menu
        label_menu = QMenu()
        add_actions(label_menu, (self.edit_action, self.delete_action))
        self.label_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_list.customContextMenuRequested.connect(self.pop_label_list_menu)

        # Dock labels toggle
        labels = self.dock.toggleViewAction()
        labels.setText(get_str('showHide'))
        labels.setShortcut('Ctrl+Shift+L')

        # Create main menus
        self.menus = Struct(
            file=self.menu(get_str('menu_file')),
            edit=self.menu(get_str('menu_edit')),
            view=self.menu(get_str('menu_view')),
            help=self.menu(get_str('menu_help')),
            recentFiles=QMenu(get_str('menu_openRecent')),
            labelList=label_menu)

        # Populate menus
        add_actions(self.menus.file,
                   (self.open_action, self.open_dir_action, self.change_save_dir_action, 
                    self.open_annotation_action, self.copy_prev_bounding_action, self.menus.recentFiles, 
                    self.save_action, self.save_format_action, self.save_as_action, self.close_action, 
                    self.reset_all_action, self.delete_image_action, self.quit_action))
        
        add_actions(self.menus.help, (self.help_default_action, self.show_info_action, self.show_shortcut_action))
        
        add_actions(self.menus.view, (
            self.auto_saving,
            self.single_class_mode,
            self.display_label_option,
            labels, self.advanced_mode_action, None,
            self.hide_all_action, self.show_all_action, None,
            self.zoom_in_action, self.zoom_out_action, self.zoom_org_action, None,
            self.fit_window_action, self.fit_width_action, None,
            self.light_brighten_action, self.light_darken_action, self.light_org_action))

        self.menus.file.aboutToShow.connect(self.update_file_menu)

        # Canvas context menus
        add_actions(self.canvas.menus[0], self.actions.beginnerContext)
        add_actions(self.canvas.menus[1], (
            partial(new_action, self)('&Copy here', self.copy_shape),
            partial(new_action, self)('&Move here', self.move_shape)))

        # Create toolbar
        self._create_toolbar()

        # Set edit button default action
        if hasattr(self, 'edit_button'):
            self.edit_button.setDefaultAction(self.edit_action)

        self.statusBar().showMessage('%s started.' % self.__class__.__name__)
        self.statusBar().show()

    def _create_toolbar(self):
        """Create main toolbar with appropriate actions."""
        self.tools = self.toolbar('Tools')
        
        # Define toolbar actions for different modes
        self.actions.beginner = (
            self.open_action, self.open_dir_action, self.change_save_dir_action, 
            self.open_next_image_action, self.open_prev_image_action, self.verify_action, 
            self.save_action, self.save_format_action, None, self.create_action, 
            self.copy_action, self.delete_action, None,
            self.zoom_in_action, self.zoom_widget_action, self.zoom_out_action, 
            self.fit_window_action, self.fit_width_action, None,
            self.light_brighten_action, self.light_widget_action, self.light_darken_action, 
            self.light_org_action)

        self.actions.advanced = (
            self.open_action, self.open_dir_action, self.change_save_dir_action, 
            self.open_next_image_action, self.open_prev_image_action, self.save_action, 
            self.save_format_action, None,
            self.create_mode_action, self.edit_mode_action, None,
            self.hide_all_action, self.show_all_action)

    def update_file_menu(self):
        """Update the recent files menu."""
        import os
        curr_file_path = self.file_path

        def exists(filename):
            return os.path.exists(filename)
        
        menu = self.menus.recentFiles
        menu.clear()
        files = [f for f in self.recent_files if f != curr_file_path and exists(f)]
        
        for i, f in enumerate(files):
            icon = new_icon('labels')
            action = QAction(icon, '&%d %s' % (i + 1, QFileInfo(f).fileName()), self)
            action.triggered.connect(partial(self.load_recent, f))
            menu.addAction(action)

    def pop_label_list_menu(self, point):
        """Show context menu for label list."""
        self.menus.labelList.exec_(self.label_list.mapToGlobal(point))
