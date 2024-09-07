import json
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from ckeditor_uploader.fields import RichTextUploadingField


class News(models.Model):
    news = 'NEW'
    tanks = 'TNK'
    heals = 'HEA'
    damageDealer = 'DAM'
    dealer = 'DEA'
    guildMAster = 'GUM'
    questGiver = 'QUG'
    blacksmiths = 'BLA'
    tanners = 'TAN'
    potionMaster = 'POT'
    spellMaster = 'SPM'

    TYPENEWS = [
        (news, 'Новость'),
        (tanks, 'Танки'),
        (heals, 'Хилы'),
        (damageDealer, 'ДД'),
        (dealer, 'Торговцы'),
        (guildMAster, 'Гильдмастеры'),
        (questGiver, 'Квестгиверы'),
        (blacksmiths, 'Кузнецы'),
        (tanners, 'Кожевники'),
        (potionMaster, 'Зельевары'),
        (spellMaster, 'Мастера заклинаний'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=3, choices=TYPENEWS, default=news)
    content = RichTextUploadingField(verbose_name='Контент')
    publicationDate = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Имя Автора')

    def __str__(self):
        return self.title

    def toJSON(self):
        def obj_handler(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            else:
                return obj.__dict__

        return json.dumps(
            self,
            default=lambda o: obj_handler(o),
            sort_keys=True,
            indent=4)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'news-{self.pk}')


class Response(models.Model):
    noWrite = 'NW'
    writeYes = 'WY'
    writeNo = 'WN'

    TYPERES = [
        (noWrite, 'Не прочтено'),
        (writeYes, 'Подтверждаю'),
        (writeNo, 'Отказываю')
    ]

    is_approved = models.BooleanField(default=False)
    responseNews = models.ForeignKey(News, related_name='news_comments', on_delete=models.CASCADE, db_column='responseNews_id')
    responseDate = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    responseType = models.CharField(max_length=2, choices=TYPERES, default=noWrite, verbose_name='Статус')
    responseAuthor = models.ForeignKey(User, on_delete=models.CASCADE, db_column='responseAuthor_id')
    responseMessage = RichTextUploadingField(verbose_name='Текст комментария')

    def __str__(self):
        return f"Comment by {self.responseAuthor} on {self.responseNews}"

    def get_category_display(self):
        return dict(self.TYPENEWS).get(self.category, self.category)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'response-{self.pk}')

    def toJSON(self):
        def obj_handler(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            else:
                return obj.__dict__

        return json.dumps(
            self,
            default=lambda o: obj_handler(o),
            sort_keys=True,
            indent=4)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Пользователь')
    category = models.CharField(max_length=3, choices=News.TYPENEWS, verbose_name='Категория')

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {dict(News.TYPENEWS).get(self.category)}'