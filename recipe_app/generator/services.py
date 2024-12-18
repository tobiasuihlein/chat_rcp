import os
import json
from dotenv import load_dotenv
import anthropic
import openai
import mistralai
from recipes.models import *
from django.db import transaction
import base64
from io import BytesIO
from django.conf import settings


class ImageGeneratorService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        openai.api_key = self.api_key

    def get_image(self, recipe_dict: str):
        prompt = f"""
        
        Create an appealing realistic high-quality photograph of the following dish:

        Title: {recipe_dict['title']}
        Description: {recipe_dict['description']}

        Show the dish, not the individual ingredients.

        """

        try:
            message = prompt
            response = self.client.images.generate(
                model = "dall-e-3",
                prompt = message,
                n = 1,
                size = "1024x1024",
                quality = "hd",
            )
            image_url = response.data[0].url
            print(image_url)
            return image_url
        except openai.OpenAIError as e:
            print(f"OpenAI Error: {e}")


class PixtralHandler:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.client = mistralai.Mistral(api_key=self.api_key)
    
    def encode_image(self, image_file):
        """
        Encode the uploaded image file to base64
        """
        try:
            # Read the uploaded file into BytesIO
            image_data = BytesIO(image_file.read())
            # Encode to base64
            base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
            return base64_image
        except Exception as e:
            raise ValueError(f"Error encoding image: {str(e)}")

    def process_image(self, image_file, prompt):
        """
        Process the image using Pixtral API
        """
        try:
            # Encode the image
            image_base64 = self.encode_image(image_file)
            
            # Prepare the messages for the API
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", 
                         "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
            
            # Make the API call
            response = self.client.chat.complete(
                model="pixtral-large-latest",
                messages=messages,
                response_format = {
                "type": "json_object",
            }
            )

            content_str = response.choices[0].message.content

            recipe = json.loads(content_str)

            return recipe
            
            
        except Exception as e:
            raise ValueError(f"Error processing image with Pixtral: {str(e)}")


class MistralRecipeGeneratorService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.client = mistralai.Mistral(api_key=self.api_key)

    def get_recipe_from_Mistral(self, prompt: str) -> dict:
        
        message = self.client.chat.complete(
            model = "mistral-large-latest",
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format = {
                "type": "json_object",
            }
        )

        content_str = message.choices[0].message.content
        recipe = json.loads(content_str)

        return recipe


