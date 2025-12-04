import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    """ 
    Form enabling registered users to add recipes. 
    """

    publication_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        help_text="Select publication date (today or earlier)"
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
        help_text="Upload an image of the dish (optional).",
    )

    servings = forms.IntegerField(
        min_value=1,
        initial=4,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "1",
                "required": "required",
            }
        ),
        help_text="How many servings does this recipe make?",
        error_messages={
            "required": "Please enter the number of servings for this recipe.",
            "invalid": "Please enter a valid number.",
            "min_value": "Servings must be at least 1.",
        }
    )

    ingredients = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": (
                    "Enter each ingredient on a new line, e.g.:\n"
                    "Garlic (5 cloves)\n"
                    "Soy sauce (4 tablespoons)\n"
                    "Chicken breast (500g)"
                ),
            }
        ),
        help_text="List each ingredient on a new line with quantities in parentheses",
    )

    steps = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": (
                    "Enter each step on a new line, e.g.:\n"
                    "Heat oil in a large pan\n"
                    "Add garlic and cook for 1 minute\n"
                    "Add chicken and cook until golden"
                ),
            }
        ),
        help_text="List each step on a new line",
    )

    private = forms.ChoiceField(
        choices=[(True, "private"), (False, "public")],
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=False,
        required=True,
        label="Recipe Visibility",
    )

    prep_time_hours = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    )
    
    prep_time_minutes = forms.IntegerField(
        min_value=0,
        max_value=59,
        initial=0,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "max": "59"}
        ),
    )
    
    cook_time_hours = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    )
    
    cook_time_minutes = forms.IntegerField(
        min_value=0,
        max_value=59,
        initial=0,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "max": "59"}
        ),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set max date dynamically to today
        self.fields['publication_date'].widget.attrs['max'] = timezone.now().date().isoformat()
    
    class Meta:
        model = Recipe
        fields = [
            "title",
            "publication_date",
            "servings",
            "ingredients",
            "steps",
            "image",
            "prep_time_hours",
            "prep_time_minutes",
            "cook_time_hours",
            "cook_time_minutes",
            "private",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }
        
    def clean_publication_date(self):
        """ Validate that publication date is not in the future. """
        date = self.cleaned_data.get('publication_date')
        if date and date > timezone.now().date():
            raise ValidationError("Publication date cannot be in the future.")
        return date

    def clean_ingredients(self):
        """ Validate ingredient format: Ingredient (quantity). """
        ingredients = self.cleaned_data.get("ingredients")
        if not ingredients:
            raise ValidationError("Ingredients are required.")

        errors = self._find_ingredient_errors(ingredients)
        if errors:
            raise ValidationError(self._format_ingredient_errors(errors))
        
        return ingredients
    
    def _find_ingredient_errors(self, text):
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        errors = []

        for i, line in enumerate(lines, start=1):
            if '(' not in line or ')' not in line:
                errors.append(f"Line {i}: missing parentheses")
            elif not line.endswith(')'):
                errors.append(f"Line {i}: parentheses should be at the end")
            elif line.count('(') != line.count(')'):
                errors.append(f"Line {i}: mismatched parentheses")

        return errors

    def _format_ingredient_errors(self, errors):
        """ Format ingredient errors for display. """
        return (
            "Please fix the following ingredient formatting errors:\n"
            + "\n".join(errors)
            + "\n\nCorrect format: Ingredient name (quantity)\n"
            "Example: Avocado (1)"
        )