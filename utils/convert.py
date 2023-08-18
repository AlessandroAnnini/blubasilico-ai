import os
import json


def convert(folder_name):
    for filename in os.listdir(folder_name):
        if filename.endswith(".json"):
            with open(f"{folder_name}/{filename}", "r") as f:
                recipe = f.read()
                recipe = json.loads(recipe)
                recipe.pop("imageBase64", None)
                with open(f"{folder_name}/{filename}", "w") as f:
                    f.write(json.dumps(recipe))


if __name__ == "__main__":
    try:
        convert("recipes")
    except Exception as e:
        print("Fatal Error!")
        print(e)
