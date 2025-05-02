from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from unittest.mock import patch

import io

from userprofile.models import CustomUser
from movie.models import Movie, MovieConvertables

from django.db.models.signals import post_save
from movie.signals import movie_post_save


class MovieViewTest(APITestCase):
    def setUp(self):
        post_save.disconnect(receiver=movie_post_save, sender=Movie)
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='user1', email='user1@test.com', password='secure123')
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('movies')

        fake_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        fake_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=fake_video,
            image_url=fake_image
        )
        post_save.connect(receiver=movie_post_save, sender=Movie)

    def test_get_movies_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Testfilm')

    def test_get_movies_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

class MovieConvertablesViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='user', email='user@test.com', password='test123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('movies-convert')

        post_save.disconnect(receiver=movie_post_save, sender=Movie)
        fake_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        fake_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        movie = Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=fake_video,
            image_url=fake_image
        )
        post_save.connect(receiver=movie_post_save, sender=Movie)
        self.convertables = MovieConvertables.objects.create(movie=movie)

    def test_get_convertables_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], self.convertables.movie.id)

    def test_get_convertables_unauthenticated(self):
        self.client.credentials()  # Token entfernen
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)