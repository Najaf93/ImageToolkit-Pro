import cv2
import numpy as np
import pytesseract
import os
from PIL import Image, ImageEnhance

def test_ocr_preprocessing(image_path):
    """Test different preprocessing techniques for product packaging OCR"""
    
    print(f"Testing OCR on: {image_path}")
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image")
        return
    
    # Test 1: Current method (grayscale + Otsu threshold)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, otsu_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    print("\n=== Current Method (Otsu) ===")
    text_otsu = pytesseract.image_to_string(otsu_thresh, config='--psm 6')
    print(f"Extracted text: {text_otsu.strip()}")
    
    # Test 2: Adaptive threshold
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
    
    print("\n=== Adaptive Threshold ===")
    text_adaptive = pytesseract.image_to_string(adaptive_thresh, config='--psm 6')
    print(f"Extracted text: {text_adaptive.strip()}")
    
    # Test 3: Contrast enhancement + threshold
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_gray = clahe.apply(gray)
    _, enhanced_thresh = cv2.threshold(enhanced_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    print("\n=== Contrast Enhanced ===")
    text_enhanced = pytesseract.image_to_string(enhanced_thresh, config='--psm 6')
    print(f"Extracted text: {text_enhanced.strip()}")
    
    # Test 4: Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    morph = cv2.morphologyEx(enhanced_thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    
    print("\n=== Morphological Cleaned ===")
    text_morph = pytesseract.image_to_string(morph, config='--psm 6')
    print(f"Extracted text: {text_morph.strip()}")
    
    # Test 5: Different PSM modes
    print("\n=== Different PSM Modes ===")
    for psm in [3, 4, 6, 8, 11]:
        try:
            text_psm = pytesseract.image_to_string(enhanced_thresh, config=f'--psm {psm}')
            print(f"PSM {psm}: {text_psm.strip()[:100]}...")
        except:
            print(f"PSM {psm}: Failed")
    
    # Test 6: Large text detection
    print("\n=== Large Text Detection ===")
    data = pytesseract.image_to_data(enhanced_thresh, config='--psm 6', output_type=pytesseract.Output.DICT)
    
    large_text = []
    avg_height = 0
    text_count = 0
    
    # Calculate average text height
    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        if word and len(word) > 1 and int(data['conf'][i]) > 30:
            avg_height += data['height'][i]
            text_count += 1
    
    if text_count > 0:
        avg_height = avg_height / text_count
        min_height = avg_height * 1.2
        print(f"Average text height: {avg_height:.1f}, Min height for large text: {min_height:.1f}")
        
        # Collect large text
        for i in range(len(data['text'])):
            word = data['text'][i].strip()
            if word and len(word) > 1:
                height = data['height'][i]
                conf = int(data['conf'][i])
                if height >= min_height and conf > 30:
                    large_text.append(word)
        
        if large_text:
            print(f"Large text found: {' '.join(large_text)}")
    
    # Save processed images for visual inspection
    cv2.imwrite('debug_otsu.jpg', otsu_thresh)
    cv2.imwrite('debug_adaptive.jpg', adaptive_thresh)
    cv2.imwrite('debug_enhanced.jpg', enhanced_thresh)
    cv2.imwrite('debug_morph.jpg', morph)
    print("\nProcessed images saved as debug_*.jpg for inspection")

if __name__ == "__main__":
    # Test with a sample image
    test_image = "test_product.jpg"  # Change this to your product image
    if os.path.exists(test_image):
        test_ocr_preprocessing(test_image)
    else:
        print(f"Please provide a product packaging image path")
        print("Available image files in current directory:")
        for f in os.listdir('.'):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"  {f}")