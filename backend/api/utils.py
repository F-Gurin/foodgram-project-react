from string import hexdigits

from rest_framework.serializers import ValidationError

from recipes.models import AmountIngredient


def is_hex_color(value):
    if len(value) not in (3, 6):
        raise ValidationError(
            f'{value} не правильной длины ({len(value)}).'
        )
    if not set(value).issubset(hexdigits):
        raise ValidationError(
            f'{value} не шестнадцатиричное.'
        )


incorrect_layout = str.maketrans(
    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
    'йцукенгшщзхъфывапролджэячсмитьбю.'
)
