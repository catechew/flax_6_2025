from django.core.validators import MinLengthValidator, RegexValidator
from django.http import HttpResponse

from django.db import models

"""A Recipe can be posted by a user and later we will be able to do all CRUD operations on it.
    It has 4 fields as shown below"""

class Recipe(models.Model):
    user = models.CharField(
		max_length=255,
		validators=[MinLengthValidator(4)]
	)
    title = models.CharField(
		max_length=255,
		validators=[MinLengthValidator(4)]
	)
    adjectives = models.CharField(
		max_length=255,
		validators=[MinLengthValidator(4)]
	)
    publication_date = models.DateField()

    def __str__(self):
        return(f"{self.user}  ({self.publication_date.year})  \"{self.title}\"  Adjectives: {self.adjectives}.")