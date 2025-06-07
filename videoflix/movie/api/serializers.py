from rest_framework import serializers
from movie.models import ConnectionTestFile, Movie, MovieConvertables, MovieProgress

class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for Movie model.

    Provides all fields except 'video_file'.

    Adds a read-only 'image_file' field which returns
    the absolute URL of the movie's image file,
    constructed using the current request context if available.
    """
    image_file = serializers.SerializerMethodField(method_name='get_image_file')   
    
    class Meta:
        model = Movie
        exclude = ['video_file']
                
    def get_image_file(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image_file.url)
        return obj.image_file.url
        
class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed representation of the Movie model.

    Includes all fields of the Movie model.
    """
    class Meta:
        model = Movie
        fields = '__all__'

class MovieConvertablesSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed representation of the MovieConvertables model.

    Includes all fields of the MovieConvertables model.
    """
    class Meta:
        model = MovieConvertables
        fields = '__all__'

class TestFileSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed representation of the ConnectionTestFile model.

    Includes all fields of the ConnectionTestFile model.
    """
    class Meta:
        model = ConnectionTestFile
        fields = '__all__'

class MovieProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed representation of the MovieProgress model.

    Includes all fields of the MovieProgress model.
    """
    class Meta:
        model = MovieProgress
        fields = '__all__'