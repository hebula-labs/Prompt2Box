"""Tests for the CLI: helpers, plus end-to-end runs with a fake detector (no API access)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from prompt2box import cli
from prompt2box.cli import _default_output_path, _load_dotenv


def test_dotenv_loads_missing_keys(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(
        "# a comment\nGEMINI_API_KEY=from_dotenv\nQUOTED='val ue'\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("QUOTED", raising=False)

    _load_dotenv()

    import os

    assert os.environ["GEMINI_API_KEY"] == "from_dotenv"
    assert os.environ["QUOTED"] == "val ue"


def test_dotenv_does_not_override_real_env(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("GEMINI_API_KEY=from_dotenv\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "real_env_wins")

    _load_dotenv()

    import os

    assert os.environ["GEMINI_API_KEY"] == "real_env_wins"


def test_dotenv_absent_is_noop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no .env here
    _load_dotenv()  # must not raise


def test_dotenv_handles_export_prefix(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("export GEMINI_API_KEY=exp_val\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    _load_dotenv()

    import os

    assert os.environ["GEMINI_API_KEY"] == "exp_val"


def test_dotenv_strips_unquoted_inline_comment(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("GEMINI_API_KEY=val123 # my key\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    _load_dotenv()

    import os

    assert os.environ["GEMINI_API_KEY"] == "val123"


def test_dotenv_keeps_hash_inside_quotes(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text('GEMINI_API_KEY="a#b#c"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    _load_dotenv()

    import os

    assert os.environ["GEMINI_API_KEY"] == "a#b#c"


def test_default_output_keeps_safe_suffix():
    assert _default_output_path(Path("a/photo.jpg")).name == "photo_boxed.jpg"
    assert _default_output_path(Path("a/photo.png")).name == "photo_boxed.png"


def test_default_output_falls_back_to_png_for_unsafe():
    # HEIC/GIF can't always be written by Pillow — annotated copy becomes PNG.
    assert _default_output_path(Path("a/photo.heic")).name == "photo_boxed.png"
    assert _default_output_path(Path("a/clip.gif")).name == "clip_boxed.png"


# ---------------------------------------------------------------------------
# End-to-end runs of main() with a fake Detector (no network)
# ---------------------------------------------------------------------------
class _FakeDetector:
    """Stand-in for ``prompt2box.cli.Detector``: no network, one canned detection.

    Records the constructor and ``detect()`` keyword arguments so tests can
    assert that CLI flags reach the library with the right values.
    """

    init_kwargs: dict = {}
    detect_kwargs: dict = {}

    def __init__(self, **kwargs):
        type(self).init_kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return None

    def detect(self, image_path, **kwargs):
        from prompt2box.detector import Detection, DetectionResult

        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")
        type(self).detect_kwargs = kwargs
        cat = Detection(label="cat", x_min=10, y_min=10, x_max=100, y_max=90)
        return DetectionResult(image_path=path, image_size=(400, 200), objects=[cat])


def _write_png(path: Path) -> Path:
    Image.new("RGB", (400, 200), (210, 210, 210)).save(path)
    return path


def test_main_end_to_end_with_fake_detector(monkeypatch, tmp_path, capsys):
    """JSON on stdout, annotated image and JSON file on disk, flags forwarded, exit 0."""
    monkeypatch.setattr(cli, "Detector", _FakeDetector)
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFake")
    img = _write_png(tmp_path / "scene.png")
    json_out = tmp_path / "out.json"

    code = cli.main(
        [str(img), "-j", str(json_out), "-c", "cat", "dog", "--refine", "-m", "gemini-2.5-pro"]
    )

    assert code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert [item["label"] for item in payload] == ["cat"]
    assert json.loads(json_out.read_text(encoding="utf-8")) == payload
    assert (tmp_path / "scene_boxed.png").is_file()
    assert "detected 1 item(s)" in captured.err
    assert _FakeDetector.init_kwargs["model"] == "gemini-2.5-pro"
    assert _FakeDetector.init_kwargs["api_key"] == "AIzaFake"
    assert _FakeDetector.detect_kwargs["classes"] == ["cat", "dog"]
    assert _FakeDetector.detect_kwargs["refine"] is True


def test_main_no_image_skips_annotated_output(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "Detector", _FakeDetector)
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFake")
    img = _write_png(tmp_path / "scene.png")

    assert cli.main([str(img), "--no-image"]) == 0
    assert not (tmp_path / "scene_boxed.png").exists()
    assert json.loads(capsys.readouterr().out)[0]["label"] == "cat"


def test_main_vertex_flags_reach_detector(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "Detector", _FakeDetector)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    img = _write_png(tmp_path / "scene.png")

    code = cli.main([str(img), "--no-image", "--vertex", "--project", "proj", "--location", "eu"])

    assert code == 0
    assert _FakeDetector.init_kwargs["vertexai"] is True
    assert _FakeDetector.init_kwargs["project"] == "proj"
    assert _FakeDetector.init_kwargs["location"] == "eu"
    assert "api_key" not in _FakeDetector.init_kwargs


def test_main_without_credentials_exits_2(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)  # no .env here
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    assert cli.main([str(tmp_path / "scene.png")]) == 2
    assert "no API key" in capsys.readouterr().err


def test_main_missing_image_exits_2(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "Detector", _FakeDetector)
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFake")

    assert cli.main([str(tmp_path / "missing.png"), "--no-image"]) == 2
    assert "Image not found" in capsys.readouterr().err


def test_main_detection_failure_exits_1(monkeypatch, tmp_path, capsys):
    class ExplodingDetector(_FakeDetector):
        def detect(self, image_path, **kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli, "Detector", ExplodingDetector)
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaFake")
    img = _write_png(tmp_path / "scene.png")

    assert cli.main([str(img)]) == 1
    assert "detection failed: boom" in capsys.readouterr().err


def test_version_flag_prints_version_and_exits_0(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0
    assert capsys.readouterr().out.startswith("prompt2box ")


def test_python_dash_m_entry_point():
    """``python -m prompt2box`` behaves like the console script."""
    proc = subprocess.run(
        [sys.executable, "-m", "prompt2box", "--version"],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).resolve().parent.parent,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("prompt2box ")
