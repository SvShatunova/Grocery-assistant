import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet

from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.paginations import RecipePagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, RecipeSerializer,
                             SetPasswordSerializer, SubscribeSerializer,
                             TagSerializer, UserCreateSerializer,
                             UserReadSerializer)
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter


class CustomUserViewSet(UserViewSet):
    """Вьюсет для просмотра профиля и создания пользователя."""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserReadSerializer

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {'detail': 'Пароль успешно изменен!'},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if user == author:
                return Response({'errors': 'На себя подписаться нельзя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Subscribe.objects.filter(user=user,
                                        author=author).exists():
                return Response({'errors':
                                 'Вы уже подписаны на этого пользователя!'},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(author,
                                             context={'request': request}
                                             )

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscribe.objects.filter(user=user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(
                    {'message': 'Вы больше не подписаны на пользователя'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated, ],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        pag_queryset = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pag_queryset,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта.
       Просмотр, создание, редактирование."""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    serializer_class = RecipeCreateSerializer
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeReadSerializer(recipe,
                                              context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            fav_rec = Favorite.objects.filter(user=request.user, recipe__id=pk)
            if fav_rec.exists():
                fav_rec.delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт уже удален!'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart,
                              user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Качаем список с ингредиентами."""
        user = request.user
        buffer = io.BytesIO()
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount'))
        shopping_list = ([f'{i["ingredient__name"]}'
                          f' ({i["ingredient__measurement_unit"]})'
                          f' - {i["amount"]}'
                          for i in ingredients])
        text = canvas.Canvas(buffer)
        font = ttfonts.TTFont('Times-Roman', './docs/font.ttf')
        pdfmetrics.registerFont(font)
        text.setFont('Times-Roman', 20)
        text.drawString(200, 750, 'Список покупок')
        text.setFont('Times-Roman', 14)
        height = 700
        for line in shopping_list:
            text.drawString(50, height, line)
            height -= 25
        text.showPage()
        text.save()
        buffer.seek(0)
        return FileResponse(buffer,
                            as_attachment=True,
                            filename='shopping_cart.pdf')
