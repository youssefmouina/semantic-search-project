export interface Ingredient {
  name: string;
}

export interface MealIngredient {
  ingredient: Ingredient;
  portion: number | null;
  unit: string | null;
}

