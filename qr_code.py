import qrcode
from pathlib import Path
import random
import string

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
    random_code = ''.join(random.choice(characters) for _ in range(length))
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

if __name__ == "__main__":
    # 랜덤 코드 생성 예시
    random_code = generate_random_code()
    print(f"생성된 랜덤 코드: {random_code}")
    
    # QR 코드 생성
    qr_path = generate_qr_code(random_code)
    print(f"QR 코드가 생성되었습니다: {qr_path}")
    
    # 테스트 실행
    test_generate_qr_code()
