#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO Model Inference for RedLabel

This module provides YOLO model integration for automatic annotation,
including model detection, inference pipeline, and label generation.
"""

import os
import glob
from pathlib import Path

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *


class YOLOModelDetector:
    """Detect and manage YOLO model files (.pt) in the application directory."""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.available_models = []
        self.selected_model = None
        
    def scan_for_models(self):
        """Scan for YOLO model files (.pt) in the base directory."""
        model_pattern = os.path.join(self.base_dir, "*.pt")
        self.available_models = glob.glob(model_pattern)
        return self.available_models
    
    def has_models(self):
        """Check if any YOLO models are available."""
        return len(self.available_models) > 0
    
    def get_model_names(self):
        """Get list of model names (without full path)."""
        return [os.path.basename(model) for model in self.available_models]
    
    def set_selected_model(self, model_path):
        """Set the currently selected model."""
        if os.path.exists(model_path) and model_path.endswith('.pt'):
            self.selected_model = model_path
            return True
        return False
    
    def get_selected_model(self):
        """Get the currently selected model path."""
        return self.selected_model


class YOLOInferenceEngine:
    """Handle YOLO model inference and label generation."""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.is_ultralytics_available = self._check_ultralytics()
        
    def _check_ultralytics(self):
        """Check if ultralytics YOLO is available."""
        try:
            import ultralytics
            return True
        except ImportError:
            return False
    
    def load_model(self, model_path):
        """Load a YOLO model from the given path."""
        if not self.is_ultralytics_available:
            raise ImportError("ultralytics package is required for YOLO inference. Install with: pip install ultralytics")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.model_path = model_path
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
    
    def get_class_names(self):
        """Get the list of class names from the loaded model."""
        if self.model is None:
            raise RuntimeError("No model loaded. Call load_model() first.")
        
        # Get class names from the model
        return list(self.model.names.values())
    
    def predict_image(self, image_path, conf_threshold=0.25):
        """Run inference on a single image."""
        if self.model is None:
            raise RuntimeError("No model loaded. Call load_model() first.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            results = self.model(image_path, conf=conf_threshold)
            return self._parse_results(results[0])
        except Exception as e:
            raise RuntimeError(f"Inference failed for {image_path}: {e}")
    
    def _parse_results(self, result):
        """Parse YOLO results into standardized format."""
        detections = []
        
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            
            for i, (box, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)):
                x1, y1, x2, y2 = box
                class_name = result.names[cls_id] if cls_id < len(result.names) else f"class_{cls_id}"
                
                detection = {
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': float(conf),
                    'class_id': int(cls_id),
                    'class_name': class_name
                }
                detections.append(detection)
        
        return detections
    
    def get_class_names(self):
        """Get the class names from the loaded model."""
        if self.model is None:
            return []
        
        try:
            return list(self.model.names.values())
        except:
            return []


class YOLOInferenceWorker(QThread):
    """Worker thread for running YOLO inference on multiple images."""
    
    progress_updated = pyqtSignal(int)  # Current image index
    inference_completed = pyqtSignal(str, list)  # image_path, detections
    inference_failed = pyqtSignal(str, str)  # image_path, error_message
    finished_all = pyqtSignal()
    
    def __init__(self, inference_engine, image_paths, conf_threshold=0.25):
        super().__init__()
        self.inference_engine = inference_engine
        self.image_paths = image_paths
        self.conf_threshold = conf_threshold
        self._is_cancelled = False
    
    def cancel(self):
        """Cancel the inference process."""
        self._is_cancelled = True
    
    def run(self):
        """Run inference on all images."""
        for i, image_path in enumerate(self.image_paths):
            if self._is_cancelled:
                break
            
            try:
                detections = self.inference_engine.predict_image(image_path, self.conf_threshold)
                self.inference_completed.emit(image_path, detections)
            except Exception as e:
                self.inference_failed.emit(image_path, str(e))
            
            self.progress_updated.emit(i + 1)
        
        self.finished_all.emit()


class YOLOModelDialog(QDialog):
    """Dialog for selecting and configuring YOLO models."""
    
    def __init__(self, parent=None, model_detector=None):
        super().__init__(parent)
        self.model_detector = model_detector or YOLOModelDetector()
        self.selected_model_path = None
        self.confidence_threshold = 0.25
        
        self.setWindowTitle("YOLO Model Configuration")
        self.setModal(True)
        self.resize(500, 300)
        
        self._setup_ui()
        self._populate_models()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Configure YOLO Model for Auto-Annotation")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Model selection section
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout(model_group)
        
        # Available models list
        self.model_list = QListWidget()
        self.model_list.itemSelectionChanged.connect(self._on_model_selected)
        model_layout.addWidget(QLabel("Available Models:"))
        model_layout.addWidget(self.model_list)
        
        # Browse button for external models
        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse for Model...")
        self.browse_button.clicked.connect(self._browse_model)
        browse_layout.addWidget(self.browse_button)
        browse_layout.addStretch()
        model_layout.addLayout(browse_layout)
        
        layout.addWidget(model_group)
        
        # Configuration section
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout(config_group)
        
        # Confidence threshold
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.01, 1.0)
        self.confidence_spin.setValue(0.25)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setDecimals(2)
        config_layout.addRow("Confidence Threshold:", self.confidence_spin)
        
        layout.addWidget(config_group)
        
        # Selected model info
        self.info_label = QLabel("No model selected")
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
    
    def _populate_models(self):
        """Populate the model list with available models."""
        self.model_detector.scan_for_models()
        model_names = self.model_detector.get_model_names()
        
        self.model_list.clear()
        for model_name in model_names:
            self.model_list.addItem(model_name)
        
        if not model_names:
            item = QListWidgetItem("No models found in application directory")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.model_list.addItem(item)
    
    def _on_model_selected(self):
        """Handle model selection from the list."""
        current_item = self.model_list.currentItem()
        if current_item and current_item.flags() & Qt.ItemIsSelectable:
            model_name = current_item.text()
            model_path = None
            
            for path in self.model_detector.available_models:
                if os.path.basename(path) == model_name:
                    model_path = path
                    break
            
            if model_path:
                self.selected_model_path = model_path
                self.info_label.setText(f"Selected: {model_name}")
                self.ok_button.setEnabled(True)
    
    def _browse_model(self):
        """Browse for a model file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select YOLO Model", 
            "", 
            "YOLO Models (*.pt);;All Files (*)"
        )
        
        if file_path:
            self.selected_model_path = file_path
            model_name = os.path.basename(file_path)
            self.info_label.setText(f"Selected: {model_name}")
            self.ok_button.setEnabled(True)
            
            # Add to list if not already there
            for i in range(self.model_list.count()):
                if self.model_list.item(i).text() == model_name:
                    break
            else:
                self.model_list.addItem(model_name)
                self.model_list.setCurrentRow(self.model_list.count() - 1)
    
    def get_selected_model(self):
        """Get the selected model path."""
        return self.selected_model_path
    
    def get_confidence_threshold(self):
        """Get the confidence threshold value."""
        return self.confidence_spin.value()
