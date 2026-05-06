import os
import httpx
from tqdm import tqdm

# Define your base directories clearly
BASE_ORIGINAL_DIR = "./original/"
BASE_PREDICTIONS_DIR = "./predictions/"

# 1. Get folders dynamically from the relative path to avoid hardcoded absolute path errors
folders = [f for f in os.listdir(BASE_ORIGINAL_DIR) if os.path.isdir(os.path.join(BASE_ORIGINAL_DIR, f))]

files = []
for folder in folders:
    folder_path = os.path.join(BASE_ORIGINAL_DIR, folder)
    files += [
        os.path.join(folder, file)
        for file in os.listdir(folder_path)
        if file.lower().endswith(".jpg") or file.lower().endswith(".png")
    ]

if not files:
    print("[\x1b[1;31mDEBUG\x1b[0m] No images found!")
    exit()

print(f"[\x1b[1;32mDEBUG\x1b[0m] Found {len(files)} images. First file: {files[0]}")

# 2. Process images
for file in tqdm(files):
    image_path = os.path.join(BASE_ORIGINAL_DIR, file)
    
    try:
        with open(image_path, "rb") as img_file:
            res = httpx.post(
                "http://localhost:8000/classify",
                files={"files": img_file},
                timeout=30.0 # Added a timeout so the script doesn't hang forever
            )

        # 3. Only write the file IF the API succeeded
        if res.status_code == 200:
            results = res.json()["results"][0]
            predicted_label = results["predicted_label"]
            confidence = results["confidence"]
            entropy = results["entropy"]
            top_5_labels = results["top_5_labels"]

            # 4. Safely swap ANY extension (.jpg, .jpeg, .png) to .txt
            file_name_without_ext = os.path.splitext(file)[0]
            txt_file_path = os.path.join(BASE_PREDICTIONS_DIR, f"{file_name_without_ext}.txt")

            os.makedirs(os.path.dirname(txt_file_path), exist_ok=True)
            
            with open(txt_file_path, "w") as f:
                f.write(f"{predicted_label} {confidence} {entropy}\n")
                for top_5_label in top_5_labels:
                    f.write(f"{top_5_label[0]} {top_5_label[1]}\n")
        else:
            print(f"\n[\x1b[1;31mERROR\x1b[0m] API failed for {file} with status {res.status_code}")

    except Exception as e:
        print(f"\n[\x1b[1;31mERROR\x1b[0m] Failed to process {file}: {str(e)}")

'''
import base64
import os

import cv2
import httpx
from matplotlib import pyplot as plt
from tqdm import tqdm

folders = [
    file
    for file in os.listdir(
        "/home/cani/Workspace/Ceasefire/ceasefire_demo/api/static/classification/original"
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

'''
