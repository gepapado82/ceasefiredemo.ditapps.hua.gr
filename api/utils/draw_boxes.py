from PIL import Image, ImageDraw

LABEL_MAP = {
    0: "Metal Pistols",
    1: "Threat",
    2: "Components",
    3: "Plastic Pistols",
    4: "Revolvers",
    5: "Shotguns",
    6: "SMGs",
    7: "Ammunition",
    8: "Rifles",
}


def draw_boxes(image, boxes=None, labels=None, gt_boxes=None, gt_labels=None) -> Image:
    image = Image.fromarray(image)

    if boxes is None and labels is None:
        boxes = []
        labels = []
    
    if gt_boxes is None and gt_labels is None:
        gt_boxes = []
        gt_labels = []

    label_id = 1

    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = box
        draw = ImageDraw.Draw(image)
        draw.rectangle([x1, y1, x2, y2], outline="cyan" , width=4)
        label = f"{LABEL_MAP[label]}"
        draw.text(
            (x1, y1),
            f"{label} (ID: {label_id})",
            fill="black",
            anchor="ms",
            stroke_fill="white",
            stroke_width=3,
            font=None,
            spacing=0,
            align="center",
            font_size=18,
        )
        label_id += 1
    
    for box, label in zip(gt_boxes, gt_labels):
        x1, y1, x2, y2 = box
        draw = ImageDraw.Draw(image)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        label = f"{LABEL_MAP[label]}"
        draw.text(
            (x1, y1),
            f"{label} (ID: {label_id})",
            fill="black",
            anchor="ms",
            stroke_fill="white",
            stroke_width=3,
            font=None,
            spacing=0,
            align="center",
            font_size=18,
        )
        label_id += 1

    return image
