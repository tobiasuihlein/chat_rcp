from django.shortcuts import render
from dotenv import load_dotenv
import anthropic
import os

def previews_mockup(request):
    recipe_previews = {
        "recipes": [
            {
                "title": "Peppered Feta Pasta",
                "difficulty": "Hard",
                "time": "20 Min.",
                "additional_ingredients": [
                    "olive oil",
                    "garlic",
                    "salt",
                    "pepper"
                ],
                "description": "Al dente pasta tossed with sautéed bell peppers and melted feta cheese, creating a perfect balance of fresh and savory flavors. This colorful dish combines the sweetness of peppers with the tangy richness of feta, all brought together with aromatic garlic and fresh parsley.",
                "main_ingredients": [
                    "bell pepper",
                    "feta cheese",
                    "pasta",
                    "parsley"
                ]
            },
            {
                "title": "Parmesan Broccoli Pasta",
                "difficulty": "Medium",
                "time": "25 Min.",
                "additional_ingredients": [
                    "olive oil",
                    "garlic",
                    "salt",
                    "pepper",
                    "butter"
                ],
                "description": "Creamy pasta with tender broccoli florets and rich parmesan sauce. Fresh parsley adds a burst of color and flavor to this comforting dish that perfectly combines vegetables with indulgent cheese.",
                "main_ingredients": [
                    "pasta",
                    "broccoli",
                    "parmesan",
                    "cream",
                    "parsley"
                ]
            },
            {
                "title": "Red Lentil Rice Bowl",
                "difficulty": "Easy",
                "time": "30 Min.",
                "additional_ingredients": [
                    "olive oil",
                    "garlic",
                    "salt",
                    "pepper",
                    "vegetable stock"
                ],
                "description": "A hearty combination of fluffy rice and perfectly spiced red lentils, topped with crispy sage leaves. Bell peppers add a sweet crunch, while fresh parsley brings brightness to this nutritious meal.",
                "main_ingredients": [
                    "red lentils",
                    "rice",
                    "bell pepper",
                    "sage",
                    "parsley"
                ]
            }
        ]
    }

    def sort_previews(previews: dict) -> dict:

        difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}

        sorted_previews = sorted(
            previews,
            key = lambda x: difficulty_order.get(x["difficulty"], 999) # 999 is default value in case of error
        )

        return sorted_previews
    
    recipe_previews["recipes"] = sort_previews(recipe_previews["recipes"])

    ingredients = ["bell pepper", "feta cheese", "pasta", "rice", "parseley", "sage", "broccoli", "cream", "parmesan", "old bread", "red lentils"]
    context = {"recipe_previews": recipe_previews["recipes"], "ingredients": ingredients}
    return render(request, 'generator/previews.html', context = context)

def previews(request):

    if request.method == "POST":

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

            import json
            try:
                answer = json.loads(message.content[0].text)
                return answer
            except json.JSONDecodeError:
                raise ValueError("Sorry, something went wrong, chef.")
        
    
        #ingredients = ["bell pepper", "feta cheese", "pasta", "rice", "parsley", "sage", "broccoli", "cream", "parmesan", "old bread", "red lentils"]
        ingredients = request.POST.get("ingredients-input").split(',')
        staples = [""]
    
        prompt = create_previews_prompt(ingredients, staples)
        previews = get_previews_from_claude(prompt)

        def sort_previews(previews: dict) -> dict:

            difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}

            sorted_previews = sorted(
                previews,
                key = lambda x: difficulty_order.get(x["difficulty"], 999) # 999 is default value in case of error
            )

            return sorted_previews
    
        previews["recipes"] = sort_previews(previews["recipes"])

        context = {"recipe_previews": previews["recipes"], "ingredients": ingredients}
        return render(request, 'generator/previews.html', context=context)
    
    return render(request, 'generator/index.html')



def home(request):

    return render(request, 'generator/index.html')
