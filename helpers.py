

def sepia(img):
    # img = Image.open(image_path)
    width, height = img.size

    pixels = img.load()  # create the pixel map

    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255

            if tb > 255:
                tb = 255

            pixels[px, py] = (tr, tg, tb)

    return img


def custom_colors(img, rgb):

    print('rgb in custom is', rgb)

    width, height = img.size

    tints = [value/100 for value in rgb]

    [red_tint, green_tint, blue_tint] = tints

    pixels = img.load()

    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))

            tr = int(red_tint * r)
            tg = int(green_tint * g)
            tb = int(blue_tint * b)

            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255

            if tb > 255:
                tb = 255

            pixels[px, py] = (tr, tg, tb)

    return img
