import os
import requests
import base64
import zipfile
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Get the uploaded image file
        uploaded_file = request.FILES['image']
        
        # Save the uploaded file temporarily
        with open('uploaded_image.jpg', 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        # Define the URL and the payload to send
        url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
        image_path = "uploaded_image.jpg"
        payload = {
            "init_images": [image_path],
            "prompt": "different moods",
            "batch_size": 6,
        }

        # Send payload to the API
        response = requests.post(url, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            # Decode and save the images
            stickers = response.json().get('images', [])
            for i, sticker in enumerate(stickers):
                with open(f"sticker_{i+1}.png", 'wb') as f:
                    f.write(base64.b64decode(sticker))
            
            # Create a zip file containing all stickers
            zip_filename = 'stickers.zip'
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for i, sticker in enumerate(stickers):
                    zipf.write(f"sticker_{i+1}.png")
            
            # Return the zip file as a download response
            with open(zip_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                return response
        else:
            return HttpResponse("Failed to generate stickers. Please try again.")
    else:
        return render(request, 'upload.html')


def generate_stickers(request):
    # Define the URL and the prompt for generating stickers
    url = "http://127.0.0.1:7860/sdapi/v1/img2img"
    prompt = "web3 memoji theme different emotions"

    # Retrieve the uploaded image from the request
    uploaded_image = request.FILES.get('image')

    # Create a directory to save the sticker images
    os.makedirs("sticker_images", exist_ok=True)

    # Generate stickers using the uploaded image and the prompt
    payload = {
        "init_images": [base64.b64encode(uploaded_image.read()).decode()],  # Encode image bytes as base64
        "prompt": "reading emoji",  # Concatenate the prompt with the desired prompt
        "batch_size": 6,
    }

    # Send the payload to the API to generate stickers
    response = requests.post(url, json=payload)
    r = response.json()

    # Decode and save each sticker image
    for i, img_data in enumerate(r['images']):
        with open(f"sticker_images/sticker_{i+1}.png", 'wb') as f:
            f.write(base64.b64decode(img_data))

    # Compress the sticker images into a zip file
    zip_filename = "stickers.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk("sticker_images"):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), "sticker_images"))

    # Serve the zip file for download
    with open(zip_filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="stickers.zip"'
        return response
