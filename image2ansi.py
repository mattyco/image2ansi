import argparse
from PIL import Image as pillow

class RGB:
    def __init__(self, r: int, g: int, b: int) -> None:
        if not all(self.is_valid(n) for n in (r, g, b)):
            raise ValueError("RGB values must be between 0 and 255")
        
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    # checks if a value of the rgb is valid or not.
    def is_valid(n: int) -> bool:
        return isinstance(n, int) and not isinstance(n, bool) and n >= 0 and n <= 255

    # ansi returns the ANSI escape sequence for the current RGB colour.
    def ansi(self) -> str:
        return f"\x1b[38;2;{self.r};{self.g};{self.b}m"

class Image:
    def __init__(self, type: str, path: str, width: int, height: int):
        if type.lower() == "ansi":
            height *= 2
        
        if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        
        try:
            image = pillow.open(path, formats=("JPEG", "PNG", "WEBP", "BMP")).convert("RGB")
            self.image = image.resize((width, height), pillow.Resampling.LANCZOS)
            self.pixels = self.image.load()
        except (OSError, ValueError) as e:
            raise ValueError(f"Pillow failed to load image: {e}") from e

        self.width = width
        self.height = height

    # get_pixel returns the RGB value of a specific pixel inside of the image.
    def get_pixel(self, x: int, y: int) -> RGB:
        if self.pixels is None:
            raise RuntimeError("Image has not been loaded.")
            
        r,g,b = self.pixels[x,y]
        return RGB(r,g,b)

class ImageToANSI(Image):
    def __init__(self, path: str, width: int, height: int):
        super().__init__("ansi", path, width, height)

    # get_ansi_square returns the square for the current pixel.
    def get_ansi_square(self, x: int, y: int) -> str:
        upper = self.get_pixel(x, y+1)
        lower = self.get_pixel(x, y)

        return f"\x1b[48;2;{upper.r};{upper.g};{upper.b};38;2;{lower.r};{lower.g};{lower.b}m▀"

    # convert_image converts the provided image into ascii art.
    def convert_image(self) -> str:
        output = []
    
        for y in range(0, self.height, 2):
            row = []
    
            for x in range(self.width):
                character = self.get_ansi_square(x, y)
                row.append(character)
    
            output.append("".join(row))
    
        return "\x1b[0m\n".join(output) + "\x1b[0m"

class ImageToASCII(Image):
    def __init__(self, path: str, width: int, height: int):
            super().__init__("ascii", path, width, height)
            self.characters = "@#+*-,. "

    # get_pixel_character returns the character for the provided pixel based on intensity.
    def get_pixel_character(self, pixel: RGB) -> str:
        brightness = (0.299 * pixel.r) + (0.587 * pixel.g) + (0.114 * pixel.b)
        index = int((brightness / 255) * (len(self.characters) - 1))
        return pixel.ansi() + self.characters[index]

    # convert_image converts the provided image into ascii art.
    def convert_image(self) -> str:
        output = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                pixel = self.get_pixel(x, y)
                character = self.get_pixel_character(pixel)

                row.append(character)

            output.append("".join(row))

        return "\x1b[0m\n".join(output) + "\x1b[0m"


def main():
    parser = argparse.ArgumentParser(description="Convert an image into ASCII art.")

    parser.add_argument("-i", "--image", required=True, type=str, help="Provide the path to the desired image file.")
    parser.add_argument("-w", "--width", type=int, default=80, help="Provide the desired width of the image.")
    parser.add_argument("-he", "--height", type=int, default=24, help="Provide the desired width of the image.")
    parser.add_argument("-a", "--ascii", action="store_true", default=False, help="Choose wether you want ASCII rendering.")

    args = parser.parse_args()

    image = args.image
    width = args.width
    height = args.height
    ascii = args.ascii

    try:
        if ascii:
            converter = ImageToASCII(image, width, height)
        else:
            converter = ImageToANSI(image, width, height)

        print(converter.convert_image())
    except (ValueError, RuntimeError) as e:
        print(e)

if __name__ == "__main__":
    main()

