import time
from typing import Optional


class HashTimeGenerator:
    """해시값과 시간을 기반으로 6자리 문자열을 생성하는 클래스"""

    DEFAULT_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    @classmethod
    def rotate_left(cls, x: int, r: int) -> int:
        return ((x << r) | (x >> (64 - r))) & 0xFFFFFFFFFFFFFFFF

    @classmethod
    def custom_hash(cls, data: bytes, seed: int = 0x9E3779B185EBCA87) -> int:
        v = seed
        prime1 = 11400714785074694791
        # print(f"data: {data}")
        for b in data:
            v ^= b
            v = (v * prime1) & 0xFFFFFFFFFFFFFFFF
            v = cls.rotate_left(v, 31)
            v ^= v >> 33
            # print(f"{b}", end="-")
        # print()
        return v

    @classmethod
    def to_base(cls, n: int, charset: str, length: int) -> str:
        base = len(charset)
        result = []
        for _ in range(length):
            result.append(charset[n % base])
            n //= base
        return "".join(reversed(result))

    @classmethod
    def generate_code(
        cls,
        value: str,
        time_in_seconds: int,
        charset: Optional[str] = None,
        code_length: int = 10,
    ) -> str:
        charset = charset or cls.DEFAULT_CHARSET
        base = len(charset)
        combined = f"{value}:{time_in_seconds}"
        # print(f"combined: {combined}")
        hash_value = cls.custom_hash(combined.encode("utf-8"))
        # print(f"hash_value: {hash_value}")
        return cls.to_base(hash_value % (base**code_length), charset, code_length)

    @classmethod
    def auto_generate_code(
        cls,
        value: str,
        current_time: int | None = None,
        offset: int = 0,
    ):
        if current_time is None:
            current_time = cls.get_current_time_in_seconds()
        code = cls.generate_code(value, current_time + offset)
        print(f"code: {code}, current_time: {current_time + offset}")
        return code

    @classmethod
    def auto_generate_code_list(cls, value: str, time_range: int = 10, offset: int = 0):
        code_list = []
        current_time = cls.get_current_time_in_seconds()
        for i in range(time_range):
            code_list.append(cls.auto_generate_code(value, current_time, -i))
        return code_list

    @staticmethod
    def get_current_time_in_seconds() -> int:
        """
        현재 시간을 초 단위로 반환

        Returns:
            현재 시간 (초 단위)
        """
        return int(time.time())


def main():
    """테스트 및 사용 예시"""
    print("=== Python 버전 테스트 ===")

    test_code = "e582a7a3-a936-4730-ba9f-c3988b2f73ec"
    while True:
        current_time = HashTimeGenerator.get_current_time_in_seconds()
        code = HashTimeGenerator.generate_code(test_code, current_time)
        print(code)
        time.sleep(1)


if __name__ == "__main__":
    main()
