from django import forms

from recipes.models import Recipe

class RecipeForm(forms.ModelForm):
	"""
    Form enabling registered users to add recipes.

    Fields:
        author, title, adjectives, publication_date
    """
	class Meta:
		model = Recipe
		fields = ['author', 'title', 'adjectives', 'publication_date']
		widgets = {
              'publication_date': forms.DateInput(attrs={
                  'type': 'date',
                  'class': 'form-control'
              })
          }