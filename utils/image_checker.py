"""
Image Quality Checking Utility for CropCare
Performs blur detection, brightness analysis, and plant coverage estimation using PIL and NumPy.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image
from config import IMAGE_THRESHOLDS


@dataclass
class ImageQualityResult:
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def get_summary_message(self) -> str:
        if self.is_valid:
            return "✅ Image quality passed all checks (sharpness, lighting, coverage)."
        return "⚠️ Image quality issues detected: " + ", ".join(self.issues)


def calculate_blur_variance(gray_array: np.ndarray) -> float:
    """
    Approximate Laplacian variance using finite difference 2D convolution kernel.
    [[ 0,  1, 0],
     [ 1, -4, 1],
     [ 0,  1, 0]]
    """
    if gray_array.ndim != 2:
        raise ValueError("Input array must be 2D grayscale")

    # Fast 2D discrete Laplacian filter
    padded = np.pad(gray_array, pad_width=1, mode='edge')
    laplacian = (
        padded[0:-2, 1:-1] + padded[2:, 1:-1] +
        padded[1:-1, 0:-2] + padded[1:-1, 2:] -
        4 * padded[1:-1, 1:-1]
    )
    variance = float(np.var(laplacian))
    return variance


def calculate_brightness(gray_array: np.ndarray) -> float:
    """Calculate mean luminance (0-255 scale)."""
    return float(np.mean(gray_array))


def calculate_plant_coverage(rgb_array: np.ndarray) -> float:
    """
    Estimate percentage of plant/vegetation pixels using Excess Green Index (ExG = 2G - R - B)
    and RGB hue thresholding.
    """
    if rgb_array.ndim != 3 or rgb_array.shape[2] < 3:
        return 0.0

    r = rgb_array[:, :, 0].astype(float)
    g = rgb_array[:, :, 1].astype(float)
    b = rgb_array[:, :, 2].astype(float)

    # Excess Green Index
    exg = 2 * g - r - b
    # Also check if G is the dominant channel
    green_mask = (exg > 15) & (g > r) & (g > b)
    
    # Also include yellowing leaves (chlorosis): High G and R, lower B (R > B, G > B)
    yellow_mask = (r > 100) & (g > 100) & (b < 120) & (abs(r - g) < 40)
    
    # Brown/decaying foliage: Moderate R & G, low B
    brown_mask = (r > 60) & (r < 180) & (g > 40) & (g < 140) & (b < 90) & (r > g)

    combined_plant_mask = green_mask | yellow_mask | brown_mask
    total_pixels = rgb_array.shape[0] * rgb_array.shape[1]
    plant_pixels = np.count_nonzero(combined_plant_mask)

    return float((plant_pixels / total_pixels) * 100.0)


def check_image_quality(image: Image.Image) -> ImageQualityResult:
    """
    Analyze PIL image for blur, lighting, and plant coverage.
    Returns ImageQualityResult object.
    """
    # Resize large images for speed during metric calculation
    img_resized = image.copy()
    img_resized.thumbnail((600, 600))
    
    # Convert to RGB
    img_rgb = img_resized.convert("RGB")
    rgb_array = np.array(img_rgb)
    
    # Convert to grayscale
    img_gray = img_rgb.convert("L")
    gray_array = np.array(img_gray, dtype=float)

    # Compute metrics
    blur_var = calculate_blur_variance(gray_array)
    mean_bright = calculate_brightness(gray_array)
    plant_coverage = calculate_plant_coverage(rgb_array)

    metrics = {
        "blur_variance": round(blur_var, 2),
        "mean_brightness": round(mean_bright, 2),
        "plant_coverage_pct": round(plant_coverage, 2),
    }

    issues = []
    warnings = []

    # Check blur
    if blur_var < IMAGE_THRESHOLDS["blur_min_variance"]:
        issues.append(f"Image appears blurry or out of focus (sharpness score: {blur_var:.1f})")

    # Check darkness / brightness
    if mean_bright < IMAGE_THRESHOLDS["darkness_min_mean"]:
        issues.append(f"Image is too dark (brightness: {mean_bright:.1f}/255)")
    elif mean_bright > IMAGE_THRESHOLDS["brightness_max_mean"]:
        issues.append(f"Image is overexposed/too bright (brightness: {mean_bright:.1f}/255)")

    # Check plant coverage
    if plant_coverage < IMAGE_THRESHOLDS["coverage_min_pct"]:
        issues.append(f"Insufficient plant/leaf visible in frame (coverage: {plant_coverage:.1f}%)")
    elif plant_coverage < 25.0:
        warnings.append(f"Plant leaf coverage is low ({plant_coverage:.1f}%). Moving closer may improve triage accuracy.")

    is_valid = len(issues) == 0

    return ImageQualityResult(
        is_valid=is_valid,
        issues=issues,
        metrics=metrics,
        warnings=warnings
    )
