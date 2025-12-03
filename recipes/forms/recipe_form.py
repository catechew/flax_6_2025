import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from recipes.models import Recipe

class RecipeForm(forms.ModelForm):
    """
    Form enabling registered users to add recipes.

    Fields:
        author, title, publication_date, 
        image, servings, prep time, 
        ingredients, steps,
        private/public,
        cook_time, tags (cuisine, course, dietary, others)
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
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'required': 'required',
            }
        ),
        help_text='How many servings does this recipe make?',
        error_messages={
            'required' : 'Please enter the number of servings for this recipe.',
            'invalid' : 'Please enter a valid number',
            'min_value' : 'Servings must be at least 1.',
        }
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

    visibility_choices = [(True, 'private'), (False, 'public')]

    private = forms.ChoiceField(
        choices = visibility_choices,
        initial = False,
        required = True, 
        widget = forms.Select(attrs={'class': 'form-control'}),
        label= 'Recipe Visibility'
    )

    prep_time_hours = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min':'0'}),
        label='Prep Time (hours)'
    )
    prep_time_minutes = forms.IntegerField(
        min_value=0,
        max_value=59,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '59'}),
        label='Prep Time (minutes)'
    )
    cook_time_hours = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min':'0'}),
        label='Cook Time (hours)'
    )
    cook_time_minutes = forms.IntegerField(
        min_value=0,
        max_value=59,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '59'}),
        label='Cook Time (minutes)'
    )
    
    class Meta:
        model = Recipe
        fields = ['title', 'publication_date', 'servings', 'ingredients', 'steps', 'image', 'prep_time_hours', 'prep_time_minutes','cook_time_hours', 'cook_time_minutes', 'private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_publication_date(self):
        publication_date = self.cleaned_data.get('publication_date')
        if publication_date and publication_date > timezone.now().date():
            raise forms.ValidationError("Publication date cannot be in the future.")
        return publication_date

    def clean_ingredients(self):
        """Validate that each ingredient follows the format: Name (quantity)"""
        ingredients = self.cleaned_data.get('ingredients')
        if not ingredients:
            return ingredients

        lines = [line.strip() for line in ingredients.split('\n') if line.strip()]
        errors = []

        # Pattern: ingredient name followed by quantity in parentheses
        # Must have exactly one set of parentheses at the end
        # pattern = r'^[^()]+\([^()]+\)$'
        pattern = r'^[^(]+\(.+\)$'

        for i, line in enumerate(lines, 1):
            # Check if line matches the pattern
            if not re.match(pattern, line):
                # Check for common errors to give helpful messages
                if '(' not in line and ')' not in line:
                    errors.append(f"Line {i}: '{line}' - Missing quantity in parentheses")
                elif line.count('(') > 1 or line.count(')') > 1:
                    errors.append(f"Line {i}: '{line}' - Should have exactly one set of parentheses")
                elif not line.endswith(')'):
                    errors.append(f"Line {i}: '{line}' - Parentheses should be at the end")
                elif '(' not in line or ')' not in line:
                    errors.append(f"Line {i}: '{line}' - Invalid format")
                else:
                    errors.append(f"Line {i}: '{line}' - Should be: Ingredient name (quantity)")

        if errors:
            error_msg = "Please fix the following ingredient formatting errors:\n" + "\n".join(errors)
            error_msg += "\n\nCorrect format: Ingredient name (quantity)\nExample: Avocado (1)"
            raise ValidationError(error_msg)

        return ingredients
