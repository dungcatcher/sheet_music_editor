from PIL import ImageDraw, ImageOps
import cv2
import numpy as np


def remove_notes(data_range, image, x_thresh, y_thresh):
    staves = get_stave_lines(data_range, image, x_thresh)
    bar_lines = get_bar_lines(data_range, image, y_thresh)

    image_copy = image.copy()

    blackout = ImageDraw.Draw(image_copy)
    blackout.rectangle(data_range, fill="#ffffff")
    for pixel in staves + bar_lines:
        colour = image.getpixel(pixel)
        image_copy.putpixel(pixel, colour)

    return image_copy


def remove_stave(data_range, image, x_thresh, y_thresh, recursions=3):
    staves = get_stave_lines(data_range, image, x_thresh)
    # bar_lines = get_bar_lines(data_range, image, y_thresh)

    image_copy = image.copy()

    # blackout = ImageDraw.Draw(image_copy)
    # blackout.rectangle(data_range, fill="#ffffff")
    for pixel in staves:
        image_copy.putpixel(pixel, 255)

    image_array = image.copy()
    image_array = image_array.crop((data_range[0][0], data_range[0][1], data_range[1][0], data_range[1][1]))
    image_array = np.array(image_array)

    thresh = cv2.threshold(image_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    image_array = np.invert(cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1))
    image_array = image_array.tolist()

    for y, row in enumerate(image_array):
        for x, col in enumerate(row):
            pixel_val = int(image_array[y][x])
            pixel_x = x + data_range[0][0]
            pixel_y = y + data_range[0][1]

            if pixel_val == 0:
                image_copy.putpixel((pixel_x, pixel_y), pixel_val)

    # return image_copy
    # image_copy = recurse_pixels(image, staves, recursions, 'horizontal')
    # image_copy = recurse_pixels(image_copy, bar_lines, recursions, 'vertical')

    return image_copy


# https://stackoverflow.com/questions/60521925/how-to-detect-the-horizontal-and-vertical-lines-of-a-table-and-eliminate-the-noi

def get_stave_lines2(data_range, image, x_thresh):  # Updated function
    # Load the image
    image_copy = image.copy()
    image_copy = image_copy.crop((data_range[0][0], data_range[0][1], data_range[1][0], data_range[1][1]))
    image_copy = np.array(image_copy)

    staves = get_stave_lines(data_range, image, x_thresh=x_thresh)  # Shit version

    # blur = cv2.GaussianBlur(image_copy, (3, 3), 0)
    thresh = cv2.threshold(image_copy, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    horizontal_mask = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, horizontal_kernel, iterations=1)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
    vertical_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    stave_pixels = horizontal_mask.copy()
    stave_pixels.fill(0)

    for pixel in staves:
        x, y = pixel
        x -= (data_range[0][0] + 1)
        y -= (data_range[0][1] + 1)
        stave_pixels[y, x] = 1

    horizontal_mask[horizontal_mask > 0] = 1

    new_horizontal_mask = cv2.bitwise_and(horizontal_mask, stave_pixels)
    new_horizontal_mask = new_horizontal_mask.tolist()

    result_stave_lines = []
    for y, row in enumerate(new_horizontal_mask):
        for x, pixel in enumerate(row):
            if pixel != 0:
                print(pixel)
                result_stave_lines.append((x + data_range[0][0] + 1, y + data_range[0][1] + 1))
    return result_stave_lines

    # cv2.imshow('horizontal_mask', new_horizontal_mask)
    # cv2.imshow('vertical_mask', vertical_mask)
    # cv2.waitKey()


def recurse_pixels(image, pixels, recursions, orientation):
    image_copy = image.copy()

    if recursions > 0:
        pixels_to_check = []
        for pixel in pixels:
            if orientation == 'horizontal':
                # No neighbours above or no neighbours below
                if image_copy.getpixel((pixel[0], pixel[1] - 1)) == 255 or image_copy.getpixel((pixel[0], pixel[1] + 1)) == 255:
                    image.putpixel(pixel, 255)
                else:
                    pixels_to_check.append(pixel)
            else:
                if image_copy.getpixel((pixel[0] - 1, pixel[1])) == 255 or image_copy.getpixel((pixel[0] + 1, pixel[1])) == 255:
                    image.putpixel(pixel, 255)
                else:
                    pixels_to_check.append(pixel)
        image = recurse_pixels(image, pixels_to_check, recursions - 1, orientation)

    return image


def get_stave_lines(data_range, image, x_thresh):
    started_line = False
    lines = []

    for y in range(data_range[0][1], data_range[1][1] + 1):
        for x in range(data_range[0][0], data_range[1][0] + 1):
            pixel_colour = image.getpixel((x, y))
            if pixel_colour != 255:
                if not started_line:
                    lines.append([])
                    started_line = True
                lines[-1].append((x, y))
            else:
                started_line = False
        started_line = False

    kept_pixels = []
    for line in lines:
        if len(line) >= x_thresh:
            for pixel in line:
                kept_pixels.append(pixel)

    kept_pixels = list(dict.fromkeys(kept_pixels))  # Remove duplicates

    return kept_pixels


def get_bar_lines(data_range, image, y_thresh):
    rows = []
    started_row = False

    for x in range(data_range[0][0], data_range[1][0] + 1):
        for y in range(data_range[0][1], data_range[1][1] + 1):
            pixel_colour = image.getpixel((x, y))
            if pixel_colour != 255:
                if not started_row:
                    rows.append([])
                    started_row = True
                rows[-1].append((x, y))
            else:
                started_row = False
        started_row = False

    kept_pixels = []
    for row in rows:
        row_length = len(row)
        if row_length >= y_thresh:
            for pixel in row:
                kept_pixels.append(pixel)

    return kept_pixels