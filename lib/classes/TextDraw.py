from PIL import Image, ImageDraw, ImageFont

class Text:
    def __init__(self, text: str) -> None:
        self.text = text

    def draw_text(self, file: str):
        img = Image.open(file)
        draw = ImageDraw.Draw(img)

        draw.text((48, 870), self.text, (255, 255, 255), font=ImageFont.truetype('lib\classes\onts\Rockwell-Regular.ttf', 108))

        img.save("lib\photos\img.png")

