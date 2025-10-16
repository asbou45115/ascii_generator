import os
import argparse
from src.Renderer import Renderer

def process_images(input_path, output_path, upscale_width, upscale_height, edge_tolerance, print_text):
    if os.path.isdir(input_path):
        files = os.listdir(input_path)
        for filename in files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue
            full_input = os.path.join(input_path, filename)
            img = Renderer.get_image_from_file(full_input, upscale_height, upscale_width)
            if img is None:
                continue

            if print_text:
                Renderer.print_ascii(img, edge_tolerance)
            else:
                render = Renderer.render_as_ascii(img, edge_tolerance)
                os.makedirs(output_path, exist_ok=True)
                output_file = os.path.join(output_path, filename)
                Renderer.save_render(render, output_file)
    else:
        img = Renderer.get_image_from_file(input_path, upscale_height, upscale_width)
        if print_text:
            Renderer.print_ascii(img, edge_tolerance)
        else:
            render = Renderer.render_as_ascii(img, edge_tolerance)
            Renderer.save_render(render, output_path)


def parse_args():
    parser = argparse.ArgumentParser(description="ASCII Renderer Command-Line Tool")
    parser.add_argument("input", help="Path to image or folder of images")
    parser.add_argument("output", help="Output file or folder")
    parser.add_argument("--upscale_width", type=int, default=1920, help="Width to upscale images to (default: 1920)")
    parser.add_argument("--upscale_height", type=int, default=1080, help="Height to upscale images to (default: 1080)")
    parser.add_argument("--edge_tolerance", type=int, default=13, help="Edge detection sensitivity (default: 13)")
    parser.add_argument("--text", action="store_true", help="Print ASCII directly to terminal instead of saving image")
    return parser.parse_args()

def main():
    args = parse_args()
    process_images(
        input_path=args.input,
        output_path=args.output,
        upscale_width=args.upscale_width,
        upscale_height=args.upscale_height,
        edge_tolerance=args.edge_tolerance,
        print_text=args.text
    )

if __name__ == "__main__":
    main()
