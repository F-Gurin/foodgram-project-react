from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):

    password = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_subscribed = models.BooleanField(blank=True, null=True)
    subscribe = models.ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='self',
        symmetrical=False,
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Tag(models.Model):
    name = models.CharField(unique=True,
                            max_length=200,
                            db_index=True,
                            verbose_name='Тег')
    color = models.CharField(unique=True,
                             max_length=8,
                             blank=True,
                             null=True,)
    slug = models.SlugField(unique=True,
                            max_length=200,
                            blank=True,
                            null=True,)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Тег'


class Ingredient(models.Model):
    name = models.CharField(unique=True,
                            max_length=200,
                            db_index=True,
                            verbose_name='Ингредиент')
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipes')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        through='recipes.AmountIngredient',
    )
    is_favorited = models.BooleanField(default=False,)
    is_in_shopping_cart = models.BooleanField(default=False,)
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Рецепт'
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipe_images/',
        blank=True,
        null=True,
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now=True
    )
    favorite = models.ManyToManyField(
        User,
        verbose_name='Любимые рецепты',
        related_name='favorites',
    )
    cart = models.ManyToManyField(
        User,
        verbose_name='Список покупок',
        related_name='carts',
    )

    class Meta:
        verbose_name_plural = 'Рецепт'
        verbose_name = 'Рецепты'
        ordering = ('-pub_date',)


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        default=0,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('recipe', )
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='\n%(app_label)s_%(class)s ингредиент уже добавлен\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'
