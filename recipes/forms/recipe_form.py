from django import forms
from django.utils import timezone
from recipes.models import Recipe

class RecipeForm(forms.ModelForm):
    """
    Form enabling registered users to add recipes.

    Fields:
        author, title, adjectives, publication_date, image
    """

    publication_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat(),
            }
        ),
        help_text='Select the publication date (today or earlier)'
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }
        ),
        help_text='Upload an image of the dish (optional).'
    )

    servings = forms.IntegerField(
        min_value=1,
        initial=4,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
            }
        ),
        help_text='How many servings does this recipe make?'
    )

    ingredients = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter each ingredient on a new line, e.g.:\nGarlic (5 cloves)\nSoy sauce (4 tablespoons)\nChicken breast (500g)'
            }
        ),
        help_text='List each ingredient on a new line with quantities in parentheses'
    )

    steps = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter each step on a new line, e.g.:\nHeat oil in a large pan\nAdd garlic and cook for 1 minute\nAdd chicken and cook until golden'
            }
        ),
        help_text='List each step on a new line'
    )


    class Meta:
        model = Recipe
        fields = ['author', 'title', 'adjectives', 'publication_date', 'servings', 'ingredients', 'steps', 'image']
        widgets = {
            'author': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'adjectives': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_publication_date(self):
        publication_date = self.cleaned_data.get('publication_date')
        if publication_date and publication_date > timezone.now().date():
            raise forms.ValidationError("Publication date cannot be in the future.")
        return publication_date