class ClaudeRecipeGeneratorService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            max_retries=2,
            timeout=40,
        )

    def get_previews_from_Claude(self, prompt: str) -> dict:
        try:
            message = self.client.messages.create(
                # model="claude-3-haiku-20240307",
                # model="claude-3-5-haiku-latest",
                model="claude-3-5-sonnet-latest",
                max_tokens=1024,
                temperature=1.0,
                system="You are a helpful chef assistant that returns only valid JSON responses in the exact format requested.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        except anthropic.APIError as e:
            print(f"Anthropic API error: {e}")
        except anthropic.RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
        except anthropic.APITimeoutError as e:
            print(f"Timeout: {e}")

        try:
            answer = json.loads(message.content[0].text)
            return answer
        except json.JSONDecodeError:
            raise ValueError("Sorry, something went wrong, chef.")
        

    def get_recipe_from_Claude(self, prompt: str) -> dict:
        try:
            message = self.client.messages.create(
                # model="claude-3-haiku-20240307",
                # model="claude-3-5-haiku-latest",
                model="claude-3-5-sonnet-latest",
                max_tokens=2048,
                temperature=0.3,
                system="You are a helpful chef assistant creating accurate recipes based on a provided preview that returns only valid JSON responses in the exact format requested.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        except anthropic.APIError as e:
            print(f"Anthropic API error: {e}")
        except anthropic.RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
        except anthropic.APITimeoutError as e:
            print(f"Timeout: {e}")

        try:
            answer = json.loads(message.content[0].text)
            return answer
        except json.JSONDecodeError:
            print(message.content[0].text)
            raise ValueError("JSON could not be decoded properly.")


def recipe_to_database(recipe):
    try:
        with transaction.atomic():

            language_object, _ = Language.objects.get_or_create(
                code = recipe['language']
            )

            recipe_category_object, _ = RecipeCategory.objects.get_or_create(
                name = recipe['category'],
                language = language_object
            )

            beverage_type_object, _ = BeverageType.objects.get_or_create(
                name = recipe['beverage']['type'],
                language = language_object
            )

            beverage_object, _ = Beverage.objects.get_or_create(
                name = recipe['beverage']['name'],
                type = beverage_type_object,
                language = language_object
            )

            recipe_object = Recipe.objects.create(
                title = recipe['title'],
                description = recipe['description'],
                difficulty = recipe['difficulty'],
                default_servings = int(recipe.get('servings', 0)),
                storage = recipe['storage'],
                category = recipe_category_object,
                cost = int(recipe.get('cost', 0)),
                spiciness = int(recipe.get('spiciness', 0)),
                beverage = beverage_object,
                language = language_object
            )

            for time in recipe['times']:
                RecipeTime.objects.create(
                        name = time['name'],
                        value = time['value'],
                        recipe = recipe_object,
                        language = language_object
                    )

            for cuisine_type in recipe['cuisine_type']:
                type_object, _ = CuisineType.objects.get_or_create(
                    name = cuisine_type,
                    language = language_object
                )
                recipe_object.cuisine_types.add(type_object)

            for equipment in recipe['equipment']:
                equipment_object, _ = Equipment.objects.get_or_create(
                    name = equipment,
                    language = language_object
                )
                recipe_object.equipments.add(equipment_object)
            
            for diet in recipe['diet']:
                diet_object, _ = Diet.objects.get_or_create(
                    name = diet,
                    language = language_object
                )
                recipe_object.diets.add(diet_object)
            
            for cooking_method in recipe['cooking_method']:
                cooking_method_object, _ = CookingMethod.objects.get_or_create(
                    name = cooking_method,
                    language = language_object
                )
                recipe_object.cooking_methods.add(cooking_method_object)

            for hashtag in recipe['hashtags']:
                hashtag_object, _ = Hashtag.objects.get_or_create(
                    name = hashtag,
                    language = language_object
                )
                recipe_object.hashtags.add(hashtag_object)

            for component in recipe['components']:
                component_object = RecipeComponent.objects.create(
                    name = component['name'],
                    recipe = recipe_object,
                )
            
                for component_ingredient in component['ingredients']:
                    ingredient_category_object, _ = IngredientCategory.objects.get_or_create(
                        name = component_ingredient['category'],
                        language = language_object
                    )
                    ingredient_object, _ = Ingredient.objects.get_or_create(
                        name = component_ingredient['name'],
                        category = ingredient_category_object,
                        language = language_object
                    )
                    ComponentIngredient.objects.create(
                        ingredient = ingredient_object,
                        amount = component_ingredient['amount'],
                        unit = component_ingredient['unit'],
                        note = component_ingredient['notes'],
                        recipe_component = component_object,
                        language = language_object
                    )

            step_counter = 1
            for instruction_headline, instruction_description in recipe['instructions'].items():
                RecipeInstruction.objects.create(
                    number = step_counter,
                    headline = instruction_headline,
                    description = instruction_description,
                    recipe = recipe_object,
                    language = language_object
                )
                step_counter += 1

            for tip in recipe['tips']:
                RecipeTip.objects.create(
                    tip = tip,
                    recipe = recipe_object,
                    language = language_object
                )

        return recipe_object
    
    except Exception as e:
        print(f"Error occured; {str(e)}")
        raise


def create_previews_prompt(user_input) -> str:
    prompt = f"""Given this user input: {user_input}

    Please generate 3 recipe previews in the following exact JSON format, nothing else:

    {{
        "recipes": [
            {{
                "title": "string",    // Title of the recipe
                "difficulty": number, // 1=beginner, 2=advanced, 3=expert
                "time": "X Min.",     // sum of both active (preparation, cooking, ...) and inactive time (cooling, proofing, ...)
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
    2. Each recipe must be realistic, cookable, and tasty (use proven cooking techniques and flavor combinations)
    3. Keep descriptions under 200 characters
    4. Time should be in the format "X Min." and refer to the total time necessary
    5. Difficulties should be one of these: "Easy", "Medium", or "Hard"
    6. Try to provide one very basic, one relatively common, and one more extravagant dish
    7. Only create recipes that you would expect to receive the best ratings
    8. For expert level dishes, follow Michelin-star quality standards for: ingredient balance, texture combinations, flavor layering, presentation
    9. If you use dashes, make sure to use them properly (not '-', but '–')
    10. Make sure to include also spices and seasoning in the ingredients lists
    11. Explain complex steps in more detail than easier ones
    12. For difficulty, provide a number

    Language: German

    Return only the JSON, no other text."""

    return prompt


def create_recipe_prompt_for_image() -> str:
    prompt = f"""Please evaluate the provided image. It might either be a recipe description, notes for a recipe, or a the photo of a dish.

    Please create the corresponding recipe in the following exact JSON format, nothing else:

    {{
        "recipe": [
            {{
                "language": "en|de",  // Language code
                "title": string,      // Recipe title
                "difficulty": number, // 1=beginner, 2=advanced, 3=expert
                "times": [
                    {{"name": "time_1", "value": number}}, // e.g. preparation: 20
                    {{"name": "time_2", "value": number}}, // e.g. cooking time: 10
                ] // list of times necessary to spent for the dish (including cooling or resting time)
                "components": [
                    {{
                        "name": string, // name of the first component (e.g., 'Steak')
                        "ingredients": [
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
                        ] // list of the ingredients for the first component
                        }},
                    {{
                        "name": string, // name of the second component (e.g., 'Wine Sauce')
                        "ingredients": [
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
                        ] // list of the ingredients for the first component
                        }}
                ],
                "description": "A brief, appealing description of the dish.",
                "servings": number, // number of persons to serve with this recipe
                "instructions": {{
                    "headline step one": "description step one",
                    "headline step two": "description step two",
                }}
                "tips": [
                    "tip1",
                    "tip2"
                ]
                "storage": "string",
                "cuisine_type": ['cuisine_type_1', 'cuisine_type_2', ...],
                "equipment": ['equipment_1', 'equipment_2', ...],
                "category": "type of dish (e.g., 'Main course', 'Soup', or 'Dessert'),
                "diet": ["diet restriction one (e.g. 'Vegetarian')", "diet restriction two (e.g., 'Gluten-Free')"],
                "cooking_method": ["cooking method one (e.g. 'Grilling')", "cooking method two (e.g., 'Baking')"],
                "cost": "cost of the dish (use the numbers of the following mapping: 'budget'->1, 'moderate'->2, 'premium'->3)",
                "spiciness": "pungency level (use the numbers of the following mapping: 'not spicy'->0, 'mild'->1, 'medium'->2, 'hot'->3)",
                "beverage": {{
                    "name": string // name of the beverage (e.g., Chardonnay) // Beverage recommendation
                    "type": string // type of beverage (e.g., White Wine)
                }}
                "hashtags": ["hashtag one (e.g., 'Winter')", "hashtag two (e.g., 'Classic')", "hashtag three (e.g. Super-Sweet)", "hashtag four (e.g., Party-Food)", "hashtag five (e.g. Birthday)],
            }}
        ]
    }}

    Requirements:
    1. Response must be valid JSON
    2. Use only the provided ingredients
    3. Each recipe must be realistic and cookable
    4. Time specifications in number minutes; time values should add up to total time necessary (e.g. cutting ingredients during cooking time should not be accounted for)
    5. Use the metric system and Celcius
    6. For each instruction step create an appropriate headline and a short paragraph
    7. Notes for ingredients must be short
    8. For the list of cuisine types, include all relevant cuisines
    9. For the hashtags, try to use single words if possible, else user '-' to combine, always use capitalized words (e.g. Super-Sweet, Party-Food, Sharing-Plate)
    10. For the hashtags, do not repeat other properties already provided (such as cuisine type or cost)
    11. For expert level dishes, follow Michelin-star quality standards for: ingredient balance, texture combinations, flavor layering, presentation
    12. Amount field for ingredients must be a digit number with max. 2 decimal places
    13. Use the same language for all output fields including ingredient category, hashtags, category, diet, cuisine_types, and cooking_method
    14. Divide the dish in a reasonable number of components (e.g., 'Steak', 'Sauce', 'Roasted Potatoes')
    15. Provide ingredients for all components (e.g. 'Pasta' --> 250 g pasta, 1 tsp salt)
    16. Make sure to include all igredients for each component (i.e. including salt, spices, herbs etc.)
    17. If no diet restriction applicable: provide empty list

    Language: German

    VALIDATION REQUIREMENTS:
    1. Response MUST be complete, valid JSON
    2. ALL fields are required
    3. ALL arrays must have proper closing brackets
    4. ALL objects must have proper closing braces
    5. Response must end with proper closing brackets: {{}}]}}

    Example End Structure:
                        "hashtags": ["Tag1", "Tag2"]
                    }}
                ]
            }}

    Ensure the response includes these exact closing characters: {{}}]}}

    Return only the JSON, no other text."""

    return prompt


def create_recipe_prompt_by_description(recipe_description: str) -> str:
    prompt = f"""Given this recipe information:
    
    {recipe_description}

    Please create the corresponding recipe in the following exact JSON format, nothing else:

    {{
        "recipe": [
            {{
                "language": "en|de",  // Language code
                "title": string,      // Recipe title
                "difficulty": number, // 1=beginner, 2=advanced, 3=expert
                "times": [
                    {{"name": "time_1", "value": number}}, // e.g. preparation: 20
                    {{"name": "time_2", "value": number}}, // e.g. cooking time: 10
                ] // list of times necessary to spent for the dish (including cooling or resting time)
                "components": [
                    {{
                        "name": string, // name of the first component (e.g., 'Steak')
                        "ingredients": [
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
                        ] // list of the ingredients for the first component
                        }},
                    {{
                        "name": string, // name of the second component (e.g., 'Wine Sauce')
                        "ingredients": [
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
                        ] // list of the ingredients for the first component
                        }}
                ],
                "description": "A brief, appealing description of the dish.",
                "servings": number, // number of persons to serve with this recipe
                "instructions": {{
                    "headline step one": "description step one",
                    "headline step two": "description step two",
                }}
                "tips": [
                    "tip1",
                    "tip2"
                ]
                "storage": "string",
                "cuisine_type": ['cuisine_type_1', 'cuisine_type_2', ...],
                "equipment": ['equipment_1', 'equipment_2', ...],
                "category": "type of dish (e.g., 'Main course', 'Soup', or 'Dessert'),
                "diet": ["diet restriction one (e.g. 'Vegetarian')", "diet restriction two (e.g., 'Gluten-Free')"],
                "cooking_method": ["cooking method one (e.g. 'Grilling')", "cooking method two (e.g., 'Baking')"],
                "cost": "cost of the dish (use the numbers of the following mapping: 'budget'->1, 'moderate'->2, 'premium'->3)",
                "spiciness": "pungency level (use the numbers of the following mapping: 'not spicy'->0, 'mild'->1, 'medium'->2, 'hot'->3)",
                "beverage": {{
                    "name": string // name of the beverage (e.g., Chardonnay) // Beverage recommendation
                    "type": string // type of beverage (e.g., White Wine)
                }}
                "hashtags": ["hashtag one (e.g., 'Winter')", "hashtag two (e.g., 'Classic')", "hashtag three (e.g. Super-Sweet)", "hashtag four (e.g., Party-Food)", "hashtag five (e.g. Birthday)],
            }}
        ]
    }}

    Requirements:
    1. Response must be valid JSON
    2. Use only the provided ingredients
    3. Each recipe must be realistic and cookable
    4. Time specifications in number minutes; time values should add up to total time necessary (e.g. cutting ingredients during cooking time should not be accounted for)
    5. Use the metric system and Celcius
    6. For each instruction step create an appropriate headline and a short paragraph
    7. Notes for ingredients must be short
    8. For the list of cuisine types, include all relevant cuisines
    9. For the hashtags, try to use single words if possible, else user '-' to combine, always use capitalized words (e.g. Super-Sweet, Party-Food, Sharing-Plate)
    10. For the hashtags, do not repeat other properties already provided (such as cuisine type or cost)
    11. For expert level dishes, follow Michelin-star quality standards for: ingredient balance, texture combinations, flavor layering, presentation
    12. Amount field for ingredients must be a digit number with max. 2 decimal places
    13. Use the same language for all output fields including ingredient category, hashtags, category, diet, cuisine_types, and cooking_method
    14. Divide the dish in a reasonable number of components (e.g., 'Steak', 'Sauce', 'Roasted Potatoes')
    15. Provide ingredients for all components (e.g. 'Pasta' --> 250 g pasta, 1 tsp salt)
    16. Make sure to include all igredients for each component (i.e. including salt, spices, herbs etc.)
    17. If no diet restriction applicable: provide empty list

    Language: German

    VALIDATION REQUIREMENTS:
    1. Response MUST be complete, valid JSON
    2. ALL fields are required
    3. ALL arrays must have proper closing brackets
    4. ALL objects must have proper closing braces
    5. Response must end with proper closing brackets: {{}}]}}

    Example End Structure:
                        "hashtags": ["Tag1", "Tag2"]
                    }}
                ]
            }}

    Ensure the response includes these exact closing characters: {{}}]}}

    Return only the JSON, no other text."""

    return prompt



def create_recipe_prompt_by_preview(recipe_dict: dict) -> str:
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
                "language": "en|de",  // Language code
                "title": string,      // Recipe title
                "difficulty": number, // 1=beginner, 2=advanced, 3=expert
                "times": [
                    {{"name": "time_1", "value": number}}, // e.g. preparation: 20
                    {{"name": "time_2", "value": number}}, // e.g. cooking time: 10
                ] // list of times necessary to spent for the dish (including cooling or resting time)
                "components": [
                    {{
                        "name": string, // name of the first component (e.g., 'Steak')
                        "ingredients": [
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
                        ] // list of the ingredients for the first component
                        }},
                    {{
                        "name": string, // name of the second component (e.g., 'Wine Sauce')
                        "ingredients": [
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
                        ] // list of the ingredients for the first component
                        }}
                ],
                "description": "A brief, appealing description of the dish.",
                "servings": number, // number of persons to serve with this recipe
                "instructions": {{
                    "headline step one": "description step one",
                    "headline step two": "description step two",
                }}
                "tips": [
                    "tip1",
                    "tip2"
                ]
                "storage": "string",
                "cuisine_type": ['cuisine_type_1', 'cuisine_type_2', ...],
                "equipment": ['equipment_1', 'equipment_2', ...],
                "category": "type of dish (e.g., 'Main course', 'Soup', or 'Dessert'),
                "diet": ["diet restriction one (e.g. 'Vegetarian')", "diet restriction two (e.g., 'Gluten-Free')"],
                "cooking_method": ["cooking method one (e.g. 'Grilling')", "cooking method two (e.g., 'Baking')"],
                "cost": "cost of the dish (use the numbers of the following mapping: 'budget'->1, 'moderate'->2, 'premium'->3)",
                "spiciness": "pungency level (use the numbers of the following mapping: 'not spicy'->0, 'mild'->1, 'medium'->2, 'hot'->3)",
                "beverage": {{
                    "name": string // name of the beverage (e.g., Chardonnay) // Beverage recommendation
                    "type": string // type of beverage (e.g., White Wine)
                }}
                "hashtags": ["hashtag one (e.g., 'Winter')", "hashtag two (e.g., 'Classic')", "hashtag three (e.g. Super-Sweet)", "hashtag four (e.g., Party-Food)", "hashtag five (e.g. Birthday)],
            }}
        ]
    }}

    Requirements:
    1. Response must be valid JSON
    2. Use only the provided ingredients
    3. Each recipe must be realistic and cookable
    4. Time specifications in number minutes; time values should add up to total time necessary (e.g. cutting ingredients during cooking time should not be accounted for)
    5. Use the metric system and Celcius
    6. For each instruction step create an appropriate headline and a short paragraph
    7. Notes for ingredients must be short
    8. For the list of cuisine types, include all relevant cuisines
    9. For the hashtags, try to use single words if possible, else user '-' to combine, always use capitalized words (e.g. Super-Sweet, Party-Food, Sharing-Plate)
    10. For the hashtags, do not repeat other properties already provided (such as cuisine type or cost)
    11. For expert level dishes, follow Michelin-star quality standards for: ingredient balance, texture combinations, flavor layering, presentation
    12. Amount field for ingredients must be a digit number with max. 2 decimal places
    13. Use the same language for all output fields including ingredient category, hashtags, category, diet, cuisine_types, and cooking_method
    14. Divide the dish in a reasonable number of components (e.g., 'Steak', 'Sauce', 'Roasted Potatoes')
    15. Provide ingredients for all components (e.g. 'Pasta' --> 250 g pasta, 1 tsp salt)
    16. Make sure to include all igredients for each component (i.e. including salt, spices, herbs etc.)
    17. If no diet restriction applicable: provide empty list

    Language: German

    VALIDATION REQUIREMENTS:
    1. Response MUST be complete, valid JSON
    2. ALL fields are required
    3. ALL arrays must have proper closing brackets
    4. ALL objects must have proper closing braces
    5. Response must end with proper closing brackets: {{}}]}}

    Example End Structure:
                        "hashtags": ["Tag1", "Tag2"]
                    }}
                ]
            }}

    Ensure the response includes these exact closing characters: {{}}]}}

    Return only the JSON, no other text."""

    return prompt