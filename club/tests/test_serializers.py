from django.test import TestCase
from rest_framework import serializers


class PersonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=0, max_value=150)
    email = serializers.EmailField()

    def validate_age(self, value):
        """age 필드에 대한 custom validation"""
        if value < 18:
            raise serializers.ValidationError("성인만 가입할 수 있습니다.")
        return value

    def validate(self, data):
        """여러 필드를 동시에 검증하는 validation"""
        # name과 age가 모두 있을 때만 검증
        if "name" in data and "age" in data:
            if data["name"] == "admin" and data["age"] < 30:
                raise serializers.ValidationError("admin은 30세 이상이어야 합니다.")
        return data


class SerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {"name": "John Doe", "age": 25, "email": "john@example.com"}
        self.invalid_data = {"name": "Young Admin", "age": 20, "email": "not-an-email"}

    def test_valid_serialization(self):
        """유효한 데이터 직렬화 테스트"""
        serializer = PersonSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "John Doe")
        self.assertEqual(serializer.validated_data["age"], 25)
        self.assertEqual(serializer.validated_data["email"], "john@example.com")

    def test_invalid_email(self):
        """잘못된 이메일 형식 테스트"""
        serializer = PersonSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_age_validation(self):
        """나이 제한 검증 테스트"""
        data = self.valid_data.copy()
        data["age"] = 15
        serializer = PersonSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("age", serializer.errors)

    def test_admin_age_validation(self):
        """admin 나이 제한 검증 테스트"""
        data = self.valid_data.copy()
        data["name"] = "admin"
        data["age"] = 25
        serializer = PersonSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]),
            "admin은 30세 이상이어야 합니다.",
        )

    def test_partial_update(self):
        """부분 업데이트 테스트"""
        serializer = PersonSerializer(data=self.valid_data)
        serializer.is_valid()

        # partial=True로 부분 업데이트
        update_data = {"age": 30}
        partial_serializer = PersonSerializer(
            instance=serializer.validated_data, data=update_data, partial=True
        )
        self.assertTrue(partial_serializer.is_valid())
