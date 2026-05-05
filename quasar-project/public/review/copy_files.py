import argparse
import os
import re
import shutil
from pathlib import Path


def extract_class_number(folder_path):
    """Extract class number from folder path (e.g., class_0, class_1, etc.)"""
    match = re.search(r"class_(\d+)", folder_path)
    if match:
        return match.group(1)
    return None


def get_base_filename(filename):
    """Get filename without extension"""
    return Path(filename).stem


def copy_files_for_review(input_folder):
    """
    Copy ground truth and prediction files for images in the input folder.

    Args:
        input_folder: Path to folder containing images to review
    """
    input_path = Path(input_folder).resolve()

    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' does not exist")
        return

    # Extract class number from input path
    class_num = extract_class_number(str(input_path))
    if class_num is None:
        print(f"Error: Could not extract class number from path '{input_folder}'")
        print("Path should contain 'class_X' where X is a number")
        return

    print(f"Processing class_{class_num}...")

    # Define source directories
    # Navigate from review/detection/original/class_X up to public/
    project_root = input_path.parents[3]  # Go up to quasar-project/public
    gt_source = project_root / "detection" / "gt" / f"class_{class_num}"
    pred_source = project_root / "detection" / "predictions" / f"class_{class_num}"

    # Define destination directories
    # From review/detection/original/class_X up to review/detection/
    review_detection = input_path.parents[1]
    gt_dest = review_detection / "gt" / f"class_{class_num}"
    pred_dest = review_detection / "predictions" / f"class_{class_num}"

    # Create destination directories if they don't exist
    gt_dest.mkdir(exist_ok=True)
    pred_dest.mkdir(exist_ok=True)

    print(f"Input folder: {input_path}")
    print(f"GT source: {gt_source}")
    print(f"Predictions source: {pred_source}")
    print(f"GT destination: {gt_dest}")
    print(f"Predictions destination: {pred_dest}")
    print()

    # Check if source directories exist
    if not gt_source.exists():
        print(f"Warning: GT source directory does not exist: {gt_source}")
    if not pred_source.exists():
        print(f"Warning: Predictions source directory does not exist: {pred_source}")

    # Get all image files from input folder
    image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
    image_files = [
        f
        for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print(f"No image files found in {input_path}")
        return

    print(f"Found {len(image_files)} images to process\n")

    copied_count = 0
    missing_count = 0

    # Process each image
    for image_file in image_files:
        base_name = get_base_filename(image_file.name)
        print(f"Processing: {image_file.name}")

        # Copy from GT
        if gt_source.exists():
            for ext in [".png", ".jpg", ".jpeg", ".txt"]:
                gt_file = gt_source / f"{base_name}{ext}"
                if gt_file.exists():
                    dest_file = gt_dest / gt_file.name
                    shutil.copy2(gt_file, dest_file)
                    print(f"  ✓ Copied GT: {gt_file.name} -> {dest_file}")
                    copied_count += 1

        # Copy from Predictions
        if pred_source.exists():
            for ext in [".png", ".jpg", ".jpeg", ".txt"]:
                pred_file = pred_source / f"{base_name}{ext}"
                if pred_file.exists():
                    dest_file = pred_dest / pred_file.name
                    shutil.copy2(pred_file, dest_file)
                    print(f"  ✓ Copied Prediction: {pred_file.name} -> {dest_file}")
                    copied_count += 1

        # Check if any files were found
        gt_found = (
            any(
                (gt_source / f"{base_name}{ext}").exists()
                for ext in [".png", ".jpg", ".jpeg", ".txt"]
            )
            if gt_source.exists()
            else False
        )
        pred_found = (
            any(
                (pred_source / f"{base_name}{ext}").exists()
                for ext in [".png", ".jpg", ".jpeg", ".txt"]
            )
            if pred_source.exists()
            else False
        )

        if not gt_found and not pred_found:
            print(f"  ⚠ Warning: No matching files found for {base_name}")
            missing_count += 1

        print()

    print("=" * 60)
    print(f"Processing complete!")
    print(f"Total files copied: {copied_count}")
    print(f"Images with missing files: {missing_count}")
    print(f"GT destination: {gt_dest}")
    print(f"Predictions destination: {pred_dest}")


def main():
    parser = argparse.ArgumentParser(
        description="Copy GT and prediction files for review based on images in a folder"
    )
    parser.add_argument(
        "input_folder",
        type=str,
        help="Path to folder containing images to review (must contain class_X in path)",
    )

    args = parser.parse_args()
    copy_files_for_review(args.input_folder)


if __name__ == "__main__":
    main()
