import json
import os
import glob


class SaveSystem:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def save(self, world, slot=1):
        path = os.path.join(self.save_dir, f"slot_{slot}.json")
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(world.to_dict(), file, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
        return path

    def load(self, world, slot=1):
        path = os.path.join(self.save_dir, f"slot_{slot}.json")
        if not os.path.exists(path):
            return False, "Сохранение не найдено"
        try:
            with open(path, "r", encoding="utf-8") as file:
                world.from_dict(json.load(file))
            return True, f"Загружен слот {slot}"
        except (OSError, json.JSONDecodeError, KeyError) as error:
            return False, f"Ошибка загрузки: {error}"

    def slots(self):
        result = []
        for slot in range(1, 4):
            path = os.path.join(self.save_dir, f"slot_{slot}.json")
            result.append({"slot": slot, "exists": os.path.exists(path), "path": path})
        return result
