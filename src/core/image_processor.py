import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
from src.utils.logger import get_logger
from src.core.models import QualityMetrics, ProcessingConfig

logger = get_logger("image_processor")

class ImageProcessor:
    """Handles image preprocessing operations"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
    
    def load_image(self, file_path: str) -> np.ndarray:
        """Load image from file"""
        try:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"Could not load image: {file_path}")
            logger.info(f"Loaded image: {file_path}, shape: {img.shape}")
            return img
        except Exception as e:
            logger.error(f"Error loading image {file_path}: {e}")
            raise
    
    def resize_image(self, img: np.ndarray, 
                     target_size: Tuple[int, int]) -> np.ndarray:
        """Resize image to target dimensions"""
        resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        logger.debug(f"Resized image from {img.shape} to {resized.shape}")
        return resized
    
    def normalize_image(self, img: np.ndarray) -> np.ndarray:
        """Normalize pixel values to 0-1 range"""
        normalized = img.astype(np.float32) / 255.0
        return normalized
    
    def denoise_image(self, img: np.ndarray, strength: int = 10) -> np.ndarray:
        """Remove noise from image"""
        denoised = cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)
        logger.debug("Applied denoising")
        return denoised
    
    def adjust_brightness_contrast(self, img: np.ndarray, 
                                   brightness: int = 0, 
                                   contrast: int = 0) -> np.ndarray:
        """Adjust image brightness and contrast"""
        adjusted = cv2.convertScaleAbs(img, alpha=1 + contrast/100, beta=brightness)
        return adjusted
    
    def convert_to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        logger.debug("Converted to grayscale")
        return gray
    
    def detect_blur(self, img: np.ndarray) -> float:
        """Detect if image is blurry using Laplacian variance"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    def augment_image(self, img: np.ndarray) -> List[np.ndarray]:
        """Create augmented versions of the image"""
        augmented = []
        
        # Original
        augmented.append(img)
        
        # Horizontal flip
        augmented.append(cv2.flip(img, 1))
        
        # Rotation
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        
        for angle in [90, 180, 270]:
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img, matrix, (width, height))
            augmented.append(rotated)
        
        logger.info(f"Generated {len(augmented)} augmented versions")
        return augmented
    
    def save_image(self, img: np.ndarray, output_path: str):
        """Save processed image"""
        cv2.imwrite(output_path, img)
        logger.info(f"Saved image to: {output_path}")
    
    def process_batch(self, input_dir: str, output_dir: str,
                     target_size: Optional[Tuple[int, int]] = None,
                     normalize: bool = False,
                     denoise: bool = False) -> QualityMetrics:
        """Process a batch of images"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        total_images = len(image_files)
        processed_images = 0
        failed_images = 0
        issues = []
        
        logger.info(f"Processing {total_images} images")
        
        for img_file in image_files:
            try:
                img = self.load_image(str(img_file))
                
                # Check for blur
                blur_score = self.detect_blur(img)
                if blur_score < 100:
                    issues.append(f"{img_file.name}: Low quality (blur score: {blur_score:.2f})")
                
                # Resize if specified
                if target_size:
                    img = self.resize_image(img, target_size)
                
                # Denoise if requested
                if denoise:
                    img = self.denoise_image(img)
                
                # Normalize if requested
                if normalize:
                    img = self.normalize_image(img)
                    img = (img * 255).astype(np.uint8)  # Convert back for saving
                
                # Save processed image
                output_file = output_path / img_file.name
                self.save_image(img, str(output_file))
                
                processed_images += 1
                
            except Exception as e:
                logger.error(f"Failed to process {img_file.name}: {e}")
                failed_images += 1
                issues.append(f"{img_file.name}: Processing failed - {str(e)}")
        
        quality_score = processed_images / total_images if total_images > 0 else 0
        
        metrics = QualityMetrics(
            total_records=total_images,
            valid_records=processed_images,
            invalid_records=failed_images,
            missing_values_percent=0.0,
            duplicate_percent=0.0,
            quality_score=round(quality_score, 3),
            issues=issues[:10]  
        )
        
        logger.info(f"Batch processing complete. Success rate: {quality_score:.2%}")
        return metrics