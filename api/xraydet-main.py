import os
import io
from typing import Annotated, List

from fastapi import FastAPI, File, UploadFile
from starlette.responses import StreamingResponse, Response

from pydantic_models.detection import Detection, DetectionObject
from utils.iterable import transform_to_iterable, transform_to_iterable_of_iterables

from PIL import Image
import numpy as np
from mmdet.apis import DetInferencer

app = FastAPI()

inferencer = DetInferencer(
    model="./model/DINO.py",
    weights="./model/best.pth",
)


@app.post("/predict")
async def predict(files: list[UploadFile]):
    images = []
    for file in files:
        image_to_predict = np.asarray(Image.open(file.file))
        # image_to_predict = cv2.imdecode()
        images.append(image_to_predict)

    # Check if images are 3-dimensional, else make them
    for idx, image in enumerate(images):
        try:
            assert image.shape[2]
        except IndexError:
            images[idx] = image.reshape(image.shape[0], image.shape[1], 1)
            images[idx] = np.concatenate([image, image, image], axis=-1)

    batch_size = len(images)

    # start = time.time()
    preds = inferencer(
        images,
        batch_size=batch_size,
        # out_dir="./model/output/",
        # return_datasamples=True,
        # return_vis=True,
        # no_save_pred=False,
    )
    # end = time.time()

    outputs = {
        # "time": -1,
        "results": []
    }
    for idx, pred in enumerate(preds["predictions"]):
        scores = np.array(pred["scores"])
        detections_indices = np.argwhere(scores >= 0.5)

        if len(detections_indices) == 0:
            outputs["results"].append(
                Detection(
                    imageName=files[idx].filename,
                    detections=[DetectionObject(
                        bbox=[], predicted_class=-1, confidence=-1.0)]
                )
            )
            continue

        confidences = scores[detections_indices].squeeze().tolist()
        labels = np.array(pred["labels"])[
            detections_indices].squeeze().tolist()
        bboxes = np.array(pred["bboxes"])[
            detections_indices].squeeze().tolist()

        bboxes = transform_to_iterable_of_iterables(bboxes)
        labels = transform_to_iterable(labels)
        confidences = transform_to_iterable(confidences)

        print(f"File: {files[idx].filename}")
        print(
            f"BBoxes: {bboxes}, Labels: {labels}, Confidences: {confidences}")

        outputs["results"].append(
            Detection(
                imageName=files[idx].filename,
                detections=[DetectionObject(bbox=bbox, predicted_class=predicted_class, confidence=confidence)
                            for bbox, predicted_class, confidence in zip(bboxes, labels, confidences)]
            )
        )
    # outputs["time"] = end - start
    return outputs
