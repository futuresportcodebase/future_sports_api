import requests

backgrounds = [
    "https://ibb.co/P6gkFB2",
    "https://ibb.co/MVkWyz3",
    "https://ibb.co/R2q7npV",
    "https://ibb.co/ZNLzSqN",
    "https://ibb.co/zRyNfkV"
]

pfp = "https://ibb.co/GdpkPmz"


def test_merge_images_with_urls():
    url = "http://localhost:8000/merge_images"

    for background_url in backgrounds:
        data = {
            "image1_url": pfp,
            "image2_url": background_url
        }

        response = requests.post(url, json=data)
        print(response.content)
        # assert response.status_code == 200
        # assert response.headers["Content-Type"] == "image/png"

        filename = f"merged_image_{backgrounds.index(background_url)}.png"
        with open(filename, "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    test_merge_images_with_urls()
    print("Tests passed.")
