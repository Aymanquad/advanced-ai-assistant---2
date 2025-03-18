import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep


# Function to open and display images based on a given prompt
# def open_images(prompt):
# folder_path = r"Data" # Folder where the images are stored
# prompt = prompt.replace(" ", "") # Replace spaces in prompt with underscores
# # Generate the filenames for the images
# Files [f" {prompt}{i}.jpg" for i in range(1, 5)]
# for jpg file in Files:
# image_path = os.path.join(folder_path, jpg_file)
# try: I
# # Try to open and display the image
# img = Image.open(image_path)
# print (f" Opening image: {image_path}")
# img.show()
# sleep(1) # Pause for 1 second before showing the next image
# except IOError:
# print (f"Unable to open {image_path}")
# # API details for the Hugging Face Stable Diffusion model
# API_URL = "https://api-inference.hugging face.co/models/stabilityai/stable-diffusion-xl-base-1.0"
# headers = {"Authorization": "Bearer {get_key('.env', 'Hugging FaceAPIKey')}"}