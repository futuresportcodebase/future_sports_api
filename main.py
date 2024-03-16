from functions import merge_images_with_text

if __name__ == "__main__":
    image1_path = "test_images/prior_images/card-bg-7.jpg"
    image2_path = "test_images/prior_images/golden-monke.png"
    text = "REMINGTON"
    font_path = "Fjord_Regular.ttf"
    font_size = 40
    text_color = (1, 5, 28)

    merged_image = merge_images_with_text(image1_path, image2_path, text, font_path, font_size, text_color)
    merged_image.save("merged_image_with_text.png")
    print("Merged image with text saved as 'merged_image_with_text.png'")

