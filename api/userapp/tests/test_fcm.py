from django.test import TestCase

from common.component.fcm_component import FCMComponent


class TestFCMComponent(TestCase):
    def setUp(self):
        self.fcm = FCMComponent()
        self.test_token = "fWIuzhlnRhulm-AytVbrH2:APA91bFM9XdYKLpAwMpYPk0kmL3km0aXTUOANLHYfomFe7U5I4RibLFvvzXoBFOHZLZwp4U3k5skPKKhzDrExThSFoE_rnrpdSz4_x70ZyGAdnsfichgQGE"
        self.test_title = "Test Title"
        self.test_body = "Test Message Body"

    def test_send_message(self):
        # Act
        self.fcm.send_notification(self.test_token, self.test_title, self.test_body)

    # @patch('firebase_admin.messaging.send')
    # def test_send_message_failure(self, mock_send):
    #     # Arrange
    #     mock_send.side_effect = messaging.ApiCallError('Test error')

    #     # Act & Assert
    #     with self.assertRaises(messaging.ApiCallError):
    #         self.fcm.send_message(self.test_token, self.test_title, self.test_body)
