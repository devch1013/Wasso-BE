from api.userapp.enums import Provider
from api.userapp.models.user import User


class ClubTestUtils:
    @classmethod
    def get_test_users(cls, count: int = 2):
        users = []
        for i in range(count):
            users.append(
                User.objects.create_user(
                    identifier=f"testuser{i}",
                    username=f"testuser{i}",
                    email=f"testuser{i}@example.com",
                    provider=Provider.GOOGLE,
                    initialized=True,
                )
            )
        return users
