from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Review, Tour

from .models import (
    BlogPost, Destination, Favorite, ForumActivity, ForumReply, ForumTopic,
    ItineraryDay, NewsletterSubscriber, Order, OrderItem, Review, Tour,
    TourImage, UserProfile,
)


class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ["id", "tour", "image_url", "sort_order"]


class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        fields = ["id", "day_number", "title", "description"]


class ReviewSerializer(serializers.ModelSerializer):
    # tour_title только для чтения (выводит название на фронтенд)
    tour_title = serializers.ReadOnlyField(source='tour.title')

    # tour для записи (принимает UUID тура от фронтенда)
    tour = serializers.PrimaryKeyRelatedField(queryset=Tour.objects.all())

    class Meta:
        model = Review
        fields = [
            "id",
            "tour",  # ОБЯЗАТЕЛЬНО ДОЛЖНО БЫТЬ ТУТ
            "tour_title",
            "name",
            "avatar",
            "rating",
            "text",
            "date",
            "created_at"
        ]


class TourListSerializer(serializers.ModelSerializer):
    """Краткая версия тура для списков."""
    class Meta:
        model = Tour
        fields = [
            "id", "title", "price", "discount", "image", "location", "country",
            "duration", "rating", "reviews_count", "is_hot", "category",
            "max_people"
        ]


class TourDetailSerializer(serializers.ModelSerializer):
    """Полная версия тура с вложенными данными."""
    images = TourImageSerializer(many=True, read_only=True)
    itinerary_days = ItineraryDaySerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Tour
        fields = [
            "id", "title", "description", "price", "discount", "duration", "rating",
            "reviews_count", "image", "location", "country", "category", "tags",
            "hotel", "hotel_stars", "included", "not_included", "is_hot",
            "meals", "transport", "guide_language", "group_size", "difficulty",
            "best_season", "visa_required", "insurance_included", "free_cancellation",
            "instant_confirmation", "amenities", "highlights", "faqs", "gallery",
            "departure_cities", "arrival_info", "important_notes", "suitable_for",
            "languages", "max_people", "created_at", "images", "itinerary_days", "reviews"
        ]


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "country", "image", "tour_count"]


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "excerpt", "content", "author", "author_avatar", "date",
            "image", "category", "read_time", "likes", "created_at"
        ]


class ForumReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumReply
        fields = ["id", "topic", "author", "author_avatar", "content", "date", "likes", "created_at"]


class ForumTopicSerializer(serializers.ModelSerializer):
    replies = ForumReplySerializer(many=True, read_only=True)

    class Meta:
        model = ForumTopic
        fields = [
            "id", "title", "author", "author_avatar", "date", "replies_count", "views",
            "category", "is_pinned", "last_reply", "created_at", "replies"
        ]


class ForumTopicListSerializer(serializers.ModelSerializer):
    """Краткая версия темы для списков."""
    class Meta:
        model = ForumTopic
        fields = [
            "id", "title", "author", "author_avatar", "date", "replies_count",
            "views", "category", "is_pinned", "created_at"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    tour = TourListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "order", "tour", "quantity", "travel_date", "people_count", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # Позволим принимать список id туров и данных при создании
    cart_items = serializers.JSONField(write_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user_id", "email", "name", "phone", "total_amount", "status",
            "payment_method", "created_at", "items", "cart_items"
        ]

    def create(self, validated_data):
        cart_items_data = validated_data.pop('cart_items')
        order = Order.objects.create(**validated_data)

        for item in cart_items_data:
            tour = Tour.objects.get(id=item['tourId'])
            OrderItem.objects.create(
                order=order,
                tour=tour,
                quantity=1,
                people_count=item['people'],
                travel_date=item['travelDate'],
                unit_price=item['price']  # или считай цену со скидкой на бэке
            )
        return order


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserProfileDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "user", "avatar", "bio", "total_spent", "orders_count", "created_at"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
        }


class FavoriteSerializer(serializers.ModelSerializer):
    tour = TourListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "user", "tour", "created_at"]


class ForumActivitySerializer(serializers.ModelSerializer):
    topic = ForumTopicListSerializer(read_only=True)
    reply = ForumReplySerializer(read_only=True)

    class Meta:
        model = ForumActivity
        fields = ["id", "user", "topic", "reply", "activity_type", "content_preview", "created_at"]


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
