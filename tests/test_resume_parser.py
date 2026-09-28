from io import BytesIO

from src.resume_parser import extract_text_from_upload


class Upload:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


def test_txt_extraction():
    result = extract_text_from_upload(
        Upload("resume.txt", b"Python\nFastAPI\nMachine Learning")
    )
    assert "FastAPI" in result


def test_empty_file():
    try:
        extract_text_from_upload(Upload("resume.txt", b""))
        assert False
    except ValueError:
        assert True
