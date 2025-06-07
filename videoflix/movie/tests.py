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
from unittest.mock import patch
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

class MovieViewTest(APITestCase):
    """
    Test suite for the Movie API endpoints using Django REST Framework's APITestCase.

    This class tests basic authentication and data retrieval behaviors of the movie list API.

    Key features:
    - Sets up test data, including a user with token authentication and a sample Movie instance.
    - Temporarily disconnects and reconnects the `movie_post_save` signal receiver to avoid side effects during setup.
    - Uses Django REST Framework's APIClient for simulating HTTP requests.

    Test methods:
    - setUp():  
    Prepares the test environment by creating a test user, authentication token, API client, and a sample movie with associated video and image files.

    - test_get_movies_authenticated():  
    Sends a GET request to the movie list endpoint with valid token authentication.  
    Asserts that the response status code is 200 (OK), the response contains one movie, and the movie title matches the test data.

    - test_get_movies_unauthenticated():  
    Sends a GET request without authentication.  
    Asserts that the response status code is 401 (Unauthorized), ensuring access control is enforced.
    
    Notes:
    - The tests ensure the movie list endpoint requires authentication and returns correct movie data.
    - Uses `SimpleUploadedFile` to simulate file uploads in tests.
    """
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
            video_file=test_video,
            image_file=test_image
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
    """
    Test suite for the MovieConvertables API endpoints using Django REST Framework's APITestCase.

    This class verifies authentication and data retrieval for the movie convertables endpoint.

    Key features:
    - Sets up test environment including user, token authentication, API client, and test data.
    - Creates a Movie instance with associated video and image files.
    - Creates a MovieConvertables instance linked to the created Movie.
    - Temporarily disconnects and reconnects the `movie_post_save` signal during setup to prevent side effects.

    Test methods:
    - setUp():  
    Prepares the test environment with a user, authentication token, API client credentials,
    test movie, and associated convertables data.

    - test_get_convertables_authenticated():  
    Sends a GET request with authentication to the convertables endpoint.  
    Asserts response status 200 (OK), response contains one item, and the movie ID matches the expected convertables record.

    - test_get_convertables_unauthenticated():  
    Sends a GET request without authentication.  
    Asserts response status 401 (Unauthorized) to verify access control.

    Notes:
    - Tests ensure the convertables API endpoint requires authentication and correctly returns related data.
    - Uses `SimpleUploadedFile` to simulate file uploads during testing.
    """
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
            video_file=test_video,
            image_file=test_image
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
    """
    Test suite for retrieving a single MovieConvertables instance via the API using Django REST Framework's APITestCase.

    This class tests authenticated and unauthenticated access as well as handling of valid and invalid resource IDs.

    Key features:
    - Sets up test environment with a user, token authentication, API client, and test data.
    - Creates a Movie and a linked MovieConvertables instance.
    - Defines valid and invalid URLs for accessing single convertables by primary key.

    Test methods:
    - setUp():  
    Prepares the environment, including user, authentication token, test Movie, MovieConvertables, and URLs for testing.

    - test_get_single_convertables_success():  
    Sends a GET request with authentication to a valid convertables URL.  
    Asserts response status 200 (OK) and verifies the returned movie ID matches the test Movie.

    - test_get_single_convertables_not_found():  
    Sends a GET request with authentication to an invalid convertables URL.  
    Asserts response status 404 (Not Found) to confirm proper error handling.

    - test_get_single_convertables_unauthenticated():  
    Sends a GET request without authentication to a valid URL.  
    Asserts response status 401 (Unauthorized) to confirm access control enforcement.

    Notes:
    - Tests ensure correct retrieval of single convertables, error handling for missing resources,
    and authentication requirements.
    - Uses `SimpleUploadedFile` for simulating file uploads during test setup.
    """
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
            video_file=test_video,
            image_file=test_image
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
    """
    Test suite for the MovieProgress API endpoints using Django REST Framework's APITestCase.

    This class tests authenticated access, retrieval of user-specific movie progress data,
    and behavior when no progress data exists.

    Key features:
    - Sets up a test user, token authentication, API client, and test data including a Movie and a MovieProgress record.
    - Temporarily disconnects and reconnects the `movie_post_save` signal during setup to avoid side effects.

    Test methods:
    - setUp():  
    Initializes the test environment with user, token, client credentials, a Movie instance,
    and a MovieProgress entry with a specific playback time.

    - test_get_movie_progress_success():  
    Sends an authenticated GET request to retrieve movie progress data.  
    Verifies response status 200 (OK), data length, correct movie ID, and playback time.

    - test_get_movie_progress_empty_list():  
    Deletes the existing MovieProgress record, then sends an authenticated GET request.  
    Asserts response status 200 (OK) and that the returned data is an empty list.

    - test_get_movie_progress_unauthenticated():  
    Sends a GET request without authentication.  
    Asserts response status 401 (Unauthorized), ensuring access control is enforced.

    Notes:
    - Tests ensure the movie progress endpoint correctly handles existing and missing data.
    - Uses `SimpleUploadedFile` to simulate file uploads during setup.
    """
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
            video_file=test_video,
            image_file=test_image
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
    """
    Test suite for single movie progress API endpoint using Django REST Framework's APITestCase.

    This class tests retrieving, creating, and updating a user's progress for a specific movie,
    as well as authentication enforcement.

    Key features:
    - Sets up test user, token authentication, API client, and a Movie with associated MovieProgress.
    - Defines URL for accessing single movie progress by movie primary key.

    Test methods:
    - setUp():  
    Initializes user, token, client credentials, creates Movie and MovieProgress instances,
    and sets the URL for single movie progress.

    - test_get_existing_progress():  
    Sends an authenticated GET request to retrieve existing progress.  
    Asserts HTTP 200 OK and verifies returned progress time matches stored value.

    - test_get_nonexistent_progress():  
    Sends an authenticated GET request when no progress exists.  
    Asserts HTTP 200 OK to confirm the endpoint handles missing progress gracefully.

    - test_get_progress_unauthenticated():  
    Sends a GET request without authentication.  
    Expects HTTP 401 Unauthorized status.

    - test_create_new_progress():  
    Sends an authenticated POST request with progress time data to create new progress.  
    Asserts HTTP 201 Created, verifies progress record existence and stored time value.

    - test_update_existing_progress():  
    Sends an authenticated POST request with updated time data to modify existing progress.  
    Asserts HTTP 201 Created and checks that progress time was updated accordingly.

    - test_post_progress_unauthenticated():  
    Sends a POST request without authentication.  
    Expects HTTP 401 Unauthorized status.

    Notes:
    - Uses `SimpleUploadedFile` to simulate media uploads during setup.
    - Ensures that the endpoint supports idempotent creation and updates of progress records.
    """

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
            video_file=test_video,
            image_file=test_image
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

