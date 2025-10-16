import os
import argparse
from src.Renderer import Renderer

def process_images(input_path, output_path, upscale_width, upscale_height, edge_tolerance):
    """
    Process a single image or all images in a folder.
    """
    # If input is a folder, process all image files inside
    if os.path.isdir(input_path):
        os.makedirs(output_path, exist_ok=True)
        files = os.listdir(input_path)
        for filename in files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue
            full_input = os.path.join(input_path, filename)
            img = Renderer.get_image_from_file(full_input, upscale_height, upscale_width)
            if img is None:
                continue
            render = Renderer.render_as_ascii(img, edge_tolerance=edge_tolerance)
            output_file = os.path.join(output_path, filename)
            Renderer.save_render(render, output_file)
    elif os.path.isfile(input_path):
        # Single image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img = Renderer.get_image_from_file(input_path, upscale_height, upscale_width)
        render = Renderer.render_as_ascii(img, edge_tolerance=edge_tolerance)
        Renderer.save_render(render, output_path)
    else:
        print(f"Error: {input_path} is not a valid file or folder.")

def parse_args():
    parser = argparse.ArgumentParser(description="ASCII Renderer Command-Line Tool")
    parser.add_argument("input", help="Path to image or folder of images")
    parser.add_argument("output", help="Output file or folder")
    parser.add_argument("--upscale_width", type=int, default=1920, help="Width to upscale images to (default: 1920)")
    parser.add_argument("--upscale_height", type=int, default=1080, help="Height to upscale images to (default: 1080)")
    parser.add_argument("--edge_tolerance", type=int, default=13, help="Edge detection sensitivity (default: 13)")
    return parser.parse_args()

def main():
    args = parse_args()
    process_images(
        input_path=args.input,
        output_path=args.output,
        upscale_width=args.upscale_width,
        upscale_height=args.upscale_height,
        edge_tolerance=args.edge_tolerance
    )

if __name__ == "__main__":
    main()
