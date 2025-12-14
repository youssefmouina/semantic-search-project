import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MealSearchResponse } from '../model';

@Injectable({
  providedIn: 'root'
})
export class MealService {
  private readonly baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  searchMeals(query: string, topK: number = 5): Observable<MealSearchResponse> {
    const params = new HttpParams()
      .set('query', query)
      .set('top_k', topK.toString());

    return this.http.get<MealSearchResponse>(`${this.baseUrl}/meals/search`, { params });
  }
}
