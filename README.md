# ASCII Renderer + GUI
A simple desktop application to convert images into ASCII art using Python. Users can adjust resolution, edge detection sensitivity, and process multiple images at once.

![alt text](images/image.png)

![input](images/moon.png)
![output](output/moon.png)

## Features
- Load one or multiple images at once.
- Render ASCII art previews in real time.
- Adjust upscale resolution: choose from presets or enter custom width/height.
- Adjust edge detection sensitivity using a slider or numeric input.
- Save rendered ASCII images to a folder of your choice.

## Installation
### Option 1: Run executable
1) Download the latest release from the [Releases](https://github.com/asbou45115/ascii_renderer/releases)
 page.
2) Extract the .zip
3) Double-click main.exe to open the GUI.
4) Load images, adjust settings, and render ASCII art.

### Option 2: Run from source code
1) Clone repo:
    ```bash
    git clone https://github.com/asbou45115/ascii_renderer.git
    cd ascii_renderer
    ```

2) Create a Python virtual environment (optional but recommended - Not required if using UV package manager):
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3) Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    OR with UV package manger:
    ```bash
    uv sync
    ```

4) Run application:
    ```bash
    python AsciiApp.py
    ```
    OR 
    ```bash
    uv run AsciiApp.py
    ```

