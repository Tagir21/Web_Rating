from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя игрока")
    rating = models.IntegerField(verbose_name="Рейтинг")

    def __str__(self):
        return f"{self.name} - {self.rating}"

    class Meta:

        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"



