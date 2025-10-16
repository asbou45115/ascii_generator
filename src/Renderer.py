import numpy as np
import cv2

CHARS = np.array(list(" .:coPO?#@■"))   # ascii characters in order of luminance (darkest to brightest)
CHAR_PIXEL_SIZE = 8                     # ascii characters are 8x8 pixels

class Renderer:
    def  __init__(self):
        pass
    
    @staticmethod
    def get_image_from_file(file_path: str) -> np.ndarray:
        img = cv2.imread(file_path)
        if img is None:
            print(f"Error: could not load image at {file_path}")
            return None
        
        return img
    
    @staticmethod
    def render_as_ascii(image: np.ndarray) -> cv2.typing.MatLike:
        '''
        Renders given image and returns the image
        '''
        ascii_matrix = image_to_ascii_matrix(image)
        
        height, width = ascii_matrix.shape
        output_img = np.ones((height, width, 3), dtype=np.uint8)
        
        for y in range(0, height, CHAR_PIXEL_SIZE):
            for x in range(0, width, CHAR_PIXEL_SIZE):
                char =  CHARS[ascii_matrix[y, x]]
                cv2.putText(
                    img=output_img,
                    text=char,
                    org=(x, y + CHAR_PIXEL_SIZE),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.35,
                    color=(255, 255, 255),
                    thickness=1,
                    lineType=cv2.LINE_AA
                )
                
        return output_img
        
    @staticmethod
    def save_render(render: cv2.typing.MatLike, output_path: str="output.png"):
        '''
        Saves ascii render to given path
        - if not path given, will be saved to current directory as output.png
        '''
        cv2.imwrite(output_path, render)
        print(f"saved to {output_path}")
        
def image_to_ascii_matrix(image: np.ndarray) -> np.ndarray:
    '''
    Downscales then upscales image to fit 8x8 ascii character size
    '''
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    downscaled = cv2.resize(
        gray_img,
        (gray_img.shape[1] // CHAR_PIXEL_SIZE, gray_img.shape[0] // CHAR_PIXEL_SIZE),
        interpolation=cv2.INTER_AREA
        )
    
    # Map brightness (0-255) -> ascii index
    indices = np.clip((downscaled / 255 * (len(CHARS) - 1)), 0, len(CHARS) - 1).astype(np.uint8)
    
    upscaled = cv2.resize(
        indices,
        (gray_img.shape[1], gray_img.shape[0]),
        interpolation=cv2.INTER_NEAREST
    )
    
    return upscaled
    
