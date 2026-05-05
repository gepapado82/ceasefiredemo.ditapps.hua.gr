obj_det_labels = {
    "SMGs": 0,
    "Metal Pistols": 1,
    "Components": 2,
    "Revolvers": 3,
    "Plastic Pistols": 4,
}

classification_labels = {
    "Blades": 0,
    "Bombs": 1,
    "Bow and Arrow": 2,
    "Bullet Boxes": 3,
    "Bullet Cells": 4,
    "Full_face_hoods": 5,
    "Injectable_Drug": 6,
    "Knives": 7,
    "Military_Clothing": 8,
    "Pcp_airguns": 9,
    "Pils Drug": 10,
    "Pistols": 11,
    "Powder_Drug": 12,
    "Revolver": 13,
    "Rifles": 14,
    "Rockets": 15,
    "Seeds": 16,
    "Shotgun": 17,
    "War Accessories": 18,
    "Weapon_Cases": 19,
    "Weapon_Magazines": 20,
    "Weapon_Storage": 21,
    "Weeds": 22,
}


def id_to_label(task: str, label: int):
    if task == "classification":
        return next(
            (key for key, value in classification_labels.items() if value == label),
        )
    elif task == "detection":
        return obj_det_labels[label]
    else:
        return None


def label_to_id(task: str, label: str):
    if task == "classification":
        return classification_labels[label]
    elif task == "detection":
        return obj_det_labels[label]
    else:
        return None
