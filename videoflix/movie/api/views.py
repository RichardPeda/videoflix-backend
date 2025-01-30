from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page, cache_control
from django.utils.decorators import method_decorator
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from movie.models import Movie, MovieConvertables
from movie.api.serializers import MovieSerializer, MovieConvertablesSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny



CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class MovieView(APIView):
      # authentication_classes = [TokenAuthentication]
      # permission_classes = [IsAuthenticated]
      permission_classes = [AllowAny]

      # @method_decorator(cache_page(CACHE_TTL))
      def get(self, request):
        
        """
        This endpoint returns a all movies.
        
        Args:
            request (user): Authenticated user.

        Returns:
            JSON: Serialized offer.
        """
        
        movies = Movie.objects.all()
        movies = movies.order_by('created_at')
        serializer = MovieSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
      
class MovieConvertablesView(APIView):
    def get(self, request):
        convertables = MovieConvertables.objects.all()
        serializer = MovieConvertablesSerializer(convertables, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
