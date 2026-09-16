"""Tests for image preparation: downscaling and HEIC handling (no API)."""

import io

import pytest
from PIL import Image

from prompt2box.detector import _prepare_image, _register_heif


def test_large_jpeg_is_downscaled_but_dims_are_original(tmp_path):
    big = tmp_path / "big.jpg"
    Image.new("RGB", (4000, 3000), (120, 120, 120)).save(big)

    data, mime, w, h = _prepare_image(big, max_size=1536)

    # Original dimensions are reported (boxes map back to full res)...
    assert (w, h) == (4000, 3000)
    # ...but the uploaded bytes are a smaller JPEG.
    assert mime == "image/jpeg"
    with Image.open(io.BytesIO(data)) as sent:
        assert max(sent.size) <= 1536
        assert sent.size != (4000, 3000)


def test_large_png_stays_png(tmp_path):
    """Large PNGs (screenshots/diagrams) are kept lossless, not JPEG-ified."""
    big = tmp_path / "big.png"
    Image.new("RGBA", (3000, 2000), (10, 20, 30, 255)).save(big)

    data, mime, w, h = _prepare_image(big, max_size=1536)

    assert (w, h) == (3000, 2000)
    assert mime == "image/png"
    with Image.open(io.BytesIO(data)) as sent:
        assert sent.format == "PNG"
        assert max(sent.size) <= 1536


def test_small_image_passes_through_untouched(tmp_path):
    small = tmp_path / "small.png"
    Image.new("RGB", (400, 200), (10, 20, 30)).save(small)

    data, mime, w, h = _prepare_image(small, max_size=1536)

    assert (w, h) == (400, 200)
    assert mime == "image/png"
    assert data == small.read_bytes()  # original bytes, not re-encoded


def test_max_size_zero_disables_downscaling(tmp_path):
    big = tmp_path / "big.jpg"
    Image.new("RGB", (4000, 3000), (1, 2, 3)).save(big)
    data, mime, w, h = _prepare_image(big, max_size=0)
    assert (w, h) == (4000, 3000)
    assert data == big.read_bytes()


def test_register_heif_noop_for_non_heic(tmp_path):
    # Should not raise for ordinary formats.
    _register_heif(tmp_path / "photo.jpg")
    _register_heif(tmp_path / "photo.png")


def test_heic_without_pillow_heif_raises_clear_error(tmp_path):
    try:
        import pillow_heif  # noqa: F401

        pytest.skip("pillow-heif is installed; cannot test the missing-dep path")
    except ImportError:
        pass

    with pytest.raises(RuntimeError, match="pillow-heif"):
        _register_heif(tmp_path / "photo.heic")


def test_mime_type_follows_decoded_format_not_extension(tmp_path):
    """A JPEG saved under a misleading .png name is still uploaded as image/jpeg."""
    misnamed = tmp_path / "actually_a_jpeg.png"
    Image.new("RGB", (64, 64), (5, 5, 5)).save(misnamed, format="JPEG")

    _, mime, _, _ = _prepare_image(misnamed, max_size=1536)

    assert mime == "image/jpeg"


def test_crop_registers_heif_for_its_source(tmp_path, monkeypatch):
    """crop() must go through the same HEIF registration as detect() and drawing."""
    import prompt2box.detector as det_mod

    seen: list = []
    monkeypatch.setattr(det_mod, "_register_heif", lambda p: seen.append(p))
    src = tmp_path / "photo.png"
    Image.new("RGB", (40, 20), (1, 2, 3)).save(src)

    det = det_mod.Detection(label="x", x_min=0, y_min=0, x_max=10, y_max=10)
    out = det.crop(src, tmp_path / "crop.png")

    assert out.is_file()
    assert seen == [src]
