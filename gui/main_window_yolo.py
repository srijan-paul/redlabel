#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO inference functionality for RedLabel MainWindow
"""
import os
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

from libs.yolo_inference import YOLOModelDialog, YOLOInferenceWorker
from libs.constants import *


class MainWindowYOLOMixin:
    """Mixin class for YOLO inference functionality."""

    def select_yolo_model(self):
        """Open dialog to select YOLO model."""
        dialog = YOLOModelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_model = dialog.get_selected_model()
            if selected_model:
                self._load_yolo_model(selected_model)

    def _load_yolo_model(self, model_path):
        """Load YOLO model and update UI."""
        try:
            self.yolo_inference_engine.load_model(model_path)
            self.selected_yolo_model = model_path
            
            # Update UI
            model_name = os.path.basename(model_path)
            self.yolo_model_label.setText(f"Model: {model_name}")
            self.yolo_model_label.setStyleSheet("color: #0066cc; font-size: 11px;")
            
            # Save to settings
            self.settings[SETTING_YOLO_MODEL_PATH] = model_path
            self.settings.save()
            
            # Update inference button state
            self.update_yolo_inference_state()
            
            self.statusBar().showMessage(f"Loaded YOLO model: {model_name}", 3000)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Model Load Error", 
                f"Failed to load YOLO model:\n{str(e)}"
            )
            self.selected_yolo_model = None
            self.yolo_model_label.setText("No model selected")
            self.yolo_model_label.setStyleSheet("color: #666; font-size: 11px;")
            self.update_yolo_inference_state()

    def update_yolo_inference_state(self):
        """Update YOLO inference button enabled state."""
        has_model = self.selected_yolo_model is not None
        has_images = bool(self.m_img_list)
        has_save_dir = self.default_save_dir is not None
        has_unlabeled = bool(self._get_unlabeled_images()) if has_images and has_save_dir else False
        
        # Enable button only if we have model, images, save dir, and unlabeled images
        enabled = has_model and has_images and has_save_dir and has_unlabeled
        self.yolo_inference_button.setEnabled(enabled)
        
        # Update tooltip
        if not has_model:
            tooltip = "Select a YOLO model first"
        elif not has_save_dir:
            tooltip = "Set a save directory first"
        elif not has_images:
            tooltip = "Load image directory first"
        elif not has_unlabeled:
            tooltip = "No unlabeled images found"
        else:
            tooltip = "Run YOLO inference on unlabeled images"
        
        self.yolo_inference_button.setToolTip(tooltip)

    def _has_labels_txt(self):
        """Check if classes.txt exists in the save directory (for YOLO format)."""
        if not self.default_save_dir:
            return False
        classes_path = os.path.join(self.default_save_dir, "classes.txt")
        return os.path.exists(classes_path)

    def _load_last_yolo_model(self):
        """Load the last saved YOLO model from settings."""
        last_model_path = self.settings.get(SETTING_YOLO_MODEL_PATH, None)
        if last_model_path and os.path.exists(last_model_path):
            try:
                self.yolo_inference_engine.load_model(last_model_path)
                self.selected_yolo_model = last_model_path
                model_name = os.path.basename(last_model_path)
                self.yolo_model_label.setText(f"Model: {model_name}")
                self.yolo_model_label.setStyleSheet("color: #0066cc; font-size: 11px;")
                self.update_yolo_inference_state()
            except Exception as e:
                # Model failed to load, clear from settings
                self.settings[SETTING_YOLO_MODEL_PATH] = ''

    def _ensure_classes_txt(self):
        """Ensure classes.txt exists in save directory, create from model if missing."""
        if not self.default_save_dir:
            QMessageBox.warning(self, "No Save Directory", "Please set a save directory first.")
            return False
        
        classes_path = os.path.join(self.default_save_dir, "classes.txt")
        
        # If classes.txt already exists, we're good
        if os.path.exists(classes_path):
            return True
        
        # Try to create classes.txt from the loaded YOLO model
        try:
            class_names = self.yolo_inference_engine.get_class_names()
            
            # Write class names to classes.txt
            with open(classes_path, 'w') as f:
                for class_name in class_names:
                    f.write(f"{class_name}\n")
            
            self.statusBar().showMessage(f"Created classes.txt with {len(class_names)} classes from model", 3000)
            return True
            
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Classes File Error", 
                f"Could not create classes.txt from model:\n{str(e)}\n\n"
                f"Please create a classes.txt file in:\n{self.default_save_dir}"
            )
            return False

    def run_yolo_inference(self):
        """Run YOLO inference on all unlabeled images."""
        if not self.selected_yolo_model:
            QMessageBox.warning(self, "No Model", "Please select a YOLO model first.")
            return
        
        # Get list of images without corresponding label files
        unlabeled_images = self._get_unlabeled_images()
        
        if not unlabeled_images:
            QMessageBox.information(self, "No Images", "All images in the directory already have label files.")
            return
        
        # Ensure classes.txt exists (create it from model if missing)
        if not self._ensure_classes_txt():
            return
        
        # Confirm inference
        reply = QMessageBox.question(
            self, 
            "Run YOLO Inference", 
            f"Run YOLO inference on {len(unlabeled_images)} unlabeled images?\n\n"
            f"Model: {os.path.basename(self.selected_yolo_model)}\n"
            f"Confidence: {getattr(self, 'confidence_threshold', 0.25)}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._start_yolo_inference(unlabeled_images)

    def _get_unlabeled_images(self):
        """Get list of images that don't have corresponding label files."""
        if not self.m_img_list or not self.default_save_dir:
            return []
        
        unlabeled = []
        for img_path in self.m_img_list:
            # Get corresponding label file path
            img_name = os.path.splitext(os.path.basename(img_path))[0]
            label_path = os.path.join(self.default_save_dir, f"{img_name}.txt")
            
            if not os.path.exists(label_path):
                unlabeled.append(img_path)
        
        return unlabeled

    def _start_yolo_inference(self, image_paths):
        """Start YOLO inference in a background thread."""
        confidence = getattr(self, 'confidence_threshold', 0.25)
        
        # Setup progress bar
        self.yolo_progress.setVisible(True)
        self.yolo_progress.setRange(0, len(image_paths))
        self.yolo_progress.setValue(0)
        
        # Disable inference button during processing
        self.yolo_inference_button.setEnabled(False)
        self.yolo_inference_button.setText("Running Inference...")
        
        # Create and start worker thread
        self.yolo_worker = YOLOInferenceWorker(
            self.yolo_inference_engine, 
            image_paths, 
            confidence
        )
        
        # Connect signals
        self.yolo_worker.progress_updated.connect(self.yolo_progress.setValue)
        self.yolo_worker.inference_completed.connect(self._on_inference_completed)
        self.yolo_worker.inference_failed.connect(self._on_inference_failed)
        self.yolo_worker.finished_all.connect(self._on_inference_finished)
        
        self.yolo_worker.start()
        
        self.statusBar().showMessage("Running YOLO inference...")

    def _on_inference_completed(self, image_path, detections):
        """Handle completed inference for a single image."""
        if detections:
            # Create label file for this image
            self._create_yolo_label_file(image_path, detections)
            
            # If this is the current image, update the canvas
            if image_path == self.file_path:
                self._load_yolo_labels_for_current_image()

    def _on_inference_failed(self, image_path, error_message):
        """Handle failed inference for a single image."""
        print(f"Inference failed for {image_path}: {error_message}")

    def _on_inference_finished(self):
        """Handle completion of all inference tasks."""
        # Reset UI state
        self.yolo_progress.setVisible(False)
        self.yolo_inference_button.setEnabled(True)
        self.yolo_inference_button.setText("Run YOLO Inference")
        self.update_yolo_inference_state()
        
        # Update status
        self.statusBar().showMessage("YOLO inference completed", 3000)
        
        # Refresh current image if it was processed
        if hasattr(self, 'file_path') and self.file_path:
            self.load_file(self.file_path)

    def _create_yolo_label_file(self, image_path, detections):
        """Create YOLO format label file from detections."""
        if not self.default_save_dir or not detections:
            return
        
        # Get image dimensions
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img_width, img_height = img.size
        except ImportError:
            # Fallback to QImage if PIL not available
            img = QImage(image_path)
            img_width, img_height = img.width(), img.height()
        
        # Load class names from classes.txt
        classes_path = os.path.join(self.default_save_dir, "classes.txt")
        class_names = []
        if os.path.exists(classes_path):
            with open(classes_path, 'r') as f:
                class_names = [line.strip() for line in f.readlines()]
        
        # Create YOLO format lines
        yolo_lines = []
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            
            # Get class index
            if class_name in class_names:
                class_idx = class_names.index(class_name)
            else:
                # Add new class to classes.txt
                class_names.append(class_name)
                class_idx = len(class_names) - 1
                with open(classes_path, 'a') as f:
                    f.write(f"{class_name}\n")
            
            # Convert to YOLO format (normalized)
            x_center = (x1 + x2) / 2.0 / img_width
            y_center = (y1 + y2) / 2.0 / img_height
            width = (x2 - x1) / img_width
            height = (y2 - y1) / img_height
            
            yolo_lines.append(f"{class_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
        # Save label file
        img_name = os.path.splitext(os.path.basename(image_path))[0]
        label_file_path = os.path.join(self.default_save_dir, f"{img_name}.txt")
        
        with open(label_file_path, 'w') as f:
            f.write('\n'.join(yolo_lines))

    def _load_yolo_labels_for_current_image(self):
        """Load YOLO labels for the current image and update canvas."""
        if not self.file_path or not self.default_save_dir:
            return
        
        img_name = os.path.splitext(os.path.basename(self.file_path))[0]
        label_path = os.path.join(self.default_save_dir, f"{img_name}.txt")
        
        if os.path.exists(label_path):
            self.load_yolo_txt_by_filename(label_path)
