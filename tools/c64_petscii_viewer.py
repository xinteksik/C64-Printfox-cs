
from tkinter import Tk, Text, Button, Label, Scrollbar, END
from PIL import Image, ImageDraw

def render_chars_from_input(data):
    lines = [line for line in data.splitlines() if line.strip()]
    bitmaps = []
    for line in lines:
        line = line.replace("!by", "").replace("$", "").replace(" ", "")
        bytes_str = line.split(",")
        try:
            bitmap = [int(b, 16) for b in bytes_str if b]
            if len(bitmap) == 8:
                bitmaps.append(bitmap)
        except ValueError:
            continue  # Skip malformed lines

    if not bitmaps:
        return None

    char_width, char_height = 8, 8
    scale = 10
    cols = 10
    rows = (len(bitmaps) + cols - 1) // cols
    img_width = cols * char_width * scale
    img_height = rows * char_height * scale

    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    for idx, bitmap in enumerate(bitmaps):
        col = idx % cols
        row = idx // cols
        x_offset = col * char_width * scale
        y_offset = row * char_height * scale

        for y, byte in enumerate(bitmap):
            for x in range(8):
                if byte & (1 << (7 - x)):
                    draw.rectangle(
                        [
                            (x_offset + x * scale, y_offset + y * scale),
                            (x_offset + (x + 1) * scale - 1, y_offset + (y + 1) * scale - 1),
                        ],
                        fill="black"
                    )
    return image

def on_submit():
    data = text_area.get("1.0", END)
    img = render_chars_from_input(data)
    if img:
        img.show()

root = Tk()
root.title("C64 PETSCII Viewer")

label = Label(root, text="Vlož hexadecimální data znaků (např. $0C,$18,...):")
label.pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")

text_area = Text(root, height=20, width=80, yscrollcommand=scrollbar.set)
text_area.pack()
scrollbar.config(command=text_area.yview)

submit_button = Button(root, text="Zobrazit znaky", command=on_submit)
submit_button.pack()

root.mainloop()
