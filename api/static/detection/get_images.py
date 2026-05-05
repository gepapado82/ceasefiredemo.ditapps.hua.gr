import json
import os
import shutil
from collections import defaultdict

images_path = "/home/cani/Workspace/Ceasefire/ceasefire/Datasets/CFray_v2.1/images/"
test_annotations_path = (
    "/home/cani/Workspace/Ceasefire/ceasefire/Datasets/CFray_v2.1/annotations/test.json"
)

with open(test_annotations_path, "r") as f:
    test_annotations = json.load(f)

test_images = test_annotations["images"]
test_annotations = test_annotations["annotations"]

LABEL_MAP = {
    0: 0,
    1: 3,
    2: 4,
    3: 6,
    4: 8,
    5: 5,
    6: 2,
    7: 7,
    9: 1,
}


def get_n_images_per_class(images, annotations, label_map, n):
    # Map category_id to image_ids
    class_to_images = defaultdict(list)
    image_id_to_file = {img["id"]: img["file_name"] for img in images}

    for ann in annotations:
        mapped_class = label_map.get(ann["category_id"])
        if mapped_class is not None:
            class_to_images[mapped_class].append(ann["image_id"])

    # For each class, get up to n unique image file names and copy them
    result = {}
    for cls, image_ids in class_to_images.items():
        unique_ids = list(dict.fromkeys(image_ids))  # preserve order, remove duplicates
        selected_files = [
            image_id_to_file[iid] for iid in unique_ids[:n] if iid in image_id_to_file
        ]
        result[cls] = selected_files

        # Create class directory if it doesn't exist
        class_dir = f"./original/class_{cls}"
        os.makedirs(class_dir, exist_ok=True)

        # Copy images to their respective class folders
        for file_name in selected_files:
            src_path = os.path.join(images_path, file_name)
            dst_path = os.path.join(class_dir, file_name)
            shutil.copy2(src_path, dst_path)

    return result


get_n_images_per_class(test_images, test_annotations, LABEL_MAP, 30)
