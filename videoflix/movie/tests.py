from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from unittest.mock import patch
from rest_framework import status

import io

from userprofile.models import CustomUser
from movie.models import Movie, MovieConvertables, MovieProgress

from django.db.models.signals import post_save
from movie.signals import movie_post_save


class MovieViewTest(APITestCase):
    def setUp(self):
        post_save.disconnect(receiver=movie_post_save, sender=Movie)
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='user1', email='user1@test.com', password='secure123')
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('movies')

        test_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        test_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=test_video,
            image_url=test_image
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
        test_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        test_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        movie = Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=test_video,
            image_url=test_image
        )
        post_save.connect(receiver=movie_post_save, sender=Movie)
        self.convertables = MovieConvertables.objects.create(movie=movie)

    def test_get_convertables_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], self.convertables.movie.id)

    def test_get_convertables_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

class SingleMovieConvertablesViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='user', email='user@test.com', password='test123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        post_save.disconnect(receiver=movie_post_save, sender=Movie)
        test_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        test_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        self.movie = Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=test_video,
            image_url=test_image
        )
        post_save.connect(receiver=movie_post_save, sender=Movie)
        self.convertables = MovieConvertables.objects.create(movie=self.movie)

        self.valid_url = reverse('movie-convert', kwargs={'pk': self.convertables.pk})
        self.invalid_url = reverse('movie-convert', kwargs={'pk': 9999})

    def test_get_single_convertables_success(self):
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['movie'], self.movie.pk)

    def test_get_single_convertables_not_found(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_get_single_convertables_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 401)

class MovieProgressViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='user', email='user@test.com', password='test123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('movie-progress')

        post_save.disconnect(receiver=movie_post_save, sender=Movie)
        test_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        test_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        self.movie = Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=test_video,
            image_url=test_image
        )
        post_save.connect(receiver=movie_post_save, sender=Movie)
        self.progress = MovieProgress.objects.create(user=self.user, movie=self.movie, time=42.0)

    def test_get_movie_progress_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['movie'], self.movie.pk)
        self.assertEqual(float(response.data[0]['time']), 42.0)

    def test_get_movie_progress_empty_list(self):
        self.progress.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_movie_progress_unauthenticated(self):
        self.client.credentials()  # Auth entfernen
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

class MovieProgressSingleViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='user', email='user@test.com', password='test123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
       

        post_save.disconnect(receiver=movie_post_save, sender=Movie)
        test_video = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")
        test_image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")

        self.movie = Movie.objects.create(
            title='Testfilm',
            description='Mit Bild',
            genre='ACTION',
            video_url=test_video,
            image_url=test_image
        )
        post_save.connect(receiver=movie_post_save, sender=Movie)
        self.progress = MovieProgress.objects.create(user=self.user, movie=self.movie, time=42.0)
        self.url = reverse('single-movie-progress', kwargs={'pk': self.movie.pk})

    def test_get_existing_progress(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data['time']), 42.0)

    def test_get_nonexistent_progress(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_progress_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_create_new_progress(self):
        data = {'time': 33.5}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(MovieProgress.objects.filter(user=self.user, movie=self.movie).exists())
        self.assertEqual(MovieProgress.objects.get(user=self.user, movie=self.movie).time, 33.5)

    def test_update_existing_progress(self):
        data = {'time': 99.9}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(float(MovieProgress.objects.get(user=self.user, movie=self.movie).time), 99.9)

    def test_post_progress_unauthenticated(self):
        self.client.credentials()
        data = {'time': 22.0}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)


from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
# from yourapp.models import Movie, MovieConvertables

class MoviePostSaveSignalTest(TestCase):

    @patch('movie.signals.get_duration', return_value='123.4')
    @patch('movie.signals.convert120p.delay')
    @patch('movie.signals.convert360p.delay')
    @patch('movie.signals.convert720p.delay')
    @patch('movie.signals.convert1080p.delay')
    def test_movie_post_save_triggers_conversion(
        self, mock_1080, mock_720, mock_360, mock_120, mock_get_duration
    ):
        video_file = SimpleUploadedFile("test.mp4", b"00", content_type="video/mp4")

        movie = Movie.objects.create(
            title='Signal Test Movie',
            description='Signal test desc',
            genre='ACTION',
            video_url=video_file
        )

        # duration gesetzt?
        movie.refresh_from_db()
        self.assertEqual(float(movie.duration), float('123.4'))

        # Convertables erstellt?
        self.assertTrue(MovieConvertables.objects.filter(movie=movie).exists())

        # Alle Konvertierungsjobs aufgerufen?
        path = movie.video_url.path
        convertables_id = MovieConvertables.objects.get(movie=movie).id

        mock_120.assert_called_once_with(path, convertables_id)
        mock_360.assert_called_once_with(path, convertables_id)
        mock_720.assert_called_once_with(path, convertables_id)
        mock_1080.assert_called_once_with(path, convertables_id)
