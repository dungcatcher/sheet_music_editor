from PIL import ImageDraw


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


def remove_stave(data_range, image, x_thresh, y_thresh, recursions=2):
    staves = get_stave_lines(data_range, image, x_thresh)
    bar_lines = get_bar_lines(data_range, image, y_thresh)

    image = recurse_pixels(image, staves, recursions, 'horizontal')
    image = recurse_pixels(image, bar_lines, recursions, 'vertical')

    return image


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

    # for line in lines:
    #     if len(line) < x_thresh:
    #         final_pixel = line[-1]
    #         if (final_pixel[0], final_pixel[1] - 1) in kept_pixels:
    #             for pixel in line:
    #                 kept_pixels.append(pixel)
    #         elif (final_pixel[0], final_pixel[1] + 1) in kept_pixels:
    #             for pixel in line:
    #                 kept_pixels.append(pixel)

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