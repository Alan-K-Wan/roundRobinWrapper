from django.db import models

class Player(models.Model):
    class Rank(models.IntegerChoices):
        GREEN = 40
        GREEN_BLUE = 50
        BLUE = 60
        BLUE_BLACK = 70
        BLACK = 80
        BLACK_RED = 90
        RED = 100
    FEMALE = "F"
    MALE = "M"
    GENDER_CHOICES = {
        MALE: "Male",
        FEMALE: "Female",
    }
    peg_name = models.CharField(max_length=20)
    peg_colour = models.IntegerField(choices=Rank)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
    )
    def __str__(self):
        return self.peg_name