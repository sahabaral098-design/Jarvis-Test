import requests
import json
import subprocess

class Model:
    def __init__(self, models_config_path = "main/Models_config.json") -> None:
        # ---- Models config loading ----

        try:
            with open(models_config_path, "r") as f:
                models_config:dict = json.load(f) 
                if models_config: # To see if it even exists or just is there to make me scream
                    models_config = models_config.get("Models")  # type: ignore : pylance
                else:
                    print("`Models` configs not found")
                    exit(1)
                print(models_config)
        except (json.JSONDecodeError, Exception) as e:
            print(f"An error occured loading the Models config file: {e}")
            exit(1)

        # ---- Ollama setup ----

        subprocess.Popen(["ollama ", "serve"])

if __name__ == "__main__": # TEST
    test = Model()