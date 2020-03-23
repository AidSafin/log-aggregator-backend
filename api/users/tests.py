import http
from itertools import product

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.mixins import ViewSetTestMixin


class UsersTestCase(APITestCase,
                    ViewSetTestMixin):
    _basename = 'users'
    fixtures = ('users',)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = get_user_model().objects.get(id=1)
        cls.admin_password = "qwerty123"

        cls.user = get_user_model().objects.get(id=2)
        cls.user_password = 'qwerty123'

        # data for new test user
        cls.data = {
            "first_name": "Алексей",
            "last_name": "Васьков",
            "patronymic": "Иванович",
            "email": "alexvaskov@gmail.com",
            "password": "qwErTy1"
        }

    def _auth_header(self, login, password):
        url = self.reverse_view_url(action='login')
        data = dict(email=login, password=password)
        response = self.client.post(url, data)
        return {
            'HTTP_AUTHORIZATION': 'Token {}'.format(response.data['token'])
        }

    def _user_token(self):
        return self._auth_header(self.user.email, self.user_password)

    def _admin_token(self):
        return self._auth_header(self.admin.email, self.admin_password)

    def test_create_201(self):
        url = self.reverse_view_url(action='create')
        response = self.client.post(url, self.data)

        self.assertEqual(http.HTTPStatus.CREATED, response.status_code, response.data)

    def test_create_400(self):
        url = self.reverse_view_url(action='create')
        response = self.client.post(url, {})
        self.assertEqual(http.HTTPStatus.BAD_REQUEST, response.status_code, response.data)

    def test_login_admin(self):
        url = self.reverse_view_url(action='login')
        data = dict(email=self.admin.email, password=self.admin_password)
        response = self.client.post(url, data)

        self.assertEqual(http.HTTPStatus.OK, response.status_code, response.data)
        self.assertSetEqual({'token', 'user_id', 'first_name', 'last_name'}, set(response.data), response.data)
        self.assertEqual(response.data['user_id'], self.admin.id)

    def test_login_200(self):
        url = self.reverse_view_url(action='login')
        data = dict(email=self.user.email, password=self.user_password)
        response = self.client.post(url, data)
        self.assertEqual(http.HTTPStatus.OK, response.status_code, response.data)

        old_token_key = self.user.token.key
        self.assertSetEqual({'token', 'user_id', 'first_name', 'last_name'}, set(response.data), response.data)
        self.assertEqual(response.data['user_id'], self.user.id)

        response = self.client.post(url, data)
        self.assertEqual(http.HTTPStatus.OK, response.status_code, response.data)

        self.user.refresh_from_db()
        new_token_key = self.user.token.key

        self.assertNotEqual(old_token_key, new_token_key)

    def test_login_400_wrong_credentials(self):
        url = self.reverse_view_url(action='login')

        wrong_emails = (None, 'missed', 'email', -1, 1.0, 'email@email.email')
        wrong_passwords = (None, 'missed', 'password', -1, 1.0, True)
        expected_statuses = (http.HTTPStatus.UNAUTHORIZED, http.HTTPStatus.BAD_REQUEST)

        # test wrong email-password pairs
        for email, password in product(wrong_emails, wrong_passwords):
            data = dict(email=email, password=password)
            if email == 'missed':
                data.pop('email')
            if password == 'missed':
                data.pop('password')
            response = self.client.post(url, data)
            self.assertIn(response.status_code, expected_statuses, (email, password))

    def test_retrieve_admin(self):
        url = self.reverse_view_url(action='retrieve', pk=self.admin.pk)
        response = self.client.get(url, **self._admin_token())

        self.assertEqual(response.status_code, http.HTTPStatus.OK, response.data)
        self.assertSetEqual({'id', 'first_name', 'last_name', 'patronymic', 'email', 'is_staff'}, set(response.data))

    def test_retrieve_200(self):
        url = self.reverse_view_url(action='retrieve', pk=self.user.pk)
        response = self.client.get(url, **self._user_token())

        self.assertEqual(response.status_code, http.HTTPStatus.OK, response.data)
        self.assertSetEqual({'id', 'first_name', 'last_name', 'patronymic', 'email', 'is_staff'}, set(response.data))

    def test_retrieve_401(self):
        url = self.reverse_view_url(action='retrieve', pk=self.user.pk)
        response = self.client.get(url)

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED, response.data)

    def test_retrieve_403(self):
        url = self.reverse_view_url(action='retrieve', pk=self.admin.id)
        response = self.client.get(url, **self._user_token())

        self.assertEqual(response.status_code, http.HTTPStatus.FORBIDDEN, response.data)

    def test_retrieve_404(self):
        url = self.reverse_view_url(action='retrieve', pk=1000)
        response = self.client.get(url, **self._user_token())

        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND, response.data)

    def test_update_401(self):
        url = self.reverse_view_url(action='update', pk=self.user.pk)
        response = self.client.put(url, self.data)

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED, response.data)

    def test_update_403(self):
        url = self.reverse_view_url(action='update', pk=self.admin.pk)
        response = self.client.put(url, self.data, **self._user_token())

        self.assertEqual(response.status_code, http.HTTPStatus.FORBIDDEN, response.data)

    def test_partial_update_200(self):
        url = self.reverse_view_url(action='partial_update', pk=self.user.pk)
        data = dict(first_name='new_first_name')
        response = self.client.patch(url, data, **self._user_token())
        self.assertEqual(response.status_code, http.HTTPStatus.OK, response.data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data['first_name'])

    def test_partial_update_401(self):
        url = self.reverse_view_url(action='partial_update', pk=self.user.pk)
        response = self.client.patch(url, self.data)

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED, response.data)

    def test_partial_update_403(self):
        url = self.reverse_view_url(action='partial_update', pk=self.admin.pk)
        response = self.client.patch(url, self.data, **self._user_token())

        self.assertEqual(response.status_code, http.HTTPStatus.FORBIDDEN, response.data)

    # TODO: list, destroy
