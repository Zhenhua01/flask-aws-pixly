import requests
from io import BytesIO
from PIL import Image as PilImage, TiffImagePlugin, ExifTags, ImageFilter, ImageOps
from models import Image, Image_Metadata

def search_images(search):
    id_list = []

    metadata_search = Image_Metadata.query.filter(
        Image_Metadata.__ts_vector__.match(search)).all()

    for metadata in metadata_search:
        id_list.append(metadata.image_id)

    image_search = Image.query.filter(
        Image.__ts_vector__.match(search)).all()

    for image in image_search:
        id_list.append(image.id)

    unique_ids = set(id_list)

    images = Image.query.filter(Image.id.in_(unique_ids)).all()

    return images


def extract_exif(photo):

        image = PilImage.open(photo)
        image_metadata = image.getexif()
        TAGS = ExifTags.TAGS
        exif_data = {}

        for tag, data in image_metadata.items():
            if tag in TAGS:
                if isinstance(data, TiffImagePlugin.IFDRational):
                    data = float(data)
                elif isinstance(data, bytes):
                    data = data.decode(errors="replace")

                exif_data[TAGS[tag]] = data

        return exif_data


def save_image(s3_location):

    response = requests.get(s3_location)
    img = PilImage.open(BytesIO(response.content))
    img.save("static/images/edit.JPG")

    return img

def image_editor(img, form):

    img = custom_colors(img, form)

    if form.tone.data == 'sepia':
        img = sepia(img)

    if form.tone.data == 'black_white':
        img = ImageOps.grayscale(img)

    if form.border.data != 'no_border':
        img = ImageOps.expand(img, border=30, fill=form.border.data)

    if "smooth" in form.edge_detection.data:
        img = img.filter(ImageFilter.SMOOTH)

    if "edges" in form.edge_detection.data:
        img = img.filter(ImageFilter.FIND_EDGES)

    if "enhance" in form.edge_detection.data:
        img = img.filter(ImageFilter.EDGE_ENHANCE)

    if form.reduce.data:
        img = img.reduce(form.reduce.data)

    img.save("static/images/edit.JPG")

    return img


def custom_colors(img, form):

    rgb_form = [form.red.data or 0,
               form.green.data or 0,
               form.blue.data or 0]

    if all(val == 0 for val in rgb_form): return img

    tints = [value/100 for value in rgb_form]
    [red_tint, green_tint, blue_tint] = tints

    img_pixels = img.load()
    width, height = img.size

    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))

            tr = int((1+red_tint) * r)
            tg = int((1+green_tint) * g)
            tb = int((1+blue_tint) * b)

            if tr > 255: tr = 255
            if tg > 255: tg = 255
            if tb > 255: tb = 255

            img_pixels[px, py] = (tr, tg, tb)

    return img


def sepia(img):

    img_pixels = img.load()
    width, height = img.size

    for py in range(height):
        for px in range(width):
            r, g, b = img.getpixel((px, py))

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            if tr > 255: tr = 255
            if tg > 255: tg = 255
            if tb > 255: tb = 255

            img_pixels[px, py] = (tr, tg, tb)

    return img

