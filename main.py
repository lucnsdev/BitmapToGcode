from PIL import Image

PIXEL_SIZE = 0.1
BLACK_THRESHOLD = 128

def is_black(pixel):
    if isinstance(pixel, tuple):
        value = sum(pixel[:3]) / 3
    else:
        value = pixel
    return value <= BLACK_THRESHOLD


def format_number(value):
    return f"{value:.1f}".rstrip("0").rstrip(".")


def process_image(input_file, output_file):
    image = Image.open(input_file).convert("RGB")
    width, height = image.size
    pixels = image.load()

    print(f"Imagem: {width} x {height} pixels")

    with open(output_file, "w", encoding="utf-8") as file:
        output_row = 0
        for image_y in range(height - 1, -1, -1):
            y = (height - 1 - image_y) * PIXEL_SIZE
            black_runs = []
            x = 0

            while x < width:
                if not is_black(pixels[x, image_y]):
                    x += 1
                    continue
                start_x = x

                while x < width and is_black(pixels[x, image_y]):
                    x += 1
                end_x = x

                black_runs.append((start_x, end_x))

            # Se a linha inteira for branca
            if not black_runs:
                # Se quiser uma linha G0 para cada linha branca
                # file.write(f"G0 X0 Y{format_number(y)} S0\n")
                continue

            if output_row % 2 == 0:
                runs = black_runs
            else:
                runs = reversed(black_runs)

            file.write(f"G0 X0 Y0 F1000\n")
            for start_x, end_x in runs:
                start = start_x * PIXEL_SIZE
                end = end_x * PIXEL_SIZE
                if output_row % 2 == 0:
                    file.write(
                        f"G0 X{format_number(start)} "
                        f"Y{format_number(y)} S0\n"
                    )

                    file.write(
                        f"G1 X{format_number(end)} S160\n"
                    )

                else:
                    file.write(
                        f"G0 X{format_number(end)} "
                        f"Y{format_number(y)} S0\n"
                    )

            file.write(f"G0 X0 Y0 F1000\n")
            output_row += 1
        file.write(
            "G0 X0 Y0 S0\nM5"
        )
    print(f"Arquivo gerado: {output_file}")


INPUT_IMAGE = "image.bmp"
OUTPUT_FILE = "pcb.nc"

if __name__ == "__main__":
    process_image(INPUT_IMAGE, OUTPUT_FILE)