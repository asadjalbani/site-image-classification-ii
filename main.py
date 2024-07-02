import fitz  # PyMuPDF
from PIL import Image
import io
import os

# Define the keywords for each category
categories_keywords = {
    "Site ID": ["site id", "site identification", "site number"],
    "Shelter": ["shelter"],
    "Tower Structure": ["tower structure", "tower"],
    "Panorama": ["panorama"],
    "Access Road": ["access road"],
    "Site Road Type": ["site road type"],
    "Obstacles": ["obstacles"],
    "Surrounding Garbage": ["surrounding garbage", "garbage"],
    "Risks": ["risks"],
    "Building Height": ["building height"],
    "Building": ["building"],
    "Cabinets": ["cabinets"],
    "Indoor Equipment": ["indoor equipment", "equipment"],
    "Photo for the site from outside": ["photo for the site from outside", "site from outside"]
}

def extract_images_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_num in range(2, len(pdf_document)):  # Start from page 2 to skip the first two pages
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append((page_num, img_index, image, image_ext, page.get_text()))

    return images

def categorize_image(text):
    text = text.lower()
    for category, keywords in categories_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return "Uncategorized"

def is_real_photo(image):
    # Check if the image is a real photo based on its properties
    # For example, filter out small images or black images
    if image.width < 100 or image.height < 100:
        return False
    if image.getextrema() == ((0, 0), (0, 0), (0, 0)):
        return False
    return True

def save_images(images, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page_num, img_index, image, image_ext, text in images:
        if not is_real_photo(image):
            continue
        
        category = categorize_image(text)
        category_folder = os.path.join(output_folder, category)

        if not os.path.exists(category_folder):
            os.makedirs(category_folder)

        image_path = os.path.join(category_folder, f"page_{page_num+1}_img_{img_index+1}.{image_ext}")
        image.save(image_path)

def filter_and_save_top_images(base_folder, output_folder):
    # Initialize a list to hold image information (file path and resolution)
    images_info = []

    # Iterate through each category folder including "Building" and "Building Height"
    for category in os.listdir(base_folder):
        category_folder = os.path.join(base_folder, category)
        
        if os.path.isdir(category_folder):
            for image_name in os.listdir(category_folder):
                image_path = os.path.join(category_folder, image_name)
                
                # Open the image and get its resolution
                with Image.open(image_path) as img:
                    resolution = img.width * img.height
                    images_info.append((image_path, resolution))

    # Sort the images by resolution in descending order
    images_info.sort(key=lambda x: x[1], reverse=True)

    # Select the top 10 images with the highest resolution
    top_10_images = images_info[:10]

    # Define the folder to save the selected images
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Copy the top 10 images to the new folder
    for i, (image_path, resolution) in enumerate(top_10_images, start=1):
        img = Image.open(image_path)
        output_path = os.path.join(output_folder, f"high_res_image_{i}.png")
        img.save(output_path)

    print("Top 10 high-resolution images have been saved in the 'high_resolution_images' folder.")

if __name__ == "__main__":
    pdf_path = "SiteSurvey_GLI_RIY0023_PA20230329000100_71583.pdf"
    output_folder = "output"

    # Extract images from PDF
    images = extract_images_from_pdf(pdf_path)
    
    # Save images to categorized folders
    save_images(images, output_folder)
    
    # Filter and save top 10 high-resolution images
    filter_and_save_top_images(output_folder, "output/high_resolution_images")

