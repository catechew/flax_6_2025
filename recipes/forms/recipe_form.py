from django import forms
from django.utils import timezone
from django.forms import inlineformset_factory

from recipes.models import Recipe, RecipeIngredient, RecipeStep, Store, IngredientPrice

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

    class Meta:
        model = Recipe
        fields = ['author', 'title', 'adjectives', 'publication_date', 'image']
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


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['name', 'quantity', 'store', 'custom_store', 'price', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Flour'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2 cups'
            }),
            'store': forms.Select(attrs={
                'class': 'form-control'
            }),
            'custom_store': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter store name (only if Other selected)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'order': forms.HiddenInput(),
        }


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['step_number', 'instruction']
        widgets = {
            'step_number': forms.HiddenInput(),
            'instruction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe this step...'
            }),
        }


# Formsets - make all fields optional so empty rows don't cause validation errors
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=10,
    can_delete=False,
    # Don't validate empty forms
    validate_min=False,
    min_num=0,
)

RecipeStepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    form=RecipeStepForm,
    extra=10,
    can_delete=False,
    # Don't validate empty forms
    validate_min=False,
    min_num=0,
)
