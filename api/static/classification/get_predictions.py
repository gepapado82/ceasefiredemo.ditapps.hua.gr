import base64
import os

import cv2
import httpx
from matplotlib import pyplot as plt
from tqdm import tqdm

folders = [
    file
    for file in os.listdir(
        "original"
    )
]

files = []
for folder in folders:
    files += [
        os.path.join(folder, file)
        for file in os.listdir(os.path.join("./original/", folder))
        if file.endswith(".jpg") or file.endswith(".png")
    ]

print(f"[\x1b[1;31mDEBUG\x1b[0m] file: {files[0]}")

for file in tqdm(files):
    res = httpx.post(
        "http://localhost:8000/classify",
        files={"files": open(os.path.join("./original/", file), "rb")},
    )

    if res.status_code == 200:
        results = res.json()["results"][0]
        predicted_label = results["predicted_label"]
        confidence = results["confidence"]
        entropy = results["entropy"]
        top_5_labels = results["top_5_labels"]

    os.makedirs(os.path.dirname("predictions/" + file), exist_ok=True)
    with open(("predictions/" + file.replace(".jpg", ".txt")), "w") as f:
        f.write(f"{predicted_label} {confidence} {entropy}\n")
        for top_5_label in top_5_labels:
            f.write(f"{top_5_label[0]} {top_5_label[1]}\n")
