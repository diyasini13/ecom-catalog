import io
from typing import Optional, Tuple, Union, List
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as im
import os
import markdown2
from vertexai.preview.vision_models import (
    Image,
    ImageGenerationModel,
    SubjectReferenceImage,
)
from vertexai.generative_models import GenerativeModel, Part
from vertexai.generative_models import Image as image_gen
import vertexai

# --- Project Setup (Move to top for clarity) ---
# PROJECT_ID = "heroprojectlivedemo"  # Replace with your project ID if different
# LOCATION = "us-central1"  # Replace with your location if different
PROJECT_ID = os.environ.get("PROJECT_ID", "heroprojectlivedemo")  # Get from env or default
LOCATION = os.environ.get("LOCATION", "us-central1")  # Get from env or default
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- Helper Functions ---
def pil_to_image(image: im) -> str:
    """Converts a PIL Image object to a base64 string."""
    with io.BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        img_bytes = buffer.getvalue()
    return img_bytes

def resize_image(image_path, base_width=300):
    """
    Resizes an image to the specified base width while maintaining aspect ratio.

    Args:
      image_path: Path to the image.
      base_width: Desired width for the image. Defaults to 300.

    Returns:
      The resized Image object.
    """
    def calculate_new_dimensions(image_path, base_width):
        wpercent = (base_width / float(image_path.size[0]))
        hsize = int((float(image_path.size[1]) * float(wpercent)))
        return (base_width, hsize)

    img = image_path.resize(calculate_new_dimensions(image_path, base_width), im.LANCZOS)
    return img

def generate_image(image1_path, image2_path, desc1, desc2, prompt):
    """Generates an image based on two reference images, their descriptions, and a prompt."""
    print(image1_path, image2_path, desc1, desc2, prompt)

    try:
        img1 = resize_image(image1_path)
        img2 = resize_image(image2_path)

        image1 = Image(pil_to_image(img1))
        image2 = Image(pil_to_image(img2))

        print(image1, image2)

        ref_image_1 = SubjectReferenceImage(
            image=image1,
            reference_id=1,
            subject_description=desc1,
            subject_type="product",
        )

        ref_image_2 = SubjectReferenceImage(
            image=image2,
            reference_id=2,
            subject_description=desc2,
            subject_type="product",
        )

        generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        customization_model = ImageGenerationModel.from_pretrained("imagen-3.0-capability-001")
        images = customization_model._generate_images(
            prompt=prompt,
            number_of_images=4,
            aspect_ratio="1:1",
            reference_images=[ref_image_1, ref_image_2],
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )

        print("Images", images)
        outputs = [this_image._pil_image for this_image in images]
        for i in range(4):
            if len(outputs) < 4:
                outputs.append(outputs[0])
        return outputs

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def image_to_bytes(image: im) -> str:
    """Converts a PIL object to a base64 string."""
    with io.BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        img_bytes = buffer.getvalue()
    return img_bytes

def pil_to_file(image: im, file_path: str) -> str:
    """Saves a PIL Image object to the specified file path."""
    try:
        image.save(file_path, format="JPEG")
        return file_path
    except Exception as e:
        print(f"Error saving image to file: {e}")
        return None

def generate_description(image_path):
    """Generates a description for an image using Gemini."""
    try:
        image = resize_image(image_path)
        image = image_gen.from_bytes(image_to_bytes(image))
        print(" BS ", image)
        model = GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content([image, "What is shown in this image?"])
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during description generation: {e}")
        return "Error generating description."

def refine_prompt(prompt):
    """Refines the given prompt using Gemini."""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content(f"Rewrite the following prompt for image generation, focusing on creating a concise and effective prompt for a fashion catalog image of a model wearing the outfit. Give only one paragraph answer: {prompt}")
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during prompt refinement: {e}")
        return "Error refining prompt."

def generate_prompt(desc1, desc2):
    """Generates a prompt for image generation using Gemini, based on two descriptions."""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content(
            f"""Create one image generation prompt based on these descriptions:
            Description 1: {desc1}
            Description 2: {desc2}

            The prompt should focus on a fashion model showcasing the outfit in different poses and angles highlighting the outfit [1][2].  Be detailed and descriptive, including information about pose, setting, lighting, and overall mood.  Aim for a high-quality, visually appealing image."""
        )
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during prompt generation: {e}")
        return "Error generating prompt."

def generate_style_and_convert_to_markdown(desc1, desc2, prompt):
    """Generates styling suggestions and converts them to markdown."""
    try:
        model = GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content(
            f"""Suggest different ways to style outfits based on these descriptions and the prompt:
            Description 1: {desc1}
            Description 2: {desc2}
            Prompt: {prompt}

            Focus on providing practical and fashionable styling advice, considering different occasions, accessories, and complementary garments."""
        )

        styling_suggestions_text = response.text.strip()
        html_output = markdown2.markdown(styling_suggestions_text)
        return html_output
    except Exception as e:
        print(f"An error occurred generating styling suggestions: {e}")
        return "Error generating styling suggestions."
