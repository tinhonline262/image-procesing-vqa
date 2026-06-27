import pytest
from PIL import Image
import io
from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from app.utils.image_utils import validate_and_load_image
from app.core.config import settings

@pytest.mark.asyncio
async def test_validate_valid_image(test_image_bytes):
    """Test validating a valid JPEG image."""
    upload_file = UploadFile(
        filename="test.jpg", 
        file=io.BytesIO(test_image_bytes),
        headers={"content-type": "image/jpeg"}
    )
    
    img = await validate_and_load_image(upload_file)
    assert isinstance(img, Image.Image)

@pytest.mark.asyncio
async def test_validate_invalid_content_type():
    """Test validation fails for non-image content types."""
    upload_file = UploadFile(
        filename="test.txt", 
        file=io.BytesIO(b"Not an image"),
        headers={"content-type": "text/plain"}
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await validate_and_load_image(upload_file)
    assert exc_info.value.status_code == 400
    assert "File must be an image" in exc_info.value.detail

@pytest.mark.asyncio
async def test_validate_corrupted_image():
    """Test validation fails for corrupted image bytes."""
    upload_file = UploadFile(
        filename="corrupted.jpg", 
        file=io.BytesIO(b"This is not a real image byte stream"),
        headers={"content-type": "image/jpeg"}
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await validate_and_load_image(upload_file)
    assert exc_info.value.status_code == 400
    assert "Invalid or corrupted image" in exc_info.value.detail
