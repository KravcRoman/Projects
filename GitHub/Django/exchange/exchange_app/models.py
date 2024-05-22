from django.db import models


class Exchange_Rate(models.Model):
    charcode = models.CharField(max_length=3)
    date = models.DateField()
    rate = models.FloatField()

    class Meta:
        unique_together = ('charcode', 'date')

    def __str__(self):
        return f"{self.charcode} {self.date} {self.rate}"

