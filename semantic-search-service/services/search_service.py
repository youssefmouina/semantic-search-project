# meal_search.py
import os
import json
import faiss
import numpy as np
import re
from docx import Document
from sentence_transformers import SentenceTransformer
from typing import Optional, List
from models.meal import MealWithScore, MealIngredient, Ingredient

# ==============================
# Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEALS_FOLDER = os.path.join(BASE_DIR, "../Documents")
FAISS_FILE = os.path.join(MEALS_FOLDER, "meals.index")
MEAL_IDS_FILE = os.path.join(MEALS_FOLDER, "meal_ids.json")

MODEL_NAME = "sentence-transformers/LaBSE"


# Meal Image URL Mapping
MEAL_IMAGE_MAPPING = {
    "01f85d39-16c2-417d-9481-1e1bebdf3207": "https://file.b18a.io/7842434458200107746_340848_.jpg",
    "05d8fdc5-c03b-4f48-b44d-bb7178156e45": "https://file.b18a.io/7847157147000105810_787174_.jpeg",
    "0973496f-8d41-48a1-9888-95cbb5f656a1": "https://file.b18a.io/7832983819500100884_546823_.jpeg",
    "0bc24bc6-8676-470e-81ec-2451ff658935": "https://file.b18a.io/7841995087200104392_419479_.jpeg",
    "140065d1-d507-4be9-bae5-2e944a87e643": "https://file.b18a.io/7928017056100105700_461173_.jpg",
    "17353f50-5bbf-4567-9c59-63e661cb60da": "https://file.b18a.io/7840541157000105888_618995_.jpg",
    "1b5bc3d6-d311-46ab-a1e6-15027b1af3cc": "https://file.b18a.io/7833363329800104589_241538_.jpeg",
    "1e823538-d5c8-4000-8f4d-02b62ae50499": "https://file.b18a.io/7838488266000105545_955159_.jpg",
    "2c3f3991-876f-4b7b-b514-ce45cd89f8e3": "https://file.b18a.io/7894755423500102364_425378_.jpg",
    "32010752-f5a4-4cf1-aa7e-a223034d0161": "https://file.b18a.io/7840839165300101543_416552_.png",
    "35872205-6f23-41be-8574-96be6a9a02c4": "https://file.b18a.io/7846305868200104171_284990_.jpg",
    "36d42f22-dc45-44de-986a-1be2e8a84eee": "https://file.b18a.io/7841850970800101152_402478_.jpg",
    "3ae6f379-bcbd-43fc-ab0b-f736d73e1e2e": "https://file.b18a.io/7976511072200107061_840178_.jpeg",
    "42236411-3dbb-4b71-8eef-872ff3ceaf3d": "https://file.b18a.io/7838946668200106359_887715_.jpg",
    "47d203ff-1446-4e25-803a-6acbce0e43ea": "https://file.b18a.io/7903176130800108550_520442_.jpg",
    "5d639067-11a3-4718-abc8-450b719d8f4f": "https://file.b18a.io/7833521803100102100_570454_.png",
    "62f62c98-8e4c-45f2-838e-23040822ff9f": "https://file.b18a.io/7833630771000100804_688005_.jpeg",
    "64bf7662-0aeb-481e-b315-9241a90ea2c2": "https://file.b18a.io/7959581219000104202_898032_.jpeg",
    "71cbd6eb-69e3-4075-a8f3-b7caa0137708": "https://file.b18a.io/7832686616300100575_768281_.jpeg",
    "7bf78add-5937-4b2f-9d17-20c1361d7aa8": "https://file.b18a.io/default_meal_image.jpg",
    "8653243c-58f8-4a09-9826-6148d011a67e": "https://file.b18a.io/7832629026100104136_901895_.jpe",
    "9e8450e4-0869-4e22-be5e-5f5e9bfec0c3": "https://file.b18a.io/7841074186800109284_920873_.png",
    "a1daaadb-02d8-4842-ad5e-1c316e97769a": "https://file.b18a.io/7846841303500103132_681018_.jpeg",
    "adc1f97d-d7d3-4308-bc0b-246831e1f272": "https://file.b18a.io/7849384442800104179_926397_.jpeg",
    "bb133d47-d814-42b7-9b48-0719dde05ba7": "https://file.b18a.io/7833632516000101563_908596_.jpeg",
    "d331fe20-9e46-4d97-ab04-80a8ed1c9ed5": "https://file.b18a.io/7837461040900106360_844437_.jpeg",
    "dc35b702-9e49-44f7-ba61-3255bfe5a5b6": "https://file.b18a.io/7834709583700102710_340980_.jpeg",
    "e9c409fd-b11e-4651-9baf-e8b00cf7da6a": "https://file.b18a.io/7833425194800102115_575499_.jpeg",
    "fc371622-5305-4509-8106-8daf95a0bfb1": "https://file.b18a.io/7840744532400108694_279917_.jpg",
    "fdceca92-cf68-42a9-a8ed-23eec6a406a8": "https://file.b18a.io/7833018387700100119_779122_.jpeg",
    "cb91dd7e-21b5-4030-b798-9c530fc1e5de": "https://file.b18a.io/7841867225700103761_775950_.jpeg",
    "97ecc7ac-2839-4cf4-9dce-def166d2b627": "https://file.b18a.io/7842521353500106898_629823_.png"
}


