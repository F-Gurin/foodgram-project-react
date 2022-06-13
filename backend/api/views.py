from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from .paginators import LimitPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from .filters import RecipeFilter, IngredientSearchFilter
from .mixins import AddDelViewMixin
from .permissions import AuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          UserSubscribeSerializer)

User = get_user_model()

DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    pagination_class = LimitPageNumberPagination
    add_serializer = UserSubscribeSerializer

    @action(methods=('get', 'post', 'delete'), detail=True)
    def subscribe(self, request, id):
        return self.add_del_obj(id, 'subscribe')

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    add_serializer = ShortRecipeSerializer

    @action(methods=('get', 'post', 'delete'), detail=True)
    def favorite(self, request, pk):
        return self.add_del_obj(pk, 'favorite')

    @action(methods=('get', 'post', 'delete'), detail=True)
    def shopping_cart(self, request, pk):
        return self.add_del_obj(pk, 'shopping_cart')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = AmountIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(total_amount=Sum('amount'))

        shopping_list = []
        for item in ingredients:
            shopping_list.append(
                f'{item["ingredient"]} - {item["total_amount"]} '
                f'{item["measure"]} \n'
            )

        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.txt"')
        return response
