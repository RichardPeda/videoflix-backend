from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from movie.models import Movie
from movie.api.serializers import MovieSerializer






class MovieView(APIView):
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