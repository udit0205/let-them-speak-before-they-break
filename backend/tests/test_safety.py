import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.safety import assess


def test_immediate_danger():
    result = assess("I am going to kill myself tonight")
    assert result.immediate_danger is True
    assert result.level == "high"


def test_elevated_signal():
    result = assess("I have been thinking about suicide")
    assert result.immediate_danger is False
    assert result.level == "elevated"


def test_normal_text():
    result = assess("I had a rough day at college and feel overwhelmed")
    assert result.immediate_danger is False
    assert result.level == "none"


if __name__ == "__main__":
    test_immediate_danger()
    test_elevated_signal()
    test_normal_text()
    print("Safety tests passed")
