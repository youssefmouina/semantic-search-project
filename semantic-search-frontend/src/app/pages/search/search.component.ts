import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Meal, MealSearchResponse } from '../../model';
import { MealService } from '../../service/meal.service';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {
  searchQuery: string = '';
  isSearching: boolean = false;
  hasSearched: boolean = false;
  meals: Meal[] = [];
  selectedMeal: Meal | null = null;

  constructor(private mealService: MealService) {}

  onSearch(): void {
    if (!this.searchQuery.trim()) return;

    this.isSearching = true;
    this.hasSearched = true;

    this.mealService.searchMeals(this.searchQuery, 5).subscribe({
      next: (response: MealSearchResponse) => {
        this.meals = response.results;
        this.isSearching = false;
      },
      error: (error: Error) => {
        console.error('Erreur lors de la recherche:', error);
        this.meals = [];
        this.isSearching = false;
      }
    });
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.onSearch();
    }
  }

  selectMeal(meal: Meal): void {
    this.selectedMeal = meal;
  }

  closeDetails(): void {
    this.selectedMeal = null;
  }
}
