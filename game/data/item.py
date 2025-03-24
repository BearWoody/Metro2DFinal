from enum import Enum

from game.tools import colors


class Item(Enum):
    FILTER = {
        "name": "Filter",
        "color": colors.GREEN
    }

    MEDKIT = {
        "name": "Med Kit",
        "color": colors.RED
    }

    def get_name(self):
        return self.value.get("name", "Unknown Item")

    def get_color(self):
        return self.value.get("color", colors.GRAY)