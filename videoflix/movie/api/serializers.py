from rest_framework import serializers
from movie.models import ConnectionTestFile, Movie, MovieConvertables

class MovieSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(method_name='get_image_url')   
    
    class Meta:
        model = Movie
        exclude = ['video_url']
                
    def get_image_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image_url.url)
        return obj.image_url.url
        
class MovieDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class MovieConvertablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieConvertables
        fields = '__all__'

class TestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionTestFile
        fields = '__all__'