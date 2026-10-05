def estimate_distance(pixel_width: float, real_width: float, focal_length: float) -> float:
    """Pinhole model: distance = real width * focal length / width in pixels."""
    if pixel_width <= 0:
        return float("inf")
    return (real_width * focal_length) / pixel_width


def get_direction(object_center: float, canvas_width: float) -> str:
    third = canvas_width / 3
    if object_center < third:
        return "to your left"
    if object_center > 2 * third:
        return "to your right"
    return "ahead"
