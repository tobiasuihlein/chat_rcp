import os
import json
from dotenv import load_dotenv
import anthropic
from recipes.models import *
from django.db import transaction
from django.utils.translation import activate



class RecipeGeneratorService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            max_retries=3,
            timeout=20.0,
        )

    def get_previews_from_LLM(self, prompt: str) -> dict:
        try:
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
        except anthropic.APIError as e:
            print(f"API error: {e}")
        except anthropic.RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
        except anthropic.APITimeoutError as e:
            print(f"Timeout: {e}")

        try:
            answer = json.loads(message.content[0].text)
            return answer
        except json.JSONDecodeError:
            raise ValueError("Sorry, something went wrong, chef.")
        

    def get_recipe_from_LLM(self, prompt: str) -> dict:
        try:
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
        except anthropic.APIError as e:
            print(f"API error: {e}")
        except anthropic.RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
        except anthropic.APITimeoutError as e:
            print(f"Timeout: {e}")

        try:
            answer = json.loads(message.content[0].text)
            return answer
        except json.JSONDecodeError:
            raise ValueError("Sorry, something went wrong, chef.")


    def recipe_to_database(self, recipe):
        activate(recipe['language'])
        try:
            with transaction.atomic():
                recipe_category_object, _ = RecipeCategory.objects.get_or_create(
                    name = recipe['category']
                )
                recipe_object = Recipe.objects.create(
                    title = recipe['title'],
                    description = recipe['description'],
                    difficulty = recipe['difficulty'],
                    time_total = recipe['time']['total'],
                    time_preparation = recipe['time']['preparation'],
                    time_cooking = recipe['time']['cooking'],
                    default_servings = int(recipe.get('servings', 0)),
                    storage = recipe['storage'],
                    category = recipe_category_object,
                    cost = int(recipe.get('cost', 0)),
                    spiciness = int(recipe.get('spiciness', 0))
                )
                for element in recipe['cuisine_type']:
                    type = element['type']
                    subtype = element['subtype']
                    type_object, _ = CuisineType.objects.get_or_create(
                        name = type
                    )
                    subtype_object, _ = CuisineSubtype.objects.get_or_create(
                        name = subtype,
                        cuisine_type = type_object,
                    )
                    recipe_object.cuisine_types.add(type_object)
                    recipe_object.cuisine_subtypes.add(subtype_object)
                for diet in recipe['diet']:
                    diet_object, _ = Diet.objects.get_or_create(
                        name = diet
                    )
                    recipe_object.diets.add(diet_object)
                for cooking_method in recipe['cooking_method']:
                    cooking_method_object, _ = CookingMethod.objects.get_or_create(
                        name = cooking_method
                    )
                    recipe_object.cooking_methods.add(cooking_method_object)
                for hashtag in recipe['hashtags']:
                    hashtag_object, _ = Hashtag.objects.get_or_create(
                        name = hashtag
                    )
                    recipe_object.hashtags.add(hashtag_object)
                for main_ingredient in recipe['main_ingredients']:
                    ingredient_category_object, _ = IngredientCategory.objects.get_or_create(
                        name = main_ingredient['category'],
                    )
                    ingredient_object, _ = Ingredient.objects.get_or_create(
                        name = main_ingredient['name'],
                        category = ingredient_category_object,
                    )
                    RecipeIngredient.objects.create(
                        ingredient = ingredient_object,
                        amount = main_ingredient['amount'],
                        unit = main_ingredient['unit'],
                        type = 'M',
                        recipe = recipe_object,
                    )
                for additional_ingredient in recipe['additional_ingredients']:
                    ingredient_category_object, _ = IngredientCategory.objects.get_or_create(
                        name = additional_ingredient['category'],
                    )
                    ingredient_object, _ = Ingredient.objects.get_or_create(
                        name = additional_ingredient['name'],
                        category = ingredient_category_object,
                    )
                    RecipeIngredient.objects.create(
                        ingredient = ingredient_object,
                        amount = additional_ingredient['amount'],
                        unit = additional_ingredient['unit'],
                        type = 'A',
                        recipe = recipe_object,
                    )
                step_counter = 1
                for instruction_headline, instruction_description in recipe['instructions'].items():
                    RecipeInstruction.objects.create(
                        number = step_counter,
                        headline = instruction_headline,
                        description = instruction_description,
                        recipe = recipe_object,
                    )
                    step_counter += 1
        except Exception as e:
            print(f"Error occured; {str(e)}")
            raise
        

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
    

    def create_recipe_prompt_by_preview(self, recipe_dict: dict) -> str:
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
                    "language": "the language the recipe is written in ('en' for English, 'de' for German)",
                    "title": "string",
                    "difficulty": "difficulty of the dish (use the numbers of the following mapping: 'beginner'->1, 'intermediate'->2, 'advanced'->3, 'expert'->4)",
                    "time": {{
                        "total": "X",
                        "preparation": "X",
                        "cooking": "X",
                    }},
                    "main_ingredients": [
                        {{"name": "ingredient one",
                        "amount": "amount of ingredient one",
                        "unit": "unit for amount specification of ingredient one",
                        "notes": "notes for ingredient one (e.g., 'finely chopped'),
                        "category": "category for ingredient one (e.g. 'vegetable', 'meat')}},
                        {{"name": "ingredient two",
                        "amount": "amount of ingredient two",
                        "unit": "unit for amount specification of ingredient two",
                        "notes": "notes for ingredient two (e.g., 'finely chopped'),
                        "category": "category for ingredient two (e.g. 'vegetable', 'meat')}},
                        {{"name": "ingredient three",
                        "amount": "amount of ingredient three",
                        "unit": "unit for amount specification of ingredient three",
                        "notes": "notes for ingredient three (e.g., 'finely chopped'),
                        "category": "category for ingredient three (e.g. 'vegetable', 'meat')}},
                    ],
                    "additional_ingredients": [
                        {{"name": "ingredient one",
                        "amount": "amount of ingredient one",
                        "unit": "unit for amount specification of ingredient one",
                        "notes": "notes for ingredient one (e.g., 'finely chopped'),
                        "category": "category for ingredient one (e.g. 'oil', 'spice')}},
                        {{"name": "ingredient two",
                        "amount": "amount of ingredient two",
                        "unit": "unit for amount specification of ingredient two",
                        "notes": "notes for ingredient two (e.g., 'finely chopped'),
                        "category": "category for ingredient two (e.g. 'oil', 'spice')}},
                        {{"name": "ingredient three",
                        "amount": "amount of ingredient three",
                        "unit": "unit for amount specification of ingredient three",
                        "notes": "notes for ingredient three (e.g., 'finely chopped'),
                        "category": "category for ingredient thre (e.g. 'oil', 'spice')}},
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
                    "cost": "cost of the dish (use the numbers of the following mapping: 'budget'->1, 'moderate'->2, 'mid-range'->3, 'premium'->4)",
                    "spiciness": "pungency level (use the numbers of the following mapping: 'not spicy'->1, 'mild'->2, 'medium'->3, 'hot'->4)",
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
        15. Amount field for ingredients must be a digit number with max. 2 decimal places

        Return only the JSON, no other text."""

        return prompt