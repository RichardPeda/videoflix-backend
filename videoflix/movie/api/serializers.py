from rest_framework import serializers
from movie.models import ConnectionTestFile, Movie, MovieConvertables, MovieProgress

class MovieSerializer(serializers.ModelSerializer):
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

class MovieProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieProgress
        fields = '__all__'