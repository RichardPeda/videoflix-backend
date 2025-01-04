from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page, cache_control
from django.utils.decorators import method_decorator
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from movie.models import Movie
from movie.api.serializers import MovieSerializer


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class MovieView(APIView):
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
        
        # self.check_object_permissions(request, offer_detail)
        serializer = MovieSerializer(movies, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)