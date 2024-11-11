import os
import json
from dotenv import load_dotenv
import anthropic


### CREATE PREVIEWS ###

def create_previews_prompt(ingredients: list, staples: list) -> str:
    prompt = f"""Given these available ingredients: {', '.join(ingredients)}
    And these staple ingredients: {', '.join(staples)}

    Please generate 3 recipe previews in the following exact JSON format, nothing else:

    {{
        "recipes": [
            {{
                "title": "string",
                "difficulty": "Easy|Medium|Hard",
                "time": "X Min.",
                "additional_ingredients": [
                    "ingredient1",
                    "ingredient2"
                ],
                "description": "A brief, appealing description of the dish.",
                "main_ingredients": [
                    "ingredient1",
                    "ingredient2"
                ]
            }}
        ]
    }}

    Requirements:
    1. Response must be valid JSON
    2. Use only the provided ingredients and very common household staples (salt, pepper, olive oil etc.)
    3. Each recipe must be realistic and cookable
    4. Keep descriptions under 200 characters
    5. Time should be in the format "X Min."
    6. Alays create one "Easy", one "Medium", and one "Hard" recipe, if the provided ingredients allow it
    7. List main ingredients from the provided ingredients list
    8. List additional ingredients that are common household staples
    9. Do not use all ingredients, if you feel like they don't match
    10. If you do not find reasonable meals in all difficulties, feel free to provide less than three
    11. Do not add ingredients that are not really common as household staples (e.g eggplant, broccoli), if not included in the provided ingredients
    12. You don't have to use all provided ingredients
    13. Do not use too many additional ingredients

    Return only the JSON, no other text."""

    return prompt


def get_previews_from_claude(prompt: str) -> dict:

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system="You are a helpful chef assistant that returns only valid JSON responses in the exact format requested.",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    try:
        answer = json.loads(message.content[0].text)
        return answer
    except json.JSONDecodeError:
        raise ValueError("Sorry, something went wrong, chef.")


### CREATE RECIPE ###

def create_recipe_prompt(preview: dict) -> str:

    prompt = f"""Given this recipe preview:

        "title": "Parmesan Broccoli Pasta",
        "difficulty": "Medium",
        "time": "25 Min.",
        "additional_ingredients":
            "olive oil",
            "garlic",
            "salt",
            "pepper",
            "butter"
        "description": "Creamy pasta with tender broccoli florets and rich parmesan sauce. Fresh parsley adds a burst of color and flavor to this comforting dish that perfectly combines vegetables with indulgent cheese.",
        "main_ingredients":
            "pasta",
            "broccoli",
            "parmesan",
            "cream",
            "parsley"

    Please create the corresponding recipe in the following exact JSON format, nothing else:

    {{
        "recipe": [
            {{
                "title": "string",
                "difficulty": "Easy|Medium|Hard",
                "time": "X Min.",
                "time": {{
                    "total": "X Min.",
                    "preparation": "X Min.",
                    "cooking": "X Min.",
                }},
                "main_ingredients": [
                    "ingredient1",
                    "ingredient2"
                ],
                "additional_ingredients": [
                    "ingredient1",
                    "ingredient2"
                ],
                "description": "A brief, appealing description of the dish.",
                "number_of_persons": "integer",
                "instructions": {{
                    "step1": [
                        "substep1",
                        "substep2",
                        "substep3"
                    ],
                    "step2": [
                        "substep1",
                        "substep2
                    ],
                }}
                "tips": [
                    "tip1",
                    "tip2"
                ]
                "storage": "string"
            }}
        ]
    }}

    Requirements:
    1. Response must be valid JSON
    2. Use only the provided ingredients
    3. Each recipe must be realistic and cookable
    4. Time should be in the format "X Min."

    Return only the JSON, no other text."""

    return prompt


def get_recipe_from_claude(prompt: str) -> dict:

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system="You are a helpful chef assistant creating accurate recipes based on a provided preview.",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    try:
        answer = json.loads(message.content[0].text)
        return answer
    except json.JSONDecodeError:
        raise ValueError("Sorry, something went wrong, chef.")
        