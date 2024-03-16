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

# Open your PNG images
image1 = Image.open("test_images/prior_images/ballstars-test-layer-0.png")

# Select the middle image using the GUI
image2_path = select_image()
if image2_path:  # Proceed only if a file is selected
    image2 = Image.open(image2_path).convert("RGBA")
else:
    image2 = None
    print("No image selected for the middle layer. Exiting.")
    exit()

# image3 = Image.open("test_images/ballstars-test-layer-2.png")

image3 = Image.open("test_images/prior_images/ballstars-test-layer-2.png")

# Determine the size of the final image
width, height = image1.size

# Create a new blank image with the same size
final_image = Image.new("RGBA", (width, height))

# Paste the images on top of each other
final_image.paste(image1, (0, 0))
final_image.paste(image2, (0, 0), image2)
final_image.paste(image3, (0, 0), image3)

# Add text at the bottom
draw = ImageDraw.Draw(final_image)

# Specify the font size
font_size = 40  # Adjust this size as needed

# Load a specific font or use default with specified size
try:
    font = ImageFont.truetype("Fjord_Regular.ttf", font_size)
except IOError:
    print("Font not found, using default font.")
    font = ImageFont.load_default()

text = "YES"

# Estimate the text width (assuming average character width around half the font size)
# This is a rough estimate and may need adjustment
average_char_width = font_size * 0.6
estimated_text_width = len(text) * average_char_width

# Center the text horizontally
text_position = ((width - estimated_text_width) // 2, height - 75)  # Keep vertical position

# Draw the text in specified color
draw.text(text_position, text, fill=(106, 93, 87), font=font)

# Save the merged image with text to a file
final_image.save("merged_image_with_text.png")

print("Merged image with text saved as 'merged_image_with_text.png'")
