import os
import json
from dotenv import load_dotenv
import anthropic
from .models import Recipe


class RecipeGeneratorService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def get_previews_from_LLM(self, prompt: str) -> dict:
        message = self.client.messages.create(
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
        

    def get_recipe_from_LLM(self, prompt: str) -> dict:

        message = self.client.messages.create(
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


    def recipe_to_database(self, request):
        print(request.POST.keys())
        print(request.POST['main_ingredients'])
        Recipe.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            difficulty=request.POST['difficulty'],
            time_total=request.POST['time']['total'],
            time_preparation=request.POST['time']['preparation'],
            time_cooking=request.POST['time']['cooking'],
            default_servings = int(request.POST.get('servings', 0)),
        )
        

    def create_previews_prompt(self, ingredients: list, staples: list) -> str:
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
        3. Each recipe must be realistic, cookable, and tasty (use proven cooking techniques and flavor combinations)
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
        15. Only create recipes that you would expect to receive the best ratings
        16. For more advanced dishes, follow Michelin-star quality standards for: ingredient balance, texture combinations, flavor layering, presentation
        17. If you use dashes, make sure to use them properly (not '-', but '–')

        Return only the JSON, no other text."""

        return prompt
    

    def create_recipe_prompt(self, recipe_dict: dict) -> str:
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
                        "total": "X",
                        "preparation": "X",
                        "cooking": "X",
                    }},
                    "main_ingredients": [
                        {{"name": "ingredient one",
                        "amount": "amount of ingredient one",
                        "unit": "unit for amount specification of ingredient one",
                        "notes": "notes for ingredient one (e.g., 'finely chopped')}},
                        {{"name": "ingredient two",
                        "amount": "amount of ingredient two",
                        "unit": "unit for amount specification of ingredient two",
                        "notes": "notes for ingredient two (e.g., 'finely chopped')}},
                        {{"name": "ingredient three",
                        "amount": "amount of ingredient three",
                        "unit": "unit for amount specification of ingredient three",
                        "notes": "notes for ingredient three (e.g., 'finely chopped')}},
                    ],
                    "additional_ingredients": [
                        {{"name": "ingredient one",
                        "amount": "amount of ingredient one",
                        "unit": "unit for amount specification of ingredient one",
                        "notes": "notes for ingredient one (e.g., 'finely chopped')}},
                        {{"name": "ingredient two",
                        "amount": "amount of ingredient two",
                        "unit": "unit for amount specification of ingredient two",
                        "notes": "notes for ingredient two (e.g., 'finely chopped')}},
                        {{"name": "ingredient three",
                        "amount": "amount of ingredient three",
                        "unit": "unit for amount specification of ingredient three",
                        "notes": "notes for ingredient three (e.g., 'finely chopped')}},
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
                    "storage": "string",
                    "cuisine_type": [
                    {{"type": "Type 1 (e.g. 'Mediterranean')",
                    "subtype": "Subtype 1 (e.g. Italian)}}",
                    {{"type": "Type 2 (e.g. 'Asian')",
                    "subtype": "Subtype 2 (e.g. Vietnamese)}}",
                    {{"type": "Type 3 (e.g. 'Central European')",
                    "subtype": "Subtype 3 (e.g. German)}}",
                    ],
                    "category": "type of dish (e.g., 'Main course', 'Soup', or 'Dessert'),
                    "diet": ["diet restriction one (e.g. 'Vegetarian')", "diet restriction two (e.g., 'Gluten-Free')"],
                    "cooking_method": ["cooking method one (e.g. 'Grilling')", "cooking method two (e.g., 'Baking')"],
                    "cost": "cost of the dish (e.g., 'Budget')",
                    "spiciness": "pungency level (use the numbers of the following mapping: 'not spicy'->0, 'mild'->1, 'medium'->2, 'hot'->3, 'very hot'->4, 'extreme'->5)",
                    "hashtags": ["hashtag one (e.g., 'Winter')", "hashtag two (e.g., 'Classic')", "hashtag three (e.g. Super-Sweet)", "hashtag four (e.g., Party-Food)", "hashtag five (e.g. Birthday)],
                }}
            ]
        }}

        Requirements:
        1. Response must be valid JSON
        2. Use only the provided ingredients
        3. Each recipe must be realistic and cookable
        4. Time must be the number of minutes
        5. Use the metric system and Celcius instead of Fahrenheit always
        6. For each instruction step create an appropriate headline and a short paragraph
        7. Notes for ingredients must be short
        8. List of cuisine types maybe only one (if dish is common only in one specific cuisine) or several (if dish is common in several cusines)
        9. For the list of cuisine types, follow the rule that the type is the superordinate category (e.g. Mediterranean), while the subtype is the basic or generic level (e.g. Italian)
        10. If several types or subtyes apply, use separate items in the list (do not combine two types to a new category, e.g. do not use Italian-American, but use two separate types instead)
        11. Make sure to provide appropriate spiciness (level 0 only if no spice at all, i.e. no pepper)
        12. For the hashtags, try to use single words if possible, else user '-' to combine, always use capitalized words (e.g. Super-Sweet, Party-Food, Sharing-Plate)
        13. For the hashtags, do not repeat other properties already provided (such as cuisine type or cost)
        14. For more advanced dishes, follow Michelin-star quality standards for: ingredient balance, texture combinations, flavor layering, presentation

        Return only the JSON, no other text."""

        return prompt