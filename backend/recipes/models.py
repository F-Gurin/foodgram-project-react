from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):

    password = models.CharField(max_length=150,
                                verbose_name='Пароль'
                                )
    username = models.CharField(max_length=150,
                                verbose_name='Логин',
                                unique=True
                                )
    email = models.EmailField(max_length=254,
                              verbose_name='Электронная почта',
                              unique=True
                              )
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя'
                                  )
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия',
                                 )
    is_subscribed = models.BooleanField(default=False)
    subscribe = models.ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='self',
        symmetrical=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(unique=True,
                            max_length=200,
                            db_index=True,
                            verbose_name='Тег',
                            )
    color = models.CharField(unique=True,
                             max_length=8,
                             verbose_name='Цвет',
                             blank=True,
                             null=True,
                             )
    slug = models.SlugField(unique=True,
                            max_length=200,
                            verbose_name='Слаг',
                            blank=True,
                            null=True,
                            )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(unique=True,
                            max_length=200,
                            db_index=True,
                            verbose_name='Ингредиент',
                            )
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единицы измерения',
                                        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag,
                                  blank=True,
                                  verbose_name='Тег',
                                  related_name='recipes',
                                  )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        through='recipes.AmountIngredient',
    )
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Рецепт'
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='',
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
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
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
