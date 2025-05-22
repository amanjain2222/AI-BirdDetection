import base64

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode('utf-8')
    except FileNotFoundError:
         print(f"Error: File not found: {image_path}")
         return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
image_path = "C:/y6s1/fit5225/Ass3/FIT5225-A3-Group51/Example_image.svg"

print(image_to_base64(image_path))