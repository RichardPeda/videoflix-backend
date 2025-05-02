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
      authentication_classes = [TokenAuthentication]
      permission_classes = [IsAuthenticated]

      @method_decorator(cache_page(CACHE_TTL))
      def get(self, request):
        
        """
        This endpoint returns a all movies.
        
        Args:
            request (user): Authenticated user.

        Returns:
            JSON: Serialized offer.
        """
        
        movies = Movie.objects.all()
        movies = movies.order_by('-created_at')
        serializer = MovieSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
      
class MovieConvertablesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        convertables = MovieConvertables.objects.all()
        serializer = MovieConvertablesSerializer(convertables, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SingleMovieConvertablesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            convertables = MovieConvertables.objects.get(pk=pk)
            serializer = MovieConvertablesSerializer(convertables, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class ConnectionTestView(APIView):
    def get(self, request):
        testfile = ConnectionTestFile.objects.get(pk=1)
        serializer = TestFileSerializer(testfile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class MovieProgressView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try: 
            req_user_id = request.user
            progress = MovieProgress.objects.filter(user=req_user_id)
            serializer = MovieProgressSerializer(progress, many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

class MovieProgressSingleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try: 
            req_user_id = request.user
            progress = MovieProgress.objects.get(movie=pk, user=req_user_id)
            serializer = MovieProgressSerializer(progress)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    def post(self,request, pk):
        req_time = request.data.get('time')
        req_user_id = request.user
        movie = Movie.objects.get(pk=pk)
        
        progress, created = MovieProgress.objects.get_or_create(movie=movie, user=req_user_id)
        progress.time = req_time
        progress.save()
        return Response(status=status.HTTP_201_CREATED)
        
       
            