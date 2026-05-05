# Ceasefire API Documentation

## Installtion

It is best advised to first create a virtual environment, either using Python's
`venv` module or the Conda environment manager. Tested on Python 3.9.18.

To install all the necessary packages please run the following command:

```bash
./mmdet_setup.sh
```

If the script is not executable, make it executable by executing `chmod +x ./mmdet_setup.sh`

TODO: Docker

## Model Weights

> [!important]
> For the API to work correctly you need to download and move all the model [weights](https://github.com/jgenc/ceasefire_demo/releases/tag/weights) into the `api/model/` directory, otherwise the API will not work. 

## Usage

First make sure you're in the correct directory (`api`), and then execute the following command:

```bash
uvicorn main:app --reload
```

The exposed port is `8000`

TODO: Docker

## Endpoints


### `/predict`

A `POST` request that requires for the `Request Body` `multipart/form-data`. Only images should be uploaded.

The returned object adheres to the following structure:

```json
{
	"results": [
		{
			"image_name": "<file_name>",
			"predicted_label": "<label_id>",
			"confidence": number,
			"entropy": number
		},
		// ... classification of other files
	]
}
```

The mapping of `predicted_label` to a Class Name is the following:

```
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
```

### `/detect`

A `POST` request that requires for the `Request Body` `multipart/form-data`. Only images should be uploaded.

The returned object adheres to the following structure:

```json
{
  "results": [
    {
      "imageName": "imageName1.jpg",
      "detections": [
        {
          "bbox": [
                      min_x, min_y, max_x, max_y
          ],
          "predicted_class": int,
          "confidence": float
        },
        // … other detections if they exist
      ]
    }
    // ... other images
  ]
}
```

The mapping of `predicted_class` to a Class Name is the following:

```
0: 'SMGs',
1: 'Metal Pistols',
2: 'Components',
3: 'Revolvers',
4: 'Plastic Pistols'
```