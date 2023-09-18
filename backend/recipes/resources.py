from import_export import resources
from recipes.models import Ingredient


class RecipesIngredient(resources.ModelResource):
    class Meta:
        model = Ingredient
