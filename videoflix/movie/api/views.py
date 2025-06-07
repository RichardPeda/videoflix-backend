from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page, cache_control
from django.utils.decorators import method_decorator
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from movie.models import ConnectionTestFile, Movie, MovieConvertables, MovieProgress
from movie.api.serializers import MovieSerializer, MovieConvertablesSerializer, TestFileSerializer, MovieProgressSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny



CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class MovieView(APIView):
    """
    API view to retrieve a list of all movies.

    Requires token authentication and user to be authenticated.

    GET:
        Returns a list of movies ordered by creation date descending.
        Serialized using MovieSerializer with request context for full URLs.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

#   @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):        
        movies = Movie.objects.all()
        movies = movies.order_by('-created_at')
        serializer = MovieSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
      
class MovieConvertablesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        Returns a list of all available movie convertables.

        This endpoint retrieves all entries from the MovieConvertables model and returns them as serialized data.
        Each convertable represents a video that has been uploaded and processed using ffmpeg.
        During processing, the original video is converted and stored in multiple resolutions: 120p, 360p, 720p, and 1080p.

        Args:
            request (Request): Authenticated GET request with valid token.

        Returns:
            Response (JSON):
                - 200 OK:
                    A list of movie convertables, each represented as serialized JSON data.

        Authentication:
            Required - Token-based authentication

        Permissions:
            Only authenticated users (IsAuthenticated)
        """
        convertables = MovieConvertables.objects.all()
        serializer = MovieConvertablesSerializer(convertables, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SingleMovieConvertablesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        """
        Retrieves a single movie convertable by its ID.

        This endpoint returns detailed information about a specific movie convertable, identified by its primary key (ID).
        Each convertable represents a video that was uploaded and processed using FFmpeg.
        During processing, the video is converted and saved in multiple resolutions: 120p, 360p, 720p, and 1080p.

        Args:
            request (Request): Authenticated GET request with valid token.
            pk (int): Primary key (ID) of the movie convertable to retrieve.

        Returns:
            Response (JSON):
                - 200 OK:
                    A serialized representation of the requested movie convertable.
                - 404 Not Found:
                    If no convertable with the given ID exists.

        Authentication:
            Required - Token-based authentication

        Permissions:
            Only authenticated users (IsAuthenticated)
        """
        try:
            convertables = MovieConvertables.objects.get(pk=pk)
            serializer = MovieConvertablesSerializer(convertables, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class ConnectionTestView(APIView):
    def get(self, request):
        """
        Returns a test file used to verify connection or media access.

        This endpoint is typically used to test client-server connectivity or to validate media streaming functionality.
        It retrieves a predefined test file (with primary key 1) from the database and returns its serialized representation.

        Args:
            request (Request): GET request (authentication not required, unless enforced elsewhere).

        Returns:
            Response (JSON):
                - 200 OK:
                    A serialized representation of the test file.

        Notes:
            - This endpoint always retrieves the file with `pk=1`.
            - Useful for connection checks, media playback testing, or system diagnostics.
        """
        try:
            testfile = ConnectionTestFile.objects.get(pk=1)
            serializer = TestFileSerializer(testfile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

class MovieProgressView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        Retrieves the movie watch progress for the authenticated user.

        This endpoint returns a list of progress entries that track how far the current user has watched each movie.
        It is useful for implementing resume/playback position features in a video platform.

        Args:
            request (Request): Authenticated GET request with valid token.

        Returns:
            Response (JSON):
                - 200 OK:
                    A list of movie progress entries for the current user.
                - 204 No Content:
                    If no progress entries are found or an unexpected error occurs.

        Authentication:
            Required – Token-based authentication

        Permissions:
            Only authenticated users (IsAuthenticated)

        Notes:
            - Each progress entry typically includes information such as movie ID and timestamp/position.
            - Consider handling specific exceptions (e.g. database errors) instead of a bare `except` for clearer error diagnostics.
        """
        progress = MovieProgress.objects.filter(user=request.user)
        serializer = MovieProgressSerializer(progress, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MovieProgressSingleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk): 
        """
        Retrieves the movie watch progress for a specific movie and the authenticated user.

        This endpoint returns the progress entry for the given movie, allowing the user to resume playback 
        from their last watched position.

        Args:
            request (Request): Authenticated GET request with valid token.
            pk (int): Primary key (ID) of the movie.

        Returns:
            Response (JSON):
                - 200 OK:
                    A serialized progress entry with the last watched timestamp.
                - 204 No Content:
                    If no progress entry exists for this movie/user combination.

        Authentication:
            Required - Token-based authentication

        Permissions:
            Only authenticated users (IsAuthenticated)
        """
        progress = MovieProgress.objects.filter(movie=pk, user=request.user).first()
        if progress:
            serializer = MovieProgressSerializer(progress)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def post(self,request, pk):
        """
        Creates or updates the user's watch progress for a specific movie.

        This endpoint stores the current playback time for a movie, so that the user can resume 
        watching later from the same position.

        Args:
            request (Request): Authenticated POST request with JSON body:
                - time (int or float): The current playback position in seconds.
            pk (int): Primary key (ID) of the movie.

        Returns:
            Response:
                - 201 Created:
                    If the progress was successfully created or updated.
                - 400 Bad Request:
                    If the 'time' field is missing or invalid.

        Authentication:
            Required - Token-based authentication

        Permissions:
            Only authenticated users (IsAuthenticated)
        """
        req_time = request.data.get('time')

        if req_time is None:
            return Response({'error': 'Time is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            movie = Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

        progress, created = MovieProgress.objects.get_or_create(movie=movie, user=request.user)
        progress.time = req_time
        progress.save()

        return Response(status=status.HTTP_201_CREATED)
        
       
            