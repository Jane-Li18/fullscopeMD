from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = [
            'first_name',
            'last_name',
            'email',
            'product',
            'testimonial',
            'image',
            'star_rating',
        ]
