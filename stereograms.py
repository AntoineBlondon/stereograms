import numpy as np
from PIL import Image, ImageDraw

def load_depth_map(path: str, target_width: int=600, target_height: int=300) -> np.ndarray:
    """
    load a depth map image and resize it to the target size while preserving aspect ratio.
    The depth map is converted to grayscale and returned as a numpy array.

    Args:
        path: path to the depth map image
        target_width: width of the resized image
        target_height: height of the resized image
    
    Returns:
        np.ndarray: the resized depth map as a 2D numpy array
    """
    img = Image.open(path).convert("L")
    original_width, original_height = img.size

    # Compute scale to fit within target while preserving aspect ratio
    scale_w = target_width / original_width
    scale_h = target_height / original_height
    scale = min(scale_w, scale_h)

    # Resize with correct aspect ratio
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    resized = img.resize((new_width, new_height), resample=Image.BICUBIC)

    # Center on black background of final size
    final = Image.new("L", (target_width, target_height), color=0)
    offset_x = (target_width - new_width) // 2
    offset_y = (target_height - new_height) // 2
    final.paste(resized, (offset_x, offset_y))

    return np.asarray(final)

def generate_random_pattern(height: int, strip_width: int=100) -> np.ndarray:
    """Generate a vertical strip of random colors to tile.
    
    Args:
        height: height of the strip
        strip_width: width of the strip
    
    Returns:
        np.ndarray: a 3D numpy array of shape (height, strip_width, 3) containing random colors
    """
    return np.random.randint(0, 256, (height, strip_width, 3), dtype=np.uint8)

def generate_stereogram(depth_map: np.ndarray, pattern_width: int=100, max_depth_shift: int=30) -> np.ndarray:
    """
    Generate a stereogram image from a depth map.

    Args:
        depth_map: a 2D numpy array representing the depth map
        pattern_width: width of the repeating pattern
        max_depth_shift: maximum horizontal shift based on depth
    
    Returns:
        np.ndarray: a 3D numpy array representing the stereogram
    """
    height, width = depth_map.shape
    output = np.zeros((height, width, 3), dtype=np.uint8)
    pattern = generate_random_pattern(height, pattern_width)

    for y in range(height):
        for x in range(width):
            # Compute horizontal shift based on depth (0 = far, 255 = close)
            depth = depth_map[y, x] / 255.0
            shift = int(round(depth * max_depth_shift))


            if x < pattern_width:
                output[y, x] = pattern[y, x]
            else:
                source_x = x - pattern_width + shift
                if 0 <= source_x < width:
                    output[y, x] = output[y, source_x]
                else:
                    output[y, x] = pattern[y, x % pattern_width]

    return output

def add_guide_dots(image_array: np.ndarray, separation: int, dot_radius: int=4, y: int=10, color: tuple[int, int, int]=(0, 0, 0)):
    """
    Add two guide dots separated by `separation` pixels horizontally at vertical position `y`.

    Args:
        image_array: the stereogram image as a 3D numpy array
        separation: distance between the two dots
        dot_radius: radius of the dots
        y: vertical position of the dots
        color: RGB color of the dots
    
    Returns:
        np.ndarray: the image array with the guide dots added
    """
    img = Image.fromarray(image_array)
    draw = ImageDraw.Draw(img)
    width = img.width
    center_x = width // 2

    left_x = center_x - separation // 2
    right_x = center_x + separation // 2

    for cx in [left_x, right_x]:
        draw.ellipse(
            (cx - dot_radius, y - dot_radius, cx + dot_radius, y + dot_radius),
            fill=color
        )

    return np.array(img)


if __name__ == "__main__":

    # === CONFIG ===
    depth_map_path = "depth_map.png"
    output_path = "stereogram.png"
    width, height = 600, 300
    pattern_width = 100
    max_shift = 40

    # === RUN ===
    depth_map = load_depth_map(depth_map_path, width, height)
    print(f"depth map {depth_map_path} loaded with shape {depth_map.shape}")
    stereo_img = generate_stereogram(depth_map, pattern_width=pattern_width, max_depth_shift=max_shift)
    stereo_img = add_guide_dots(stereo_img, separation=pattern_width, y=10, dot_radius=4, color=(0, 0, 0))
    print(f"stereogram generated with shape {stereo_img.shape}")
    Image.fromarray(stereo_img, mode="RGB").save(output_path)
    print(f"stereogram saved to {output_path}")
