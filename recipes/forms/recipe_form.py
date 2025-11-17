from django import forms
from django.utils import timezone

from recipes.models import Recipe

class RecipeForm(forms.ModelForm):
    """
    Form enabling registered users to add recipes.

    Fields:
        author, title, adjectives, publication_date
    """

    publication_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat(),  # Block future dates in UI
            }
        ),
        help_text='Select the publication date (today or earlier)'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'title', 'adjectives', 'publication_date']

    def clean_publication_date(self):
        publication_date = self.cleaned_data.get('publication_date')
        if publication_date and publication_date > timezone.now().date():
            raise forms.ValidationError("Publication date cannot be in the future.")
        return publication_date
