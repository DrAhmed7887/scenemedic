"""Imagen 3 prop generator."""
from vertexai.preview.vision_models import ImageGenerationModel

_img = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")


def generate_prop(prompt: str, aspect_ratio: str = "16:9") -> str:
    """Generate a photorealistic on-set prop image. Returns GCS URI of the asset."""
    res = _img.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio=aspect_ratio,
        safety_filter_level="block_some",
        person_generation="dont_allow",
    )
    return res.images[0]._gcs_uri  # type: ignore[attr-defined]
