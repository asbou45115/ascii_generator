from src.Renderer import Renderer

def main():
    path = 'images/blasphemous.png'
    img = Renderer.get_image_from_file(path)
    render = Renderer.render_as_ascii(img)
    Renderer.save_render(render)
    
if __name__ == "__main__":
    main()
