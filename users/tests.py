from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class TestUserAuth(APITestCase):

    def setUp(self):
        self.register_url = '/auth/users/'
        self.token_url = '/auth/token/login/'

        self.user_data = {
            'email': 'test@example.com',
            'password': 'SuperSecret123',
            'username': 'Nurzhan'
        }

    def test_user_registration_and_login(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)


