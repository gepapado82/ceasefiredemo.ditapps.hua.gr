from api.utils.labels import classification_labels, obj_det_labels
import os
import shutil

for label in classification_labels:
    os.makedirs(f"static_uploads/classifcation/{label}", exist_ok=True)

for label in obj_det_labels:
    os.makedirs(f"static_uploads/detection/{label}", exist_ok=True)
