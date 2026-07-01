import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class TimeStampedModel(models.Model):
    """Базовая модель: UUID-ключ + дата создания (как в исходной схеме Supabase)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        abstract = True


class Destination(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Название")
    country = models.CharField(max_length=255, verbose_name="Страна")
    image = models.URLField(max_length=1000, verbose_name="Изображение")
    tour_count = models.IntegerField(default=0, verbose_name="Кол-во туров")

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country}"


class Tour(TimeStampedModel):
    DIFFICULTY_CHOICES = [
        ("Легкий", "Легкий"),
        ("Средний", "Средний"),
        ("Сложный", "Сложный"),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration = models.IntegerField(verbose_name="Длительность (дней)")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, verbose_name="Рейтинг")
    reviews_count = models.IntegerField(default=0, verbose_name="Кол-во отзывов")
    image = models.URLField(max_length=1000, verbose_name="Главное изображение")
    location = models.CharField(max_length=255, verbose_name="Локация")
    country = models.CharField(max_length=255, verbose_name="Страна")
    category = models.CharField(max_length=255, verbose_name="Категория")
    tags = ArrayField(models.CharField(max_length=100), default=list, blank=True, verbose_name="Теги")
    hotel = models.CharField(max_length=255, blank=True, null=True, verbose_name="Отель")
    hotel_stars = models.IntegerField(blank=True, null=True, verbose_name="Звёзды отеля")
    included = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Включено")
    not_included = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Не включено")
    is_hot = models.BooleanField(default=False, verbose_name="Горящий тур")
    discount = models.IntegerField(default=0, verbose_name="Скидка %")
    max_people = models.IntegerField(default=30, verbose_name="Макс. человек")

    # Расширенные поля (из второй миграции)
    meals = models.TextField(blank=True, null=True, verbose_name="Питание")
    transport = models.TextField(blank=True, null=True, verbose_name="Транспорт")
    guide_language = models.CharField(max_length=255, blank=True, null=True, verbose_name="Язык гида")
    group_size = models.CharField(max_length=255, blank=True, null=True, verbose_name="Размер группы")
    difficulty = models.CharField(max_length=50, blank=True, null=True, choices=DIFFICULTY_CHOICES, verbose_name="Сложность")
    best_season = models.CharField(max_length=255, blank=True, null=True, verbose_name="Лучший сезон")
    visa_required = models.BooleanField(default=False, verbose_name="Нужна виза")
    insurance_included = models.BooleanField(default=False, verbose_name="Страховка включена")
    free_cancellation = models.BooleanField(default=True, verbose_name="Бесплатная отмена")
    instant_confirmation = models.BooleanField(default=True, verbose_name="Мгновенное подтверждение")
    amenities = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Удобства")
    highlights = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Изюминки")
    faqs = models.JSONField(default=list, blank=True, verbose_name="Вопросы и ответы")
    gallery = ArrayField(models.URLField(max_length=1000), default=list, blank=True, verbose_name="Галерея")
    departure_cities = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Города вылета")
    arrival_info = models.TextField(blank=True, null=True, verbose_name="Информация о прибытии")
    important_notes = models.TextField(blank=True, null=True, verbose_name="Важные заметки")
    suitable_for = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Подходит для")
    languages = ArrayField(models.CharField(max_length=255), default=list, blank=True, verbose_name="Языки")

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TourImage(TimeStampedModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="images", verbose_name="Тур")
    image_url = models.URLField(max_length=1000, verbose_name="URL изображения")
    sort_order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Изображение тура"
        verbose_name_plural = "Изображения туров"
        ordering = ["sort_order"]

    def __str__(self):
        return f"Изображение {self.tour.title}"


class ItineraryDay(TimeStampedModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="itinerary_days", verbose_name="Тур")
    day_number = models.IntegerField(verbose_name="День")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "День маршрута"
        verbose_name_plural = "Маршрут по дням"
        ordering = ["day_number"]

    def __str__(self):
        return f"День {self.day_number}: {self.title}"


class Review(TimeStampedModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="reviews", verbose_name="Тур")
    name = models.CharField(max_length=255, verbose_name="Имя")
    avatar = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Аватар")
    rating = models.IntegerField(verbose_name="Оценка (1-5)")
    text = models.TextField(verbose_name="Текст")
    date = models.CharField(max_length=100, verbose_name="Дата (текст)")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.rating}★"


class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    excerpt = models.TextField(verbose_name="Краткое описание")
    content = models.TextField(verbose_name="Содержание")
    author = models.CharField(max_length=255, verbose_name="Автор")
    author_avatar = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Аватар автора")
    date = models.CharField(max_length=100, verbose_name="Дата (текст)")
    image = models.URLField(max_length=1000, verbose_name="Изображение")
    category = models.CharField(max_length=255, verbose_name="Категория")
    read_time = models.IntegerField(default=5, verbose_name="Время чтения (мин)")
    likes = models.IntegerField(default=0, verbose_name="Лайки")

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ForumTopic(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    author = models.CharField(max_length=255, verbose_name="Автор")
    author_avatar = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Аватар автора")
    date = models.CharField(max_length=100, verbose_name="Дата (текст)")
    replies_count = models.IntegerField(default=0, verbose_name="Кол-во ответов")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    category = models.CharField(max_length=255, verbose_name="Категория")
    is_pinned = models.BooleanField(default=False, verbose_name="Закреплено")
    last_reply = models.CharField(max_length=255, blank=True, null=True, verbose_name="Последний ответ (текст)")

    class Meta:
        verbose_name = "Тема обсуждения"
        verbose_name_plural = "Темы обсуждений"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title


class ForumReply(TimeStampedModel):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name="replies", verbose_name="Тема")
    author = models.CharField(max_length=255, verbose_name="Автор")
    author_avatar = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Аватар автора")
    content = models.TextField(verbose_name="Сообщение")
    date = models.CharField(max_length=100, verbose_name="Дата (текст)")
    likes = models.IntegerField(default=0, verbose_name="Лайки")

    class Meta:
        verbose_name = "Ответ в обсуждении"
        verbose_name_plural = "Ответы в обсуждениях"
        ordering = ["created_at"]

    def __str__(self):
        return f"Ответ от {self.author}"


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True, verbose_name="Email")

    class Meta:
        verbose_name = "Подписчик рассылки"
        verbose_name_plural = "Подписчики рассылки"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "В обработке"),
        ("paid", "Оплачен"),
        ("completed", "Завершён"),
        ("cancelled", "Отменён"),
    ]

    user_id = models.UUIDField(blank=True, null=True, verbose_name="ID пользователя")
    email = models.EmailField(verbose_name="Email")
    name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, default="pending", choices=STATUS_CHOICES, verbose_name="Статус")
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name="Способ оплаты")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ {self.id} — {self.name} (${self.total_amount})"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="order_items", verbose_name="Тур")
    quantity = models.IntegerField(default=1, verbose_name="Количество")
    travel_date = models.DateField(blank=True, null=True, verbose_name="Дата поездки")
    people_count = models.IntegerField(default=1, verbose_name="Кол-во человек")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.tour.title} × {self.people_count}"


class UserProfile(TimeStampedModel):
    """Расширенный профиль пользователя с избранными турами и статистикой."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователь")
    avatar = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Аватар")
    bio = models.TextField(blank=True, null=True, verbose_name="Биография")
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Всего потрачено")
    orders_count = models.IntegerField(default=0, verbose_name="Кол-во заказов")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.get_full_name() or self.user.username}"


class Favorite(TimeStampedModel):
    """Избранные туры пользователя (M2M)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites", verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="favorited_by", verbose_name="Тур")

    class Meta:
        verbose_name = "Избранный тур"
        verbose_name_plural = "Избранные туры"
        unique_together = ("user", "tour")

    def __str__(self):
        return f"{self.user.username} → {self.tour.title}"


class ForumActivity(TimeStampedModel):
    """История активности пользователя в форуме."""

    ACTIVITY_TYPES = [
        ("reply", "Ответ"),
        ("like", "Лайк"),
        ("mention", "Упоминание"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_activities", verbose_name="Пользователь")
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name="activities", verbose_name="Тема", blank=True, null=True)
    reply = models.ForeignKey(ForumReply, on_delete=models.CASCADE, related_name="activities", verbose_name="Ответ", blank=True, null=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name="Тип активности")
    content_preview = models.TextField(blank=True, null=True, verbose_name="Превью содержимого")

    class Meta:
        verbose_name = "Активность в форуме"
        verbose_name_plural = "Активность в форумах"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.get_activity_type_display()}"