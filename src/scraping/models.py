from django.db import models
from .utils import *
import jsonfield
__all__ = [
    'City',
    'Language',
    'Vacancy',
    'Error',
    'Url',
]


def default_urls():
    return {
        'work': '',
        'djinni': '',
    }


class BaseModel(models.Model):
    """
    Base class model
    """
    objects = models.Manager()

    class Meta:
        abstract = True


class City(BaseModel):
    """
    Model with city's
    """
    name = models.CharField(
        max_length=50,
        verbose_name='Название населенного пункта',
        unique=True,
    )
    slug = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
    )
    
    class Meta:
        verbose_name = 'Название населенного пункта'
        verbose_name_plural = 'Название населенных пунктов'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliteration(str(self.name))
        super().save(*args, **kwargs)


class Language(BaseModel):
    name = models.CharField(
        max_length=50,
        verbose_name='Язык программирования',
        unique=True,
    )
    slug = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'Язык программирования'
        verbose_name_plural = 'Языки программирования'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliteration(str(self.name))
        super().save(*args, **kwargs)


class Vacancy(BaseModel):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=250, verbose_name='Заголовок вакансии')
    company = models.CharField(max_length=250, verbose_name='Компания')
    description = models.TextField(verbose_name='Описание вакансии')
    city = models.ForeignKey('city', on_delete=models.CASCADE, verbose_name='Город')
    language = models.ForeignKey('language', on_delete=models.CASCADE, verbose_name='Язык программирования')
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-timestamp']

    def __str__(self):
        return self.title


class Error(BaseModel):
    timestamp = models.DateField(auto_now_add=True)
    data = jsonfield.JSONField()

    def __str__(self):
        return str(self.timestamp)


class Url(BaseModel):
    city = models.ForeignKey('city', on_delete=models.CASCADE, verbose_name='Город')
    language = models.ForeignKey('language', on_delete=models.CASCADE, verbose_name='Язык программирования')
    url_data = jsonfield.JSONField(default=default_urls)

    class Meta:
        unique_together = ('city', 'language')
