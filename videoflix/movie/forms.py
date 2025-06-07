from django import forms
from .models import Movie

class MovieAdminForm(forms.ModelForm):
    """
    Custom form for the Movie model used in the Django admin interface.

    This form extends the default ModelForm and is intended for use in MovieAdmin
    to customize form behavior and validation logic for the Movie model.

    Key features:
    - Uses all fields from the Movie model (`fields = '__all__'`).
    - Applies a custom widget to the 'ranking' field, rendering it as an HTML number input
    with specific constraints (min: 0, max: 5, step: 0.5).
    - Implements custom validation logic for the 'ranking' field to ensure values
    stay within the allowed range (0 to 5).

    Meta configuration:
    - model: Specifies the Movie model as the base for this form.
    - fields: Includes all model fields in the form.
    - widgets: Overrides the default widget for the 'ranking' field with a number input.

    Methods:
    - clean_ranking(): Validates that the entered ranking is between 0 and 5.
    Raises a ValidationError if the value is outside the allowed range.
    """
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