class MoviePostSaveSignalTest(TestCase):
    """
    Unit test for the Movie post-save signal handling using Django's TestCase and unittest.mock.patch.

    This test verifies that saving a Movie instance triggers:
    - The retrieval of video duration via the `get_duration` function.
    - Creation of a related MovieConvertables instance.
    - Asynchronous conversion tasks for multiple video resolutions are queued.

    Key features:
    - Uses patch decorators to mock:
    - `get_duration` function returning a fixed duration ('123.4').
    - Celery tasks: `convert120p.delay`, `convert360p.delay`, `convert720p.delay`, and `convert1080p.delay`.
    - Creates a Movie instance with a mocked video file.
    - Checks that the Movie's duration is correctly set from the mocked `get_duration`.
    - Asserts that a corresponding MovieConvertables object is created.
    - Verifies each video conversion task is called exactly once with correct arguments.

    Test methods:
    - test_movie_post_save_triggers_conversion():  
    Main test method that exercises the post-save signal logic and asserts all expected side effects.

    Notes:
    - Ensures that the signal integration properly handles asynchronous task dispatch and model updates.
    - Provides confidence that video processing workflow is triggered after movie creation.
    """

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
            video_file=video_file
        )

        movie.refresh_from_db()
        self.assertEqual(float(movie.duration), float('123.4'))
        self.assertTrue(MovieConvertables.objects.filter(movie=movie).exists())

        path = movie.video_file.path
        convertables_id = MovieConvertables.objects.get(movie=movie).id

        mock_120.assert_called_once_with(path, convertables_id)
        mock_360.assert_called_once_with(path, convertables_id)
        mock_720.assert_called_once_with(path, convertables_id)
        mock_1080.assert_called_once_with(path, convertables_id)