# Load Model & Index
print("Loading LaBSE model...")
model = SentenceTransformer(MODEL_NAME)
print("✓ LaBSE Loaded")

print("Loading FAISS index...")
index = faiss.read_index(FAISS_FILE)
print("✓ FAISS Loaded")

print("Loading meal IDs...")
with open(MEAL_IDS_FILE, "r", encoding="utf-8") as f:
    meal_ids = json.load(f)
print(f"✓ Loaded {len(meal_ids)} meal IDs")


# Extract JSON from DOCX
def extract_meal_from_docx(meal_id: str, filepath: str) -> Optional[dict]:
    try:
        doc = Document(filepath)

        raw_lines = []
        for p in doc.paragraphs:
            if p.text.strip():
                raw_lines.extend([l.strip() for l in p.text.split("\n") if l.strip()])

        meal = {
            "mealId": meal_id,
            "mealName": raw_lines[0],
            "foodType": "",
            "cooking_method": "",
            "mealTargetCalories": 0.0,
            "mealTargetProtein": 0.0,
            "mealTargetCarbs": 0.0,
            "mealTargetFats": 0.0,
            "description": "",
            "mealTypes": [],
            "mealIngredients": []
        }

        section = None

        for line in raw_lines[1:]:
            lower = line.lower()



            if lower == "meal information":
                section = "info"
                continue
            if lower == "nutritional profile":
                section = "nutrition"
                continue
            if lower == "ingredients":
                section = "ingredients"
                continue
            if lower == "description":
                section = "description"
                continue

            if section == "info":
                if line.startswith("Food Type:"):
                    meal["foodType"] = line.split(":", 1)[1].strip()

                elif line.startswith("Cooking Method:"):
                    meal["cooking_method"] = line.split(":", 1)[1].strip()

                elif line.startswith("Meal Types:"):
                    meal["mealTypes"] = [
                        t.strip() for t in line.split(":", 1)[1].split(",")
                    ]

            elif section == "nutrition":
                if "Calories" in line:
                    meal["mealTargetCalories"] = float(re.findall(r"\d+", line)[0])
                elif "Protein" in line:
                    meal["mealTargetProtein"] = float(re.findall(r"\d+", line)[0])
                elif "Carbohydrates" in line:
                    meal["mealTargetCarbs"] = float(re.findall(r"\d+", line)[0])
                elif "Fats" in line:
                    meal["mealTargetFats"] = float(re.findall(r"\d+", line)[0])


            elif section == "ingredients":
                name_part = line.split(":", 1)[0]

                portion = None
                unit = None

                match = re.search(r"(.*?)(?:-\s*(\d+)(g|ml))?$", name_part)
                if match:
                    name = match.group(1).strip()
                    if match.group(2):
                        portion = float(match.group(2))
                        unit = match.group(3)
                else:
                    name = name_part.strip()

                meal["mealIngredients"].append({
                    "ingredient": {"name": name},
                    "portion": portion,
                    "unit": unit
                })

            elif section == "description":
                meal["description"] += line + " "

        meal["description"] = meal["description"].strip()
        return meal

    except Exception as e:
        print(f"Error parsing DOCX {filepath}: {e}")
        return None


def get_meal_by_id(meal_id: str, score: float = 0.0) -> Optional[MealWithScore]:
    clean_id = meal_id.replace("meal_", "")
    filename = f"meal_{clean_id}.docx"
    filepath = os.path.join(MEALS_FOLDER, filename)

    if not os.path.exists(filepath):
        return None

    meal_data = extract_meal_from_docx(clean_id,filepath)
    if not meal_data:
        return None

    ingredients = [
        MealIngredient(
            ingredient=Ingredient(name=i["ingredient"]["name"]),
            portion=i.get("portion"),
            unit=i.get("unit")
        )
        for i in meal_data["mealIngredients"]
    ]

    return MealWithScore(
        mealId=meal_data["mealId"],
        mealimageurl=MEAL_IMAGE_MAPPING.get(clean_id),
        mealName=meal_data["mealName"],
        foodType=meal_data["foodType"],
        cooking_method=meal_data["cooking_method"],
        mealTargetCalories=meal_data["mealTargetCalories"],
        mealTargetProtein=meal_data["mealTargetProtein"],
        mealTargetCarbs=meal_data["mealTargetCarbs"],
        mealTargetFats=meal_data["mealTargetFats"],
        description=meal_data["description"],
        mealTypes=meal_data["mealTypes"],
        mealIngredients=ingredients,
        score=score
    )

# Semantic Search
def semantic_search(query: str, top_k: int = 5) -> List[MealWithScore]:
    if not query.strip():
        return []

    print(f"\n🔎 Searching for: {query}")

    # Encode query
    q_emb = model.encode([query], show_progress_bar=False).astype("float32")

    # Normalize query
    q_emb /= np.linalg.norm(q_emb, axis=1, keepdims=True)

    # Search
    scores, idxs = index.search(q_emb, top_k)

    results = []
    for idx, score in zip(idxs[0], scores[0]):
        if idx < 0 or idx >= len(meal_ids):
            continue

        meal_id = meal_ids[idx]
        meal_with_score = get_meal_by_id(meal_id, float(round(score, 4)))

        if meal_with_score:
            results.append(meal_with_score)

    return results


