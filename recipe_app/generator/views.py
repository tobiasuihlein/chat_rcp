from django.shortcuts import render

def generator(request):
    recipe_previews = {
        "recipes": [
            {
                "title": "Peppered Feta Pasta",
                "difficulty": "Easy",
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
                "difficulty": "Easy",
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
    ingredients = ["bell pepper", "feta cheese", "pasta", "rice", "parseley", "sage", "broccoli", "cream", "parmesan", "old bread", "red lentils"]
    context = {"recipe_previews": recipe_previews["recipes"], "ingredients": ingredients}
    return render(request, 'generator/index.html', context = context)
