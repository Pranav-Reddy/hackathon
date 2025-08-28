from google.cloud import vision

def analyze_image(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    # OCR
    ocr_response = client.document_text_detection(image=image)
    text = ocr_response.full_text_annotation.text.strip() if ocr_response.full_text_annotation else ""

    # Labels
    label_response = client.label_detection(image=image)
    labels = ", ".join([label.description for label in label_response.label_annotations[:5]])

    return text, labels

def detect_labels_from_image(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.label_detection(image=image)
    labels = [label.description for label in response.label_annotations]

    return labels

def recognize_product_from_image(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.web_detection(image=image)
    web_detection = response.web_detection

    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")

    # Try best guess labels first
    if web_detection.best_guess_labels:
        print("Best Guess:")
        for label in web_detection.best_guess_labels:
            return label.label  # Use this as the product name

    # Fall back to web entities
    if web_detection.web_entities:
        print("Web Entities:")
        for entity in web_detection.web_entities:
            if entity.description:
                return entity.description  # Use for product name

    return None