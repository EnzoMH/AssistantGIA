import re
import unicodedata

def remove_chinese_characters(text: str) -> str:
    """중국어 문자를 제거합니다."""
    return re.sub(r"[\u4e00-\u9fff]+", "", text)

def remove_control_characters(text: str) -> str:
    """제어 문자를 제거합니다."""
    return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")

def preprocess_text(text: str) -> str:
    """텍스트 전처리 작업을 수행합니다."""
    text = remove_chinese_characters(text)
    text = remove_control_characters(text)
    # 추가적인 전처리 작업을 여기에서 수행할 수 있습니다.
    return text
