import numpy as np
import cv2
import pyperclip

CHARS = np.array(list(" .:coPO?@■"))   # ascii characters in order of luminance (darkest to brightest)
CHAR_PIXEL_SIZE = 8                     # ascii characters are 8x8 pixels
EDGE_CHARS = {
    0: '-',
    45:  '/',
    90: '|',
    135: '\\'
}

class Renderer:
    def  __init__(self):
        pass
    
    @staticmethod
    def get_image_from_file(file_path: str, upscale_height: int=1080, upscale_width: int=1920) -> np.ndarray:
        '''
        Reads image and up/downscales image with given params
        '''
        img = cv2.imread(file_path)
        if img is None:
            print(f"Error: could not load image at {file_path}")
            return None

        h, w = img.shape[:2]
        scale = upscale_width / w
        height = int(h * scale)
        img = cv2.resize(img, (upscale_width, height), interpolation=cv2.INTER_LANCZOS4)

        return img
    
    @staticmethod
    def render_as_ascii(image: np.ndarray, edge_tolerance: int=13) -> cv2.typing.MatLike:
        '''
        Renders given image and returns the image
        '''
        ascii_matrix, edge_mask, angle = image_to_ascii_matrix(image, edge_tolerance)
        
        height, width = ascii_matrix.shape
        output_img = np.zeros((height, width, 3), dtype=np.uint8)
        color = (255, 255, 255)

        for y in range(0, height, CHAR_PIXEL_SIZE):
            for x in range(0, width, CHAR_PIXEL_SIZE):
                char = CHARS[ascii_matrix[y, x]]

                # If it's an edge, choose edge character based on angle
                if edge_mask[y, x] > 0:
                    ang = (np.degrees(angle[y, x]) + 180) % 180
                    if 22.5 < ang <= 67.5:
                        char = '/'
                    elif 67.5 < ang <= 112.5:
                        char = '|'
                    elif 112.5 < ang <= 157.5:
                        char = '\\'
                    else:
                        char = '-'

                cv2.putText(
                    output_img,
                    char,
                    (x, y + CHAR_PIXEL_SIZE),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    color,
                    1,
                    cv2.LINE_AA
                )

        return output_img
        
    @staticmethod
    def save_render(render: cv2.typing.MatLike, output_path: str="output.png"):
        '''
        Saves ascii render as image to given path
        - if not path given, will be saved to current directory as output.png
        '''
        cv2.imwrite(output_path, render)
        print(f"saved to {output_path}")
        
    @staticmethod
    def render_ascii_to_text(image: np.ndarray, edge_tolerance: int=13) -> str:
        '''
        Converts an image to ASCII text string for terminal or clipboard
        '''
        ascii_matrix, edge_mask, angle = image_to_ascii_matrix(image, edge_tolerance)
        height, width = ascii_matrix.shape

        ascii_lines = []
        for y in range(0, height, CHAR_PIXEL_SIZE):
            line = []
            for x in range(0, width, CHAR_PIXEL_SIZE):
                char = CHARS[ascii_matrix[y, x]]
                if edge_mask[y, x] > 0:
                    ang = (np.degrees(angle[y, x]) + 180) % 180
                    if 22.5 < ang <= 67.5:
                        char = '/'
                    elif 67.5 < ang <= 112.5:
                        char = '|'
                    elif 112.5 < ang <= 157.5:
                        char = '\\'
                    else:
                        char = '-'
                line.append(char)
            ascii_lines.append(''.join(line))
        return "\n".join(ascii_lines)
    
    @staticmethod
    def print_ascii(image: np.ndarray, edge_tolerance: int=13):
        '''
        Prints ASCII directly to terminal
        '''
        ascii_text = Renderer.render_ascii_to_text(image, edge_tolerance)
        print(ascii_text)
        return ascii_text

    @staticmethod
    def copy_ascii_to_clipboard(image: np.ndarray, edge_tolerance: int=13):
        '''
        Copies ASCII text version to clipboard (for GUI)
        '''
        ascii_text = Renderer.render_ascii_to_text(image, edge_tolerance)
        pyperclip.copy(ascii_text)
        print("ASCII art copied to clipboard!")
        return ascii_text
        
def image_to_ascii_matrix(image: np.ndarray, edge_tolerance: int) -> np.ndarray:
    '''
    Downscales then upscales image to fit 8x8 ascii character size
    '''
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Difference of Gaussians to boost contrast to apply sobel edge detection on
    blur1 = cv2.GaussianBlur(gray_img, (0, 0), sigmaX=1.0)
    blur2 = cv2.GaussianBlur(gray_img, (0, 0), sigmaX=4.0)
    dog = cv2.subtract(blur1, blur2)
    dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    downscaled = cv2.resize(
        gray_img,
        (gray_img.shape[1] // CHAR_PIXEL_SIZE, gray_img.shape[0] // CHAR_PIXEL_SIZE),
        interpolation=cv2.INTER_AREA
    )

    # Normalize downscaled to use full 0-255 range
    downscaled = cv2.normalize(downscaled, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Now map brightness (0-255) -> ascii index 
    indices = ((downscaled / 255 * len(CHARS)).astype(np.uint8)) % len(CHARS)
    
    # Sobel edge detection
    gx = cv2.Sobel(dog, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(dog, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(gx, gy)
    angle = np.arctan2(gy, gx)
    
    mag_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    edge_mask = (mag_norm > edge_tolerance).astype(np.uint8) * 255
    
    # Upscaling
    indices_up = cv2.resize(indices, (gray_img.shape[1], gray_img.shape[0]), interpolation=cv2.INTER_NEAREST)
    edge_mask_up = cv2.resize(edge_mask, (gray_img.shape[1], gray_img.shape[0]), interpolation=cv2.INTER_NEAREST)
    angle_up = cv2.resize(angle, (gray_img.shape[1], gray_img.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    return indices_up, edge_mask_up, angle_up
    
