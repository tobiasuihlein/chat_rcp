from django.shortcuts import render, redirect
from django.urls import reverse
from .utils.claude import *
from .utils.helpers import sort_previews

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
    
    recipe_previews["recipes"] = sort_previews(recipe_previews["recipes"])

    ingredients = ["bell pepper", "feta cheese", "pasta", "rice", "parseley", "sage", "broccoli", "cream", "parmesan", "old bread", "red lentils"]
    context = {"recipe_previews": recipe_previews["recipes"], "ingredients": ingredients}
    return render(request, 'generator/previews.html', context=context)


def previews(request):

    if request.method == "POST":
    
        #ingredients = ["bell pepper", "feta cheese", "pasta", "rice", "parsley", "sage", "broccoli", "cream", "parmesan", "old bread", "red lentils"]
        ingredients = request.POST.get("ingredients-input").split(',')
        staples = [""]
    
        prompt = create_previews_prompt(ingredients, staples)
        previews = get_previews_from_claude(prompt)
    
        previews["recipes"] = sort_previews(previews["recipes"])

        print(previews["recipes"])

        context = {"recipe_previews": previews["recipes"], "ingredients": ingredients}
        return render(request, 'generator/previews.html', context=context)
    
    return render(request, 'generator/index.html')


def home(request):
    return render(request, 'generator/index.html')


def recipe_mockup(request):

    recipe = [
    {'title': 'Parmesan Broccoli Pasta', 'difficulty': 'Medium', 'time': {'total': '25 Min.', 'preparation': '10 Min.', 'cooking': '15 Min.'}, 'main_ingredients': ['pasta', 'broccoli', 'parmesan', 'cream', 'parsley'], 'additional_ingredients': ['olive oil', 'garlic', 'salt', 'pepper', 'butter'], 'description': 'Creamy pasta with tender broccoli florets and rich parmesan sauce. Fresh parsley adds a burst of color and flavor to this comforting dish that perfectly combines vegetables with indulgent cheese.', 'number_of_persons': 4, 'instructions': {'step1': ['Bring a large pot of salted water to a boil. Cook the pasta according to package instructions until al dente. Drain and set aside.', 'In a large skillet, heat the olive oil over medium heat. Add the minced garlic and sauté for 1-2 minutes until fragrant.', 'Add the broccoli florets to the skillet and season with salt and pepper. Sauté for 5-7 minutes, or until the broccoli is tender.'], 'step2': ['Reduce the heat to low and add the heavy cream to the skillet. Stir in the grated parmesan cheese until the sauce is creamy and smooth.', 'Add the cooked pasta to the skillet and toss to coat everything evenly with the parmesan sauce.', 'Garnish with fresh chopped parsley before serving.']}, 'tips': ['Use freshly grated parmesan cheese for the best flavor.', 'For extra creaminess, add a tablespoon of butter to the sauce.'], 'storage': 'This dish is best served immediately, but leftovers can be stored in an airtight container in the refrigerator for up to 3 days.'}
    ]
    context = {"recipe": recipe[0]}

    return render(request, 'generator/recipe.html', context=context)

def recipe(request):

    if request.method == "POST":
        try:
            recipe_dict = request.POST.dict()
            prompt = create_recipe_prompt(recipe_dict)
            recipe = get_recipe_from_claude(prompt)
            context = {"recipe": recipe["recipe"][0]}
            return render(request, 'generator/recipe.html', context=context)
        except Exception as e:
            print(f"Error: {e}")
            print("no recipe data provided")
            return redirect('generator:home')
    
    return redirect('generator:home')