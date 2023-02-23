from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


im = Image.open("test.HEIC")

size = (400,400)

im.thumbnail(size)
im.save("output.jpg", "JPEG")
