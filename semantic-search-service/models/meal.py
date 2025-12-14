from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    name: str

class MealIngredient(BaseModel):
    ingredient: Ingredient
    portion: Optional[float]
    unit: Optional[str]

class Meal(BaseModel):
    mealId: str
    mealName: str
    foodType: str
    mealimageurl: str
    cooking_method: str
    mealTargetCalories: float
    mealTargetProtein: float
    mealTargetCarbs: float
    mealTargetFats: float
    description: str
    mealTypes: List[str]
    mealIngredients: List[MealIngredient]

class MealsRequest(BaseModel):
    meals: List[Meal]

class MealWithScore(BaseModel):
    mealId: str
    mealimageurl: str
    mealName: str
    foodType: str
    cooking_method: str
    mealTargetCalories: float
    mealTargetProtein: float
    mealTargetCarbs: float
    mealTargetFats: float
    description: str
    mealTypes: List[str]
    mealIngredients: List[MealIngredient]
    score: float

class SearchResponse(BaseModel):
    results: List[MealWithScore]
    total: int

