#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI initialization and widget creation for RedLabel MainWindow
"""
import sys

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

from libs.combobox import ComboBox
from libs.default_label_combobox import DefaultLabelComboBox
from libs.canvas import Canvas
from libs.zoomWidget import ZoomWidget
from libs.lightWidget import LightWidget
from libs.labelDialog import LabelDialog
from libs.colorDialog import ColorDialog
from libs.constants import *
from libs.utils import add_actions


class MainWindowUIMixin:
    """Mixin class for UI initialization and widget creation."""

    def init_ui_components(self):
        """Initialize all UI components and widgets."""
        get_str = self.get_str
        
        # Main dialog
        self.label_dialog = LabelDialog(parent=self, list_item=self.label_hist)

        # Create label panel layout
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)

        # Default label controls
        self._create_default_label_controls(list_layout, get_str)
        
        # Edit and difficulty controls  
        self._create_edit_controls(list_layout, get_str)
        
        # Label list and combo box
        self._create_label_list_controls(list_layout, get_str)
        
        # Create dock widgets
        self._create_dock_widgets(list_layout, get_str)
        
        # Create main canvas and scroll area
        self._create_canvas_and_scroll(get_str)
        
        # Connect canvas signals
        self._connect_canvas_signals()
        
        # Setup dock widget features
        self._setup_dock_features()

    def _create_default_label_controls(self, layout, get_str):
        """Create default label checkbox and combo box controls."""
        self.use_default_label_checkbox = QCheckBox(get_str('useDefaultLabel'))
        self.use_default_label_checkbox.setChecked(False)
        self.default_label_combo_box = DefaultLabelComboBox(self, items=self.label_hist)

        use_default_label_qhbox_layout = QHBoxLayout()
        use_default_label_qhbox_layout.addWidget(self.use_default_label_checkbox)
        use_default_label_qhbox_layout.addWidget(self.default_label_combo_box)
        use_default_label_container = QWidget()
        use_default_label_container.setLayout(use_default_label_qhbox_layout)
        
        layout.addWidget(use_default_label_container)

    def _create_edit_controls(self, layout, get_str):
        """Create edit button and difficulty checkbox controls."""
        self.diffc_button = QCheckBox(get_str('useDifficult'))
        self.diffc_button.setChecked(False)
        self.diffc_button.stateChanged.connect(self.button_state)
        
        self.edit_button = QToolButton()
        self.edit_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        layout.addWidget(self.edit_button)
        layout.addWidget(self.diffc_button)
        
        # YOLO inference section
        self._create_yolo_controls(layout)
        
        # Update YOLO button state
        self.update_yolo_inference_state()

    def _create_yolo_controls(self, layout):
        """Create YOLO inference controls."""
        yolo_group = QWidget()
        yolo_layout = QVBoxLayout(yolo_group)
        yolo_layout.setContentsMargins(4, 8, 4, 4)
        yolo_layout.setSpacing(4)
        
        # YOLO model selection
        yolo_model_layout = QHBoxLayout()
        yolo_model_layout.setSpacing(4)
        
        self.yolo_model_button = QPushButton("Select Model")
        self.yolo_model_button.clicked.connect(self.select_yolo_model)
        self.yolo_model_button.setToolTip("Select YOLO model for auto-annotation")
        
        self.yolo_model_label = QLabel("No model selected")
        self.yolo_model_label.setStyleSheet("color: #666; font-size: 11px;")
        self.yolo_model_label.setWordWrap(True)
        
        yolo_model_layout.addWidget(self.yolo_model_button)
        yolo_layout.addLayout(yolo_model_layout)
        yolo_layout.addWidget(self.yolo_model_label)
        
        # YOLO inference button
        self.yolo_inference_button = QPushButton("Run YOLO Inference")
        self.yolo_inference_button.clicked.connect(self.run_yolo_inference)
        self.yolo_inference_button.setEnabled(False)
        self.yolo_inference_button.setToolTip("Run YOLO inference on unlabeled images")
        
        yolo_layout.addWidget(self.yolo_inference_button)
        
        # Progress bar for inference
        self.yolo_progress = QProgressBar()
        self.yolo_progress.setVisible(False)
        yolo_layout.addWidget(self.yolo_progress)
        
        layout.addWidget(yolo_group)

    def _create_label_list_controls(self, layout, get_str):
        """Create label list and combo box for showing unique labels."""
        self.combo_box = ComboBox(self)
        layout.addWidget(self.combo_box)

        self.label_list = QListWidget()
        self.label_list.itemActivated.connect(self.label_selection_changed)
        self.label_list.itemSelectionChanged.connect(self.label_selection_changed)
        self.label_list.itemDoubleClicked.connect(self.edit_label)
        self.label_list.itemChanged.connect(self.label_item_changed)
        layout.addWidget(self.label_list)

    def _create_dock_widgets(self, list_layout, get_str):
        """Create and setup dock widgets for labels and file list."""
        # Label dock widget
        label_list_container = QWidget()
        label_list_container.setLayout(list_layout)
        self.dock = QDockWidget(get_str('boxLabelText'), self)
        self.dock.setObjectName(get_str('labels'))
        self.dock.setWidget(label_list_container)

        # File list dock widget
        self.file_list_widget = QListWidget()
        self.file_list_widget.itemDoubleClicked.connect(self.file_item_double_clicked)
        file_list_layout = QVBoxLayout()
        file_list_layout.setContentsMargins(0, 0, 0, 0)
        file_list_layout.addWidget(self.file_list_widget)
        file_list_container = QWidget()
        file_list_container.setLayout(file_list_layout)
        self.file_dock = QDockWidget(get_str('fileList'), self)
        self.file_dock.setObjectName(get_str('files'))
        self.file_dock.setWidget(file_list_container)

    def _create_canvas_and_scroll(self, get_str):
        """Create main canvas and scroll area components."""
        # Create utility widgets
        self.zoom_widget = ZoomWidget()
        self.light_widget = LightWidget(get_str('lightWidgetTitle'))
        self.color_dialog = ColorDialog(parent=self)

        # Create main canvas
        self.canvas = Canvas(parent=self)
        self.canvas.set_drawing_shape_to_square(self.settings.get(SETTING_DRAW_SQUARE, False))

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scroll_bars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.scroll_area = scroll

    def _connect_canvas_signals(self):
        """Connect all canvas-related signals."""
        self.canvas.zoomRequest.connect(self.zoom_request)
        self.canvas.lightRequest.connect(self.light_request)
        self.canvas.scrollRequest.connect(self.scroll_request)
        self.canvas.newShape.connect(self.new_shape)
        self.canvas.shapeMoved.connect(self.set_dirty)
        self.canvas.selectionChanged.connect(self.shape_selection_changed)
        self.canvas.drawingPolygon.connect(self.toggle_drawing_sensitive)

    def _setup_dock_features(self):
        """Setup main window layout and dock widget features."""
        self.setCentralWidget(self.scroll_area)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.file_dock)
        self.file_dock.setFeatures(QDockWidget.DockWidgetFloatable)

        self.dock_features = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        self.dock.setFeatures(self.dock.features() ^ self.dock_features)

    def complete_ui_setup(self, default_filename):
        """Complete UI setup and load initial files."""
        # Populate menus and connect final callbacks
        self.update_file_menu()
        self.zoom_widget.valueChanged.connect(self.paint_canvas)
        self.light_widget.valueChanged.connect(self.paint_canvas)
        self.populate_mode_actions()

        # Setup status bar coordinates display
        self.label_coordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.label_coordinates)

        # Load initial file/directory if specified
        import os
        from functools import partial
        if self.file_path and os.path.isdir(self.file_path):
            self.queue_event(partial(self.import_dir_images, self.file_path or ""))
            self.open_dir_dialog(dir_path=self.file_path, silent=True)
        elif self.file_path:
            self.queue_event(partial(self.load_file, self.file_path or ""))
        
        # Load last saved YOLO model (after UI is fully initialized)
        self._load_last_yolo_model()

    def toggle_actions(self, value=True):
        """Enable/Disable widgets which depend on an opened image."""
        for z in self.actions.zoomActions:
            z.setEnabled(value)
        for z in self.actions.lightActions:
            z.setEnabled(value)
        for action in self.actions.onLoadActive:
            action.setEnabled(value)

    def populate_mode_actions(self):
        """Populate toolbar and menu actions based on current mode."""
        if self.beginner():
            tool, menu = self.actions.beginner, self.actions.beginnerContext
        else:
            tool, menu = self.actions.advanced, self.actions.advancedContext
        self.tools.clear()
        add_actions(self.tools, tool)
        self.canvas.menus[0].clear()
        add_actions(self.canvas.menus[0], menu)
        self.menus.edit.clear()
        actions = (self.actions.create,) if self.beginner()\
            else (self.actions.createMode, self.actions.editMode)
        add_actions(self.menus.edit, actions + self.actions.editMenu)

    def toggle_advanced_mode(self, value=True):
        """Toggle between beginner and advanced UI modes."""
        self._beginner = not value
        self.canvas.set_editing(True)
        self.populate_mode_actions()
        self.edit_button.setVisible(not value)
        if value:
            self.actions.createMode.setEnabled(True)
            self.actions.editMode.setEnabled(False)
            self.dock.setFeatures(self.dock.features() | self.dock_features)
        else:
            self.dock.setFeatures(self.dock.features() ^ self.dock_features)
