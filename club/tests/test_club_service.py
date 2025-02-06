from django.test import TestCase

from club.models import GenerationMapping
from club.services.club_service import ClubService
from main.exceptions import CustomException, ErrorCode
from userapp.models import Provider, User


class ClubServiceTest(TestCase):
    def setUp(self):
        # Create a test user for all test cases.
        self.user = User.objects.create(identifier="testuser", provider=Provider.KAKAO)
        self.club_name = "Test Club"
        # Use a dummy image value (update if your image field requires a File object)
        self.image = "dummy_image.png"
        self.description = "A club for testing."
        # Make sure to supply all required fields for Generation; adjust as needed.
        self.generation_data = {
            "name": "Generation 1",
            # Add more generation-specific fields if needed.
        }

    def test_create_club_success(self):
        # Call the service to create a club
        club, member = ClubService.create_club(
            user=self.user,
            name=self.club_name,
            image=self.image,
            description=self.description,
            generation_data=self.generation_data,
        )

        # Club assertions
        self.assertIsNotNone(club.id)
        self.assertEqual(club.name, self.club_name)
        self.assertEqual(club.description, self.description)
        self.assertEqual(club.image, self.image)

        # Generation assertions (the current_generation was set in the service)
        generation = club.current_generation
        self.assertIsNotNone(generation)
        self.assertEqual(generation.club, club)
        self.assertEqual(generation.name, self.generation_data["name"])
        # Verify that the invite_code is a 6-digit string
        self.assertEqual(len(generation.invite_code), 6)
        self.assertTrue(generation.invite_code.isdigit())

        # Role assertions
        self.assertIsNotNone(club.default_role)  # member role assigned as default

        # Member assertions
        self.assertIsNotNone(member.id)
        self.assertEqual(member.user, self.user)
        self.assertEqual(member.club, club)
        self.assertEqual(member.last_user_generation.generation, generation)

        # Check that there's a generation mapping (the creator was set as owner)
        owner_mappings = GenerationMapping.objects.filter(
            member=member, generation=generation
        )
        self.assertEqual(owner_mappings.count(), 1)
        owner_mapping = owner_mappings.first()
        self.assertIsNotNone(owner_mapping.role)

    def test_create_club_duplicate_name(self):
        # Create the club once
        ClubService.create_club(
            user=self.user,
            name=self.club_name,
            image=self.image,
            description=self.description,
            generation_data=self.generation_data,
        )

        # Attempting to create a club with the same name should raise a CustomException
        with self.assertRaises(CustomException) as context:
            ClubService.create_club(
                user=self.user,
                name=self.club_name,
                image=self.image,
                description=self.description,
                generation_data=self.generation_data,
            )
        self.assertEqual(context.exception.error_code, ErrorCode.CLUB_ALREADY_EXISTS)
