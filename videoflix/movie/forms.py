from django import forms
from .models import Movie

class MovieAdminForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
        widgets = {
            'ranking': forms.NumberInput(attrs={
                'min': 0,
                'max': 5,
                'step': 0.5, 
            })
        }
    
    def clean_ranking(self):
        value = self.cleaned_data['ranking']
        if value < 0 or value > 5:
            raise forms.ValidationError("Die Bewertung muss zwischen 0 und 5 liegen.")
        return value
