import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont

def select_image():
    # Open a dialog to select an image file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path


def merge_images_with_text(image1_path, image2_path, text="TEXT", font_path="Fjord_Regular.ttf", font_size=40,
                           text_color=(1, 5, 28)):
    # Open your images
    image1 = Image.open(image1_path).convert("RGBA")
    image2 = Image.open(image2_path)

    # Determine the size of the final image
    width, height = image1.size

    # Create a new blank image with the same size
    final_image = Image.new("RGBA", (width, height))

    # Paste the images on top of each other
    final_image.paste(image1, (0, 0))
    final_image.paste(image2, (0, 0), image2)

    # Add text at the bottom
    draw = ImageDraw.Draw(final_image)

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default()

    # Estimate the text width (assuming average character width around half the font size)
    average_char_width = font_size * 0.6
    estimated_text_width = len(text) * average_char_width

    # Center the text horizontally
    text_position = ((width - estimated_text_width) // 2, height - 85)  # Keep vertical position

    # Draw the text in specified color
    draw.text(text_position, text, fill=text_color, font=font)

    return final_image


# if __name__ == "__main__":
#     image1_path = "test_images/prior_images/card-bg-7.jpg"
#     image2_path = "test_images/prior_images/golden-monke.png"
#
#     merged_image = merge_images_with_text(image1_path, image2_path)
#     merged_image.save("merged_image_with_text.png")
#     print("Merged image with text saved as 'merged_image_with_text.png'")


if __name__ == "__main__":
    image1_path = "test_images/prior_images/card-bg-7.jpg"
    image2_path = "test_images/prior_images/golden-monke.png"
    text = "TEXT"
    font_path = "app/api/api_v0/assets/Fjord_Regular.ttf"
    font_size = 40
    text_color = (1, 5, 28)

    merged_image = merge_images_with_text(image1_path, image2_path, text, font_path, font_size, text_color)
    merged_image.save("merged_image_with_text.png")
    print("Merged image with text saved as 'merged_image_with_text.png'")
