from django.db import models


class Book(models.Model):

    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=50, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]
