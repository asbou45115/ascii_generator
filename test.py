import os
from src.Renderer import Renderer

def test_all_images():
    input_folder = 'images'
    output_folder = 'output'

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            continue

        input_path = os.path.join(input_folder, filename)
        img = Renderer.get_image_from_file(input_path)
        if img is None:
            continue

        render = Renderer.render_as_ascii(img)

        # Save with the same filename in the output folder
        output_path = os.path.join(output_folder, filename)
        Renderer.save_render(render, output_path)

def test_one_image():
    path = 'images/image.png'
    img = Renderer.get_image_from_file(path)
    render = Renderer.render_as_ascii(img)
    Renderer.save_render(render)

def main():
    test_all_images()
    # test_one_image()

if __name__ == "__main__":
    main()
