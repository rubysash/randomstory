from PIL import Image
import numpy as np
import os
import glob
import sys

print("this will duplicate icons, so make sure you understand the code")

sys.exit()

"""
This looks for all *.png in the sources directory
These pngs are expected to be icon sheets (32 or so icons per sheet)
Icons are expected to be about 91 pixels square and black and white

The script separates them into individual icons automatically
You do not need to run this script, but it is one I used to separate icons
"""

# Function to find the next available index for the icon files
def find_next_icon_index():
    existing_icons = glob.glob('./icon_*.png')
    if not existing_icons:
        return 1  # Start from 1 if no icons exist
    highest_index = max(int(os.path.splitext(os.path.basename(icon))[0].split('_')[-1]) for icon in existing_icons)
    return highest_index + 1

# Function to load the image and convert it to a binary array representing the icons
def load_image(file_path):
    img = Image.open(file_path)
    gray_img = img.convert('L')
    inv_img_array = 255 - np.array(gray_img)
    binary_threshold = 128
    binary_img_array = inv_img_array > binary_threshold
    return binary_img_array, img

# Function to find the continuous blocks where black squares are present
def find_blocks(arr, min_size=20):
    blocks = []
    start = None
    for i, val in enumerate(arr):
        if val > 0 and start is None:
            start = i
        elif val == 0 and start is not None:
            if i - start >= min_size:
                blocks.append((start, i))
            start = None
    if start is not None and len(arr) - start >= min_size:
        blocks.append((start, len(arr)))
    return blocks

# Function to crop icons from the detected row and column blocks
def crop_icons_from_blocks(image, row_blocks, col_blocks):
    icons = []
    icon_paths = []
    icon_index = find_next_icon_index()  # Get the starting index for this batch of icons
    for row_block in row_blocks:
        for col_block in col_blocks:
            left, right = col_block
            upper, lower = row_block
            icon = image.crop((left, upper, right, lower))
            icon_path = f'./icon_{icon_index:08d}.png'  # Save icons with padded numbering
            icon.save(icon_path)
            icons.append(icon)
            icon_paths.append(icon_path)
            icon_index += 1  # Increment the index for the next icon
    return icons, icon_paths

# Function to process a single image
def process_image(file_path):
    binary_img_array, img = load_image(file_path)
    sum_rows = np.sum(binary_img_array, axis=1)
    sum_cols = np.sum(binary_img_array, axis=0)
    row_blocks = find_blocks(sum_rows)
    col_blocks = find_blocks(sum_cols)
    cropped_icons, cropped_icon_paths = crop_icons_from_blocks(img, row_blocks, col_blocks)
    return cropped_icon_paths

# Get a list of all .png files in the 'sources' subfolder
source_images = glob.glob('./sources/*.png')

# Process each source image
all_cropped_icon_paths = []
for image_path in source_images:
    cropped_icon_paths = process_image(image_path)
    all_cropped_icon_paths.extend(cropped_icon_paths)
