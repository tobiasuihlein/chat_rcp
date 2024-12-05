def sort_previews(previews: dict) -> dict:

    difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}

    sorted_previews = sorted(
        previews,
        key = lambda x: difficulty_order.get(x["difficulty"], 999) # 999 is default value in case of error
    )

    return sorted_previews
