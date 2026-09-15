from PIL import Image

class BlackLine:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._width = 1

    def increment(self):
        self._width += 1

    def get_width(self):
        return self._width

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y


def is_black(pixel):
    if isinstance(pixel, tuple):
        value = sum(pixel[:3]) / 3
    else:
        value = pixel
    return value <= BLACK_THRESHOLD

def get_lines(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pixels = image.load()

    lines = []
    for y in range(height):
        black_lines = []
        line = None
        x = 0
        while x < width:
            if is_black(pixels[x, height - y - 1]): break;
            x += 1
        while x < width:
            pixel_black = is_black(pixels[x, height - y - 1])
            if line is None and pixel_black:
                line = BlackLine(x, y)
                black_lines.append(line)
            elif pixel_black:
                line.increment()
            else:
                line = None
            x += 1
        lines.append(black_lines)
    return lines


def convert_gcode(output_file, lines):
    with open(output_file, "w") as f:
        f.write("G0 X0 Y0 F1000\nM3 S0\n")
        reverse = False
        for black_lines in lines:
            if reverse: black_lines.reverse()
            for line in black_lines:
                x = line.get_x()
                y = line.get_y()
                if reverse:
                    f.write(f"G0 X{(x + line.get_width()) * PIXEL_SIZE} Y{y * PIXEL_SIZE} S0\n")
                    f.write(f"G1 X{x * PIXEL_SIZE} Y{y * PIXEL_SIZE} S{LASER_PWM}\n")
                else:
                    f.write(f"G0 X{x * PIXEL_SIZE} Y{y * PIXEL_SIZE} S0\n")
                    f.write(f"G1 X{(x + line.get_width()) * PIXEL_SIZE} Y{y * PIXEL_SIZE} S{LASER_PWM}\n")
            reverse = not reverse
        f.write("G0 X0 Y0 S0\nM5\n")


PIXEL_SIZE = 0.1            # passo do motor em milimetros
BLACK_THRESHOLD = 128       # 0-255 acima de 128 considera branco e abaixo considera preto
LASER_PWM = 160             # 0-1023 PWM do ESP32
INPUT_IMAGE = "image.bmp"   # nome da imagem de entrada
OUTPUT_FILE = "pcb.nc"      # nome do arquivo a ser gerado

if __name__ == "__main__":
    lines = get_lines(INPUT_IMAGE)
    convert_gcode(OUTPUT_FILE, lines)