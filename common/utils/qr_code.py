import random
import string
import uuid
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import qrcode
from django.core.files.base import ContentFile


def generate_random_code(length: int = 15) -> str:
    """
    지정된 길이의 랜덤 코드를 생성하는 함수

    Args:
        length (int): 생성할 코드의 길이 (기본값: 15)

    Returns:
        str: 생성된 랜덤 코드
    """
    # 사용할 문자 세트 정의 (대문자, 소문자, 숫자)
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits

    # 랜덤 코드 생성
    random_code = "".join(random.choice(characters) for _ in range(length))
    return random_code


def generate_qr_code(data: str, file_name: str = "qr_code.png") -> str:
    """
    QR 코드를 생성하고 이미지 파일로 저장하는 함수

    Args:
        data (str): QR 코드에 인코딩할 데이터
        file_name (str): 저장할 파일 이름 (기본값: qr_code.png)

    Returns:
        str: 저장된 파일의 경로
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")

    # 현재 디렉토리에 이미지 저장
    output_path = Path(file_name)
    qr_image.save(output_path)

    return str(output_path.absolute())


def generate_url_qr_code(url: str, file_name: str = "url_qr_code.png") -> str:
    """
    URL을 QR 코드로 변환하여 이미지 파일로 저장하는 함수

    Args:
        url (str): QR 코드로 변환할 URL
        file_name (str): 저장할 파일 이름 (기본값: url_qr_code.png)

    Returns:
        str: 저장된 파일의 경로

    Raises:
        ValueError: 유효하지 않은 URL이 입력된 경우
    """
    # URL 유효성 검사
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("유효하지 않은 URL 형식입니다.")
    except Exception as e:
        raise ValueError(f"URL 검증 실패: {str(e)}")

    # QR 코드 생성
    return generate_qr_code(url, file_name)


def test_generate_qr_code():
    """
    QR 코드 생성 함수를 테스트하는 함수
    """
    # 테스트할 데이터
    test_data = generate_random_code()
    test_file = "test_qr_code.png"

    # QR 코드 생성
    file_path = generate_qr_code(test_data, test_file)

    # 파일이 생성되었는지 확인
    assert Path(file_path).exists(), "QR 코드 파일이 생성되지 않았습니다."

    # 파일 크기가 0보다 큰지 확인
    assert Path(file_path).stat().st_size > 0, "QR 코드 파일이 비어있습니다."

    print("QR 코드 생성 테스트 완료!")
    return True


def generate_uuid_qr_for_imagefield() -> tuple[str, ContentFile]:
    """
    UUID QR 코드를 생성하고 Django ImageField에 적합한 형식으로 반환하는 함수

    Returns:
        tuple[str, ContentFile]: (생성된 UUID 문자열, QR 코드 이미지 ContentFile)
    """
    # UUID 생성
    unique_id = str(uuid.uuid4())

    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(unique_id)
    qr.make(fit=True)

    # QR 코드 이미지 생성
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # PIL Image를 BytesIO로 변환
    image_io = BytesIO()
    qr_image.save(image_io, format="JPEG")
    image_io.seek(0)

    # ContentFile 생성
    image_file = ContentFile(image_io.getvalue(), name=f"{unique_id}.jpg")

    return unique_id, image_file


if __name__ == "__main__":
    # 랜덤 코드 생성 예시
    random_code = generate_random_code()
    print(f"생성된 랜덤 코드: {random_code}")

    # QR 코드 생성
    qr_path = generate_qr_code(random_code)
    print(f"QR 코드가 생성되었습니다: {qr_path}")

    # 테스트 실행
    test_generate_qr_code()

    # URL QR 코드 생성 예시
    try:
        url = "wasso://event/1"
        url_qr_path = generate_url_qr_code(url)
        print(f"URL QR 코드가 생성되었습니다: {url_qr_path}")
    except ValueError as e:
        print(f"오류 발생: {str(e)}")
