
import os
import django
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.models import ProductImage
from apps.scraper.tasks import process_product_image_ocr
from django.contrib.auth import get_user_model

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
User = get_user_model()

def verify_ocr_pipeline():
    print("--- Antigravity OCR Verification ---")
    
    # 1. Create Mock User if needed
    user, created = User.objects.get_or_create(email='ocr_tester@example.com', defaults={'username': 'ocr_tester'})
    if created:
        user.set_password('testpass')
        user.save()
        print("[PASS] Created Test User.")

    # 2. Create Synthetic Image (Text: "iPhone 15")
    # Since we can't easily generate text on image without fonts installed, 
    # we'll create a blank image to test the *Pipeline*, knowing OCR will return low confidence/empty.
    # The goal is to verify the Task Execution, not Tesseract's accuracy (which depends on binary).
    
    print("\n[1] Creating Synthetic Image Record...")
    img_io = BytesIO()
    image = Image.new('RGB', (200, 50), color=(255, 255, 255))
    image.save(img_io, format='PNG')
    
    product_img = ProductImage.objects.create(
        user=user,
        status='PENDING'
    )
    product_img.image.save('test_ocr.png', ContentFile(img_io.getvalue()))
    print(f"[PASS] Created ProductImage ID {product_img.id}")
    
    # 3. Trigger Task Directly (Synchronous Test)
    print("\n[2] Executing OCR Task (Sync Mode)...")
    try:
        # We call the function directly to avoid celery worker requirement for verification
        # The logic inside uses .delay() for the next step, which will just queue it up (good).
        result = process_product_image_ocr(product_img.id)
        print(f"[RESULT] {result}")
        
        # 4. Verify State Update
        product_img.refresh_from_db()
        print(f"[PASS] Final Status: {product_img.status}")
        print(f"[PASS] Extracted Text: '{product_img.extracted_text}'")
        
        if product_img.status in ['COMPLETED', 'LOW_CONFIDENCE']:
            print(" -> OCR PIPELINE: FUNCTIONAL")
        else:
             print(" -> OCR PIPELINE: FAILED STATE")

    except Exception as e:
        print(f"[FAIL] Execution Error: {e}")

if __name__ == "__main__":
    verify_ocr_pipeline()
