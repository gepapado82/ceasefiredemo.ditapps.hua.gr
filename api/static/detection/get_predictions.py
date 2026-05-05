import base64
import os

import cv2
import httpx
from matplotlib import pyplot as plt
from tqdm import tqdm

# folders = [
#     file
#     for file in os.listdir(
#         "/home/cani/Workspace/Ceasefire/ceasefire_demo/api/static/detection/original"
#     )
# ]

folders = [
    "/home/cani/Workspace/Ceasefire/ceasefire_demo/api/static/detection/original/class_9"
]

files = []
for folder in folders:
    files += [
        os.path.join(folder, file)
        for file in os.listdir(os.path.join("./original/", folder))
        if file.endswith(".jpg") or file.endswith(".png")
    ]

for file in tqdm(files):
    res = httpx.post(
        "http://localhost:8000/predict_vis2",
        files={"file": open(os.path.join("./original/", file), "rb")},
    )
    if res.status_code == 200:
        image_data = res.json()["base64_image"]
        image_data = base64.b64decode(image_data)
        labels = res.json()["labels"]
        confidences = res.json()["confidences"]
        boxes = res.json()["boxes"]

    os.makedirs(os.path.dirname("predictions/" + file), exist_ok=True)
    with open(("predictions/" + file), "wb") as f:
        f.write(image_data)

    with open(("predictions/" + file.replace(".png", ".txt")), "w") as f:
        for label, confidence, box in zip(labels, confidences, boxes):
            f.write(f"{label} {confidence} {' '.join(map(str, box))}\n")

    res = httpx.post(
        "http://localhost:8000/predict_vis_gt",
        files={"file": open(os.path.join("./original/", file), "rb")},
    )
    if res.status_code == 200:
        image_data = res.json()["base64_image"]
        image_data = base64.b64decode(image_data)
        labels = res.json()["labels"]
        boxes = res.json()["boxes"]

    os.makedirs(os.path.dirname("gt/" + file), exist_ok=True)
    with open(("gt/" + file), "wb") as f:
        f.write(image_data)

    with open(("gt/" + file.replace(".png", ".txt")), "w") as f:
        for label, box in zip(labels, boxes):
            f.write(f"{label} {' '.join(map(str, box))}\n")
