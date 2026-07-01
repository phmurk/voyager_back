from django.contrib import admin

from .models import (
    BlogPost,
    Destination,
    Favorite,
    ForumActivity,
    ForumReply,
    ForumTopic,
    ItineraryDay,
    NewsletterSubscriber,
    Order,
    OrderItem,
    Review,
    Tour,
    TourImage,
    UserProfile,
)


# ---------- Inlines ----------

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1


class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


class ForumReplyInline(admin.TabularInline):
    model = ForumReply
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ["tour"]


# ---------- ModelAdmins ----------

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "tour_count", "created_at"]
    search_fields = ["name", "country"]
    list_filter = ["country"]


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ["title", "location", "country", "price", "discount", "rating", "is_hot", "created_at"]
    list_filter = ["country", "category", "is_hot", "difficulty", "visa_required"]
    search_fields = ["title", "location", "country", "description"]
    list_editable = ["price", "discount", "is_hot"]
    inlines = [TourImageInline, ItineraryDayInline, ReviewInline]
    fieldsets = (
        ("Основное", {
            "fields": ("title", "description", "image", "location", "country", "category", "tags")
        }),
        ("Цена и параметры", {
            "fields": ("price", "discount", "duration", "max_people", "rating", "reviews_count", "is_hot")
        }),
        ("Отель и состав", {
            "fields": ("hotel", "hotel_stars", "included", "not_included")
        }),
        ("Детали", {
            "classes": ("collapse",),
            "fields": (
                "meals", "transport", "guide_language", "group_size", "difficulty", "best_season",
                "visa_required", "insurance_included", "free_cancellation", "instant_confirmation",
                "amenities", "highlights", "faqs", "gallery", "departure_cities",
                "arrival_info", "important_notes", "suitable_for", "languages",
            ),
        }),
    )


@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin):
    list_display = ["tour", "image_url", "sort_order"]
    search_fields = ["tour__title"]


@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ["tour", "day_number", "title"]
    list_filter = ["tour"]
    search_fields = ["tour__title", "title"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["name", "tour", "rating", "date", "created_at"]
    list_filter = ["rating"]
    search_fields = ["name", "tour__title", "text"]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "read_time", "likes", "created_at"]
    list_filter = ["category", "author"]
    search_fields = ["title", "excerpt", "content", "author"]
    list_editable = ["likes"]


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "replies_count", "views", "is_pinned", "created_at"]
    list_filter = ["category", "is_pinned"]
    search_fields = ["title", "author"]
    list_editable = ["is_pinned"]
    inlines = [ForumReplyInline]


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ["topic", "author", "likes", "created_at"]
    search_fields = ["topic__title", "author", "content"]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "created_at"]
    search_fields = ["email"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "total_amount", "status", "payment_method", "created_at"]
    list_filter = ["status", "payment_method"]
    search_fields = ["name", "email", "phone"]
    list_editable = ["status"]
    inlines = [OrderItemInline]
    readonly_fields = ["created_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "tour", "people_count", "unit_price", "travel_date"]
    search_fields = ["order__name", "tour__title"]
    autocomplete_fields = ["tour", "order"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_email", "orders_count", "total_spent", "created_at")
    list_filter = ("created_at", "orders_count")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at",)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Имя пользователя"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_tour", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "tour__title")
    readonly_fields = ("created_at",)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Пользователь"

    def get_tour(self, obj):
        return obj.tour.title
    get_tour.short_description = "Тур"


@admin.register(ForumActivity)
class ForumActivityAdmin(admin.ModelAdmin):
    list_display = ("get_username", "activity_type", "get_topic", "created_at")
    list_filter = ("activity_type", "created_at")
    search_fields = ("user__username", "topic__title", "reply__content")
    readonly_fields = ("created_at",)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Пользователь"

    def get_topic(self, obj):
        return obj.topic.title if obj.topic else "—"
    get_topic.short_description = "Тема"