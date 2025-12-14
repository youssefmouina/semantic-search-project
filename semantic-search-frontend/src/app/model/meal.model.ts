import { MealIngredient } from './ingredient.model';

export interface Meal {
  mealId: string;
  mealimageurl: string;
  mealName: string;
  foodType: string;
  cooking_method: string;
  mealTargetCalories: number;
  mealTargetProtein: number;
  mealTargetCarbs: number;
  mealTargetFats: number;
  description: string;
  mealTypes: string[];
  mealIngredients: MealIngredient[];
  score: number;
}

export interface MealSearchResponse {
  results: Meal[];
  total: number;
}

