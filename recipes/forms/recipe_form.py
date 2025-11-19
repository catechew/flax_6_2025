from django import forms
from django.utils import timezone
from django.forms import inlineformset_factory

from recipes.models import Recipe, RecipeIngredient, RecipeStep, Store, IngredientPrice

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

    def clean_publication_date(self):
        publication_date = self.cleaned_data.get('publication_date')
        if publication_date and publication_date > timezone.now().date():
            raise forms.ValidationError("Publication date cannot be in the future.")
        return publication_date
    
class RecipeIngredientForm(forms.ModelForm):
    # Add a field to show suggested price
    suggested_price = forms.DecimalField(
        required=False,
        disabled=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #e9ecef;'
        }),
        label='Suggested Price (£)'
    )
    class Meta:
        model = RecipeIngredient
        fields = ['name', 'quantity', 'store', 'custom_store', 'price', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder' : 'e.g., Flour'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder' : 'e.g., 2 cups'
            }),
            'store': forms.Select(attrs={
                'class': 'form-control store-select'
            }),
            'custom_store': forms.TextInput(attrs={
                'class': 'form-control custom-store-input d-none',
                'placeholder' : 'Enter store name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control ingredient-price',
                'step': '0.01',
                'min': '0',
                'placeholder' : '0.00'
            }),
            'order': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prepopulate suggested price if ingredient and store is known
        if self.instance and self.instance.pk:
            if self.instance.name and self.instance.store:
                try:
                    price_record = IngredientPrice.objects.get(
                        ingredient_name=self.instance.name,
                        store=self.instance.store
                    )
                    self.fields['suggested_price'].initial = price_record.price
                except IngredientPrice.DoesNotExist:
                    pass

class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['step_number', 'instruction']
        widgets = {
            'step_number': forms.HiddenInput(),
            'instruction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder' : 'Describe this step...'
            }),
        }
    
# Formsets for dynamic ingredient and step forms
RecipeIngredientFormSet = inlineformset_factory(
    Recipe, 
    RecipeIngredient, 
    form=RecipeIngredientForm,
    extra=1,
    can_delete=False
)

RecipeStepFormSet = inlineformset_factory(
    Recipe, 
    RecipeStep, 
    form=RecipeStepForm,
    extra=1,
    can_delete=False
)
