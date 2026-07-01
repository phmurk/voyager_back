from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    BlogPost, Destination, Favorite, ForumActivity, ForumReply, ForumTopic,
    NewsletterSubscriber, Order, Review, Tour, UserProfile,  # <-- Добавлен Review
)
from .serializers import (
    BlogPostSerializer, DestinationSerializer, FavoriteSerializer,
    ForumActivitySerializer, ForumReplySerializer, ForumTopicListSerializer,
    ForumTopicSerializer, NewsletterSubscriberSerializer, OrderSerializer,
    ReviewSerializer,  # <-- Добавлен ReviewSerializer
    TourDetailSerializer, TourListSerializer, UserLoginSerializer,
    UserProfileDetailSerializer, UserRegisterSerializer,
)


class TourViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tour.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TourDetailSerializer
        return TourListSerializer

    @action(detail=False, methods=["get"])
    def hot(self, request):
        """Получить горящие туры."""
        tours = Tour.objects.filter(is_hot=True)[:10]
        serializer = TourListSerializer(tours, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Поиск туров по названию, локации или стране."""
        query = request.query_params.get("q", "")
        if len(query) < 2:
            return Response({"error": "Минимум 2 символа"}, status=status.HTTP_400_BAD_REQUEST)
        tours = Tour.objects.filter(
            title__icontains=query
        ) | Tour.objects.filter(
            location__icontains=query
        ) | Tour.objects.filter(
            country__icontains=query
        )
        serializer = TourListSerializer(tours, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def filter(self, request):
        """Фильтр туров по стране, категории, цене, сложности."""
        queryset = Tour.objects.all()
        country = request.query_params.get("country")
        category = request.query_params.get("category")
        difficulty = request.query_params.get("difficulty")
        price_min = request.query_params.get("price_min")
        price_max = request.query_params.get("price_max")

        if country:
            queryset = queryset.filter(country__icontains=country)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))

        serializer = TourListSerializer(queryset, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """API эндпоинт для отзывов"""
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]  # Создавать может только залогиненный
        return [AllowAny()]  # Читать могут все

class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """Получить статьи по категории."""
        category = request.query_params.get("category")
        if not category:
            return Response({"error": "Укажите category"}, status=status.HTTP_400_BAD_REQUEST)
        posts = BlogPost.objects.filter(category=category)
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)


class ForumTopicViewSet(viewsets.ModelViewSet):
    queryset = ForumTopic.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ForumTopicSerializer
        return ForumTopicListSerializer

    @action(detail=True, methods=["post"])
    def add_reply(self, request, pk=None):
        """Добавить ответ в тему (временно без авторизации)."""
        topic = self.get_object()
        author = request.data.get("author", "Гость")
        content = request.data.get("content", "")

        if not content:
            return Response({"error": "Содержимое не может быть пустым"}, status=status.HTTP_400_BAD_REQUEST)

        reply = ForumReply.objects.create(
            topic=topic,
            author=author,
            content=content,
            date="Только что"
        )
        topic.replies_count += 1
        topic.save()

        # Логирование активности (если пользователь авторизован)
        if request.user.is_authenticated:
            ForumActivity.objects.create(
                user=request.user,
                topic=topic,
                reply=reply,
                activity_type="reply",
                content_preview=content[:100]
            )

        serializer = ForumReplySerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ForumReplyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ForumReply.objects.all()
    serializer_class = ForumReplySerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свои заказы."""
        return Order.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """Создать новый заказ."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "token": token.key,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "token": token.key,
                }, status=status.HTTP_200_OK)
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить профиль пользователя с заказами и избранными турами."""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        profile_serializer = UserProfileDetailSerializer(profile)

        orders = Order.objects.filter(user_id=request.user.id)
        orders_serializer = OrderSerializer(orders, many=True)

        favorites = Favorite.objects.filter(user=request.user)
        favorites_serializer = FavoriteSerializer(favorites, many=True)

        activities = ForumActivity.objects.filter(user=request.user)[:20]
        activities_serializer = ForumActivitySerializer(activities, many=True)

        return Response({
            "profile": profile_serializer.data,
            "orders": orders_serializer.data,
            "favorites": favorites_serializer.data,
            "activities": activities_serializer.data,
        })

    def put(self, request):
        """Обновить профиль пользователя."""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        if "avatar" in request.data:
            profile.avatar = request.data["avatar"]
        if "bio" in request.data:
            profile.bio = request.data["bio"]
        if "first_name" in request.data:
            request.user.first_name = request.data["first_name"]
        if "last_name" in request.data:
            request.user.last_name = request.data["last_name"]

        profile.save()
        request.user.save()

        serializer = UserProfileDetailSerializer(profile)
        return Response(serializer.data)


class FavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить избранные туры пользователя."""
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Добавить/удалить тур в избранное."""
        tour_id = request.data.get("tour_id")
        if not tour_id:
            return Response({"error": "Укажите tour_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tour = Tour.objects.get(id=tour_id)
        except Tour.DoesNotExist:
            return Response({"error": "Тур не найден"}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, tour=tour)
        if not created:
            favorite.delete()
            return Response({"status": "removed"}, status=status.HTTP_200_OK)

        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ForumActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получить историю активности пользователя в форуме."""
        activities = ForumActivity.objects.filter(user=request.user).order_by("-created_at")[:50]
        serializer = ForumActivitySerializer(activities, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class NewsletterSubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Подписаться на рассылку."""
        serializer = NewsletterSubscriberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                NewsletterSubscriber.objects.create(**serializer.validated_data)
                return Response({"status": "subscribed"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

