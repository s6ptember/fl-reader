import uuid
from django.db import models


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, verbose_name='Название')
    author = models.CharField(max_length=300, verbose_name='Автор')
    cover = models.ImageField(upload_to='covers/', null=True, blank=True, verbose_name='Обложка')
    file = models.FileField(upload_to='books/', verbose_name='Файл книги')
    flibusta_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='ID Флибусты')
    reading_progress = models.IntegerField(default=0, verbose_name='Прогресс чтения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"
