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
                "description": "A brief, appealing description of the dish.",
                "main_ingredients": [
                    "ingredient1",
                    "ingredient2"
                ],
                "additional_ingredients": [
                    "ingredient1",
                    "ingredient2"
                ]
            }}
        ]
    }}

    Requirements:
    1. Response must be valid JSON
    2. Use only the provided main ingredients and very common household staples (salt, pepper, olive oil etc.) as additional ingredients
    3. Each recipe must be realistic and cookable
    4. Keep descriptions under 200 characters
    5. Time should be in the format "X Min." and refer to the total time necessary
    6. Difficulties should be one of these: "Easy", "Medium", or "Hard"
    7. List main ingredients from the provided ingredients list
    8. List additional ingredients that are common household staples
    9. Do not use all ingredients, if you feel like they don't match
    10. Only combine provided ingredients that actually match
    11. Do not add ingredients that are not really common as household staples (e.g eggplant, broccoli), if not included in the provided ingredients
    12. You don't have to use all provided ingredients
    13. Do not use too many additional ingredients
    14. Try to provide one very basic, one quite common, and one more extravagant dish (but also for the extravagant dish: use only the provided ingredients)
    15. Only create recipes with the best ratings
    16. Focus on European dishes and eating traditions

    Return only the JSON, no other text."""

    return prompt


def get_previews_from_claude(prompt: str) -> dict:

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        # model="claude-3-haiku-20240307",
        # model="claude-3-5-haiku-latest",
        model="claude-3-5-sonnet-latest",
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

def create_recipe_prompt(recipe_dict: dict) -> str:

    prompt = f"""Given these recipe information:
    
    Title: {recipe_dict['title']}
    Description: {recipe_dict['description']}
    Total Time: {recipe_dict['time']}
    Difficulty: {recipe_dict['difficulty']}
    Ingredients: {recipe_dict['main_ingredients']} and {recipe_dict['additional_ingredients']}

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
                    "Xg ingredient one",
                    "Yg ingredient two",
                    "Zg ingredient three"
                ],
                "additional_ingredients": [
                    "X tbsp additional ingridient 1",
                    "Y whatever unit additional ingridient 2"
                ],
                "description": "A brief, appealing description of the dish.",
                "servings": "number of persons to serve with this recipe",
                "instructions": {{
                    "headline step one": "description step one",
                    "headline step two": "description step two",
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
    5. Use the metric system and Celcius instead of Fahrenheit
    6. For each instruction step create an appropriate headline and a short paragraph

    Return only the JSON, no other text."""

    return prompt


def get_recipe_from_claude(prompt: str) -> dict:

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        # model="claude-3-haiku-20240307",
        # model="claude-3-5-haiku-latest",
        model="claude-3-5-sonnet-latest",
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
        