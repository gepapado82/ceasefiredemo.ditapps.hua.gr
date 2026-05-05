import json
import os

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


def get_gt_labels(image_name=None):
    paths = [
        "/home/cani/Workspace/Ceasefire/ceasefire_demo/api/static/detection/test.json",
        "/home/cani/Workspace/Ceasefire/ceasefire_demo/api/static/detection/train.json",
        "/home/cani/Workspace/Ceasefire/ceasefire_demo/api/static/detection/val.json",
    ]

    if image_name is None:
        raise ValueError("Image name must be provided to get ground truth labels.")

    image_id = None
    gt_labels = None
    for path in paths:
        with open(path, "r") as f:
            gt_labels = json.load(f)
        for i, image in enumerate(gt_labels["images"]):
            if image["file_name"] == image_name:
                image_id = i
                break
        if image_id is not None:
            break

    if image_id is None:
        raise ValueError(f"Image '{image_name}' not found in any annotations file.")

    gathered_gt_labels = []
    for annotation in gt_labels["annotations"]:
        if annotation["image_id"] == image_id:
            gathered_gt_labels.append(
                {
                    "bbox": [
                        annotation["bbox"][0],
                        annotation["bbox"][1],
                        annotation["bbox"][0] + annotation["bbox"][2],
                        annotation["bbox"][1] + annotation["bbox"][3],
                    ],
                    "category_id": LABEL_MAP[annotation["category_id"]],
                }
            )

    if len(gathered_gt_labels) == 0:
        raise ValueError(f"No ground truth labels found for image '{image_name}'.")

    labels = [label["category_id"] for label in gathered_gt_labels]
    bboxes = [label["bbox"] for label in gathered_gt_labels]

    return (labels, bboxes)
