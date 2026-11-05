import ast
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def load_allowed_file():
    """Load only the validation function without starting the app."""
    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "allowed_file"
    )

    namespace = {
        "ALLOWED_EXTENSIONS": {"png", "jpg", "jpeg", "gif", "webp"}
    }
    exec(  # noqa: S102
        compile(ast.Module(body=[function], type_ignores=[]), str(APP_PATH), "exec"),
        namespace,
    )
    return namespace["allowed_file"]


allowed_file = load_allowed_file()


def test_valid_image_extensions():
    assert allowed_file("photo.png")
    assert allowed_file("photo.jpg")
    assert allowed_file("photo.jpeg")
    assert allowed_file("photo.gif")
    assert allowed_file("photo.webp")


def test_invalid_extensions():
    assert not allowed_file("document.pdf")
    assert not allowed_file("script.exe")
    assert not allowed_file("notes.txt")


def test_filename_without_extension():
    assert not allowed_file("image")


def test_uppercase_extensions():
    assert allowed_file("PHOTO.PNG")
    assert allowed_file("PHOTO.JPG")
