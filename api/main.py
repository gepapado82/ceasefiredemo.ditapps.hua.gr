import base64
import io
import os

import cv2
import numpy as np
from dino.dino_inferencer import ViTInferencer
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from mmdet.apis import DetInferencer
from PIL import Image, UnidentifiedImageError
from pydantic_models.detection import Detection, DetectionObject
from pydantic_models.response import DetResponse
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import preprocess_image, show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from torch import from_numpy, tensor, topk
from torch.distributions import Categorical
from utils.draw_boxes import draw_boxes
from utils.get_gt_labels import get_gt_labels
from utils.iterable import transform_to_iterable, transform_to_iterable_of_iterables
from utils.labels import id_to_label, label_to_id

app = FastAPI(
    # docs_url=None,
    redoc_url=None
)

origins = [
    # "http://localhost:9000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

classification_inferencer = ViTInferencer(model_path="./model/vit-s_finetuned.pth.tar")


# def reshape_transform(tensor, height=16, width=16):
#     result = tensor[:, 1:, :].reshape(tensor.size(0), height, width, tensor.size(2))

#     # Bring the channels to the first dimension,
#     # like in CNNs.
#     result = result.transpose(2, 3).transpose(1, 2)
#     return result


# grad_cam = GradCAM(
#     classification_inferencer.model,
#     target_layers=[classification_inferencer.model.blocks[-1].norm1],
#     reshape_transform=reshape_transform,
# )


object_detection_inferencer = DetInferencer(
    model="./model/swin-b_dino_cfray_updated.py",
    weights="./model/swin-b_dino_cfray_updated.pth",
)


@app.post("/classify")
async def classify(files: list[UploadFile]):
    images = []
    for file in files:
        # image_to_predict = np.asarray(Image.open(file.file))
        image_to_predict = np.frombuffer(file.file.read(), dtype=np.uint8)
        image_to_predict = cv2.imdecode(image_to_predict, cv2.IMREAD_COLOR)
        image_to_predict = cv2.cvtColor(image_to_predict, cv2.COLOR_BGR2RGB)
        image_to_predict = np.array(image_to_predict)
        images.append(image_to_predict)

    predictions = classification_inferencer(images)

    outputs = {
        # "time": -1,
        "results": []
    }
    for idx, prediction in enumerate(predictions):
        # First item in the prediction list seems to be the one with the
        # highest confidence
        result = {
            "image_name": files[idx].filename,
            "predicted_label": prediction["predicted_label"],
            "confidence": prediction["confidence"],
        }

        softmax_activations = prediction["scores"]
        result["entropy"] = (
            Categorical(probs=tensor(softmax_activations).to("cuda:0")).entropy().item()
        )

        top_5_indices = topk(tensor(softmax_activations), 5).indices.tolist()
        top_5_labels = []
        for top5_idx in top_5_indices:
            top_5_labels.append(
                (
                    id_to_label("classification", top5_idx),
                    round(softmax_activations[top5_idx] * 100, 2),
                )
            )
        result["top_5_labels"] = top_5_labels

        # result["viz"] = show_cam_on_image(
        #     images[idx],
        #     grad_cam(
        #         input_tensor=preprocess_image(images[idx].astype(np.float32) / 255),
        #         targets=None,
        #     ),
        # )

        outputs["results"].append(result)

        # print(f"\nPrediction: {prediction}")
    # outputs["time"] = end - start
    print(f"[\x1b[1;31mDEBUG\x1b[0m] Outputs: {outputs}")
    return outputs


@app.post("/classify_static")
async def classify_static(file: UploadFile, num_images: int):
    images = []
    image = np.frombuffer(file.file.read(), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.array(image)
    images.append(image)

    predictions = classification_inferencer(images)

    predicted_label = -1
    for _, prediction in enumerate(predictions):
        predicted_label = prediction["predicted_label"]

    class_to_return = predicted_label
    static_dir = f"./static/classification/class_{class_to_return}"
    static_files = list(
        map(lambda x: f"{static_dir.removeprefix('./')}/{x}", os.listdir(static_dir))
    )

    try:
        files = np.random.choice(static_files, num_images).tolist()
    except:
        files = []
    print(f"[\x1b[1;31mDEBUG\x1b[0m] Files: {files}")
    return JSONResponse(content={"files": files})


@app.post("/predict")
async def predict(file: UploadFile):
    try:
        image_to_predict = np.frombuffer(file.file.read(), dtype=np.uint8)
        image_to_predict = cv2.imdecode(image_to_predict, cv2.IMREAD_COLOR)
        # image_to_predict = cv2.cvtColor(image_to_predict, cv2.COLOR_BGR2RGB)
        image_to_predict = np.array(image_to_predict)
    except UnidentifiedImageError as e:
        # print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid image format")

    # batch_size = min(len(images), 6)

    print(f"[\x1b[1;31mDEBUG\x1b[0m] Image shape: {image_to_predict.shape}")

    # start = time.time()
    preds = object_detection_inferencer(
        image_to_predict,
        batch_size=1,
        # out_dir="./model/output/",
        # return_datasamples=True,
        # return_vis=True,
        # no_save_pred=False,
    )
    # end = time.time()

    outputs = {
        # "time": -1,
        "results": [],
    }
    negatives = 0
    for idx, pred in enumerate(preds["predictions"]):
        scores = np.array(pred["scores"])
        detections_indices = np.argwhere(scores >= 0.5)

        if len(detections_indices) == 0:
            outputs["results"].append(
                Detection(
                    imageName=file.filename,
                    detections=[
                        DetectionObject(bbox=[], predicted_class=-1, confidence=-1.0)
                    ],
                )
            )
            negatives += 1
            continue

        confidences = scores[detections_indices].squeeze().tolist()
        labels = np.array(pred["labels"])[detections_indices].squeeze().tolist()
        bboxes = np.array(pred["bboxes"])[detections_indices].squeeze().tolist()

        bboxes = transform_to_iterable_of_iterables(bboxes)
        labels = transform_to_iterable(labels)
        confidences = transform_to_iterable(confidences)

        # print(f"File: {files[idx].filename}")
        # print(f"BBoxes: {bboxes}, Labels: {labels}, Confidences: {confidences}")

        outputs["results"].append(
            Detection(
                imageName=file.filename,
                detections=[
                    DetectionObject(
                        bbox=bbox,
                        predicted_class=predicted_class,
                        confidence=confidence,
                    )
                    for bbox, predicted_class, confidence in zip(
                        bboxes, labels, confidences
                    )
                ],
            )
        )
    # outputs["time"] = end - start

    print(f"[\x1b[1;31mDEBUG\x1b[0m] Found {len(outputs['results'])} detections")

    return DetResponse(**outputs)


@app.post("/predict_vis")
async def predict_vis(file: UploadFile, request: Request = None):
    image = np.frombuffer(file.file.read(), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.array(image)

    # try:
    #     image = np.asarray(Image.open(file.file).convert("RGB"))
    # except UnidentifiedImageError as e:
    #     raise HTTPException(status_code=400, detail="Invalid image format")

    try:
        assert image.shape[2]
    except IndexError:
        image = image.reshape(image.shape[0], image.shape[1], 1)
        image = np.concatenate([image, image, image], axis=-1)

    pred = object_detection_inferencer(image)

    # print(f"[\x1b[1;31mDEBUG\x1b[0m] After prediction")

    for preds in pred["predictions"]:
        scores = np.array(preds["scores"])
        detections_indices = np.argwhere(scores >= 0.5)

        if len(detections_indices) == 0:
            bboxes = []
            labels = []
            confidences = []
            break
            return draw_boxes(image, [], [])

        confidences = scores[detections_indices].squeeze().tolist()
        labels = np.array(preds["labels"])[detections_indices].squeeze().tolist()
        bboxes = np.array(preds["bboxes"])[detections_indices].squeeze().tolist()

        bboxes = transform_to_iterable_of_iterables(bboxes)
        labels = transform_to_iterable(labels)
        confidences = transform_to_iterable(confidences)

    # print(f"[\x1b[1;31mDEBUG\x1b[0m] Before base64 conversion")

    print(f"[\x1b[1;31mDEBUG\x1b[0m] Predictions: {labels}, {confidences}")

    image_with_boxes = draw_boxes(image, bboxes, labels).convert("RGBA")
    temp = io.BytesIO()
    image_with_boxes.save(temp, format="PNG")
    temp.seek(0)
    temp_bytes = temp.read()
    encoding = base64.b64encode(temp_bytes).decode("utf-8")
    return JSONResponse(
        content={
            "base64_image": encoding,
            "labels": labels,
            "confidences": confidences,
        }
    )


@app.post("/predict_vis2")
async def predict_vis2(file: UploadFile, request: Request = None):
    image = np.frombuffer(file.file.read(), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.array(image)

    # try:
    #     image = np.asarray(Image.open(file.file).convert("RGB"))
    # except UnidentifiedImageError as e:
    #     raise HTTPException(status_code=400, detail="Invalid image format")

    try:
        assert image.shape[2]
    except IndexError:
        image = image.reshape(image.shape[0], image.shape[1], 1)
        image = np.concatenate([image, image, image], axis=-1)

    pred = object_detection_inferencer(image)

    # print(f"[\x1b[1;31mDEBUG\x1b[0m] After prediction")

    for preds in pred["predictions"]:
        scores = np.array(preds["scores"])
        detections_indices = np.argwhere(scores >= 0.5)

        if len(detections_indices) == 0:
            bboxes = []
            labels = []
            confidences = []
            break
            return draw_boxes(image, [], [])

        confidences = scores[detections_indices].squeeze().tolist()
        labels = np.array(preds["labels"])[detections_indices].squeeze().tolist()
        bboxes = np.array(preds["bboxes"])[detections_indices].squeeze().tolist()

        bboxes = transform_to_iterable_of_iterables(bboxes)
        labels = transform_to_iterable(labels)
        confidences = transform_to_iterable(confidences)

    image_with_boxes = draw_boxes(image, boxes=bboxes, labels=labels)

    temp = io.BytesIO()
    image_with_boxes.save(temp, format="PNG")
    temp.seek(0)
    temp_bytes = temp.read()
    encoding = base64.b64encode(temp_bytes).decode("utf-8")
    return JSONResponse(
        content={
            "base64_image": encoding,
            "labels": labels,
            "confidences": confidences,
            "boxes": bboxes,
        }
    )


@app.post("/predict_vis_gt")
async def predict_vis_gt(file: UploadFile, request: Request = None):
    image = np.frombuffer(file.file.read(), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.array(image)

    gt_labels, gt_bboxes = get_gt_labels(image_name=file.filename)
    image_with_gt_boxes = draw_boxes(image, gt_boxes=gt_bboxes, gt_labels=gt_labels)

    temp = io.BytesIO()
    image_with_gt_boxes.save(temp, format="PNG")
    temp.seek(0)
    temp_bytes = temp.read()
    encoding = base64.b64encode(temp_bytes).decode("utf-8")
    return JSONResponse(
        content={
            "base64_image": encoding,
            "labels": gt_labels,
            "boxes": gt_bboxes,
        }
    )


@app.post("/predict_static")
async def predict_static(file: UploadFile, num_images: int):
    try:
        image_to_predict = np.frombuffer(file.file.read(), dtype=np.uint8)
        image_to_predict = cv2.imdecode(image_to_predict, cv2.IMREAD_COLOR)
        image_to_predict = cv2.cvtColor(image_to_predict, cv2.COLOR_BGR2RGB)
        image = np.array(image_to_predict)
    except UnidentifiedImageError as e:
        # print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid image format")

    # try:
    #     assert image.shape[2]
    # except IndexError:
    #     image = image.reshape(image.shape[0], image.shape[1], 1)
    #     image = np.concatenate([image, image, image], axis=-1)

    pred = object_detection_inferencer(image)

    for preds in pred["predictions"]:
        scores = np.array(preds["scores"])
        detections_indices = np.argwhere(scores >= 0.5)

        if len(detections_indices) == 0:
            return draw_boxes(image, [], [])

        confidences = scores[detections_indices].squeeze().tolist()
        labels = np.array(preds["labels"])[detections_indices].squeeze().tolist()
        bboxes = np.array(preds["bboxes"])[detections_indices].squeeze().tolist()

        bboxes = transform_to_iterable_of_iterables(bboxes)
        labels = transform_to_iterable(labels)
        confidences = transform_to_iterable(confidences)

    class_to_return = labels[0]
    static_dir = f"./static/detection/class_{class_to_return}"
    static_files = list(
        map(lambda x: f"{static_dir.removeprefix('./')}/{x}", os.listdir(static_dir))
    )

    files = np.random.choice(static_files, num_images).tolist()
    print(f"[\x1b[1;31mDEBUG\x1b[0m] Files: {files}")
    return JSONResponse(content={"files": files})


@app.get("/images/{task}")
async def get_images(task: str, label: str, num_images: int = 1):
    num_images = min(num_images, 20)

    if task == "classification":
        static_dir = "./static/classification"
    elif task == "detection":
        static_dir = "./static/detection"
    else:
        return JSONResponse(content={"files": []})

    label_id = label_to_id(task, label)
    print(
        f"[\x1b[1;31mDEBUG\x1b[0m] Task: {task}, Label: {label}, Label ID: {label_id}"
    )
    static_dir = f"{static_dir}/class_{label_id}"
    static_files = list(
        map(lambda x: f"{static_dir.removeprefix('./')}/{x}", os.listdir(static_dir))
    )
    try:
        files = np.random.choice(static_files, num_images).tolist()
    except:
        files = []
    print(f"[\x1b[1;31mDEBUG\x1b[0m] Files: {files}")
    return JSONResponse(content={"files": files})
