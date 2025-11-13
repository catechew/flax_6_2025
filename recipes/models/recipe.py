from django.core.validators import MinLengthValidator, RegexValidator

from django.db import models

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