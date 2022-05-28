import pdb
from datetime import datetime as dt
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse

from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import Ingredient, Recipe, Tag, AmountIngredient

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .mixins import AddDelViewMixin
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAdminOrReadOnly, IsStaffOrReadOnly, AuthorOrReadOnly
from .serializers import (UserSubscribeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          )
from .services import incorrect_layout

User = get_user_model()

DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    pagination_class = PageNumberPagination
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

    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translate(incorrect_layout)
            name = name.lower()
            stw_queryset = list(queryset.filter(name__startswith=name))
            cnt_queryset = queryset.filter(name__contains=name)
            stw_queryset.extend(
                [i for i in cnt_queryset if i not in stw_queryset]
            )
            queryset = stw_queryset
        return queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    add_serializer = ShortRecipeSerializer

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping in ('1', 'true'):
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping in ('0', 'false'):
            queryset = queryset.exclude(cart=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ('1', 'true'):
            queryset = queryset.filter(favorite=user.id)
        if is_favorited in ('0', 'false'):
            queryset = queryset.exclude(favorite=user.id)

        return queryset


    def perform_destroy(self, serializer):
        super().perform_destroy(serializer)

    @action(methods=('get', 'post', 'delete'), detail=True)
    def favorite(self, request, pk):
        return self.add_del_obj(pk, 'favorite')

    @action(methods=('get', 'post', 'delete'), detail=True)
    def shopping_cart(self, request, pk):
        return self.add_del_obj(pk, 'shopping_cart')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = AmountIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        # filename = f'{user.username}_shopping_list.txt'
        # shopping_list = (
        #     f'Список покупок: пользователя {user.first_name}\n\n'
        #     f'{dt.now().strftime(DATE_TIME_FORMAT)}\n\n'
        # )

        # for ing in ingredients:
        #     shopping_list += (
        #         f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
        #     )
        # response = HttpResponse(
        #     shopping_list, content_type='shopping_list.txt; charset=utf-8'
        # )
        # response['Content-Disposition'] = f'attachment; filename={filename}'
# *******************
        shopping_list = []
        for item in ingredients:
            shopping_list.append(f'{item["ingredient"]} - {item["amount"]} '
                                 f'{item["measure"]} \n')

        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.txt"')
        return response
# *******************
        # return response
