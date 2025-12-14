from fastapi import APIRouter, Query
from models.meal import SearchResponse
from services.search_service import semantic_search
from services.build_index import load_documents
import os

router = APIRouter()




@router.get("/search", response_model=SearchResponse)
async def search_meals(query: str = Query(..., description="Search query"), top_k: int = 5):

    results = semantic_search(query, top_k)
    return SearchResponse(results=results, total=len(results))




