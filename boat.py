import math
from enum import Enum
import time
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class Cargo:
    def __init__(self, cargo_id: str, weight: int):
        self.weight = weight
        self.id = cargo_id

    def __str__(self):
        return f"Груз {self.id} весом {self.weight} кг"


class AnchorState(Enum):
    UP = "up"
    DOWN = "down"


class Boat:
    def __init__(self, max_passengers: int, max_weight: int):
        self.max_passengers = max_passengers
        self.max_weight = max_weight
        self.anchor = AnchorState.UP
        self.count_passengers = 0
        self.current_weight = 0
        self.direction = 0  # угол в градусах, где 0 – например, восток
        self.current_speed = 0
        self.position = (0.0, 0.0)
        self.cargo_map = {}

    def add_passenger(self, quantity: int):
        if self.count_passengers + quantity <= self.max_passengers:
            self.count_passengers += quantity
            # time.sleep(quantity)
            logger.info(f"Added {quantity} passengers")
        else:
            raise ValueError("Too many passengers")

    def remove_passenger(self, quantity: int):
        if self.count_passengers - quantity >= 0:
            self.count_passengers -= quantity
            # time.sleep(quantity)
            logger.info(f"Removed {quantity} passengers")
        else:
            raise ValueError("There are fewer people on board")

    def load_cargo(self, cargo: Cargo):
        if self.current_weight + cargo.weight > self.max_weight:
            raise ValueError("Too much cargo")
        if cargo.id in self.cargo_map:
            raise ValueError(f"Cargo {cargo.id} already on board")
        self.cargo_map[cargo.id] = cargo
        self.current_weight += cargo.weight
        # time.sleep(cargo.weight // 20)
        logger.info(f"Cargo {cargo.id} loaded.")

    def unload_cargo(self, cargo: Cargo):
        if cargo.id not in self.cargo_map:
            raise ValueError(f"Cargo {cargo.id} not on board")
        self.current_weight -= cargo.weight
        self.cargo_map.pop(cargo.id)
        # time.sleep(cargo.weight // 20)
        logger.info(f"Cargo {cargo.id} unloaded.")

    def drop_anchor(self):
        if self.anchor == AnchorState.DOWN:
            raise ValueError("Anchor is already down")
        # time.sleep(2)
        self.anchor = AnchorState.DOWN
        logger.info("Anchor dropped.")

    def raise_anchor(self):
        if self.anchor == AnchorState.UP:
            raise ValueError("Anchor is already up")
        # time.sleep(5)
        self.anchor = AnchorState.UP
        logger.info("Anchor raised.")

    def rowing_to(self, angle: float, speed: int, time_in_seconds: int):
        if self.anchor != AnchorState.UP:
            raise ValueError("Anchor is down. Cannot row.")
        if self.count_passengers <= 0:
            raise ValueError("There is no one to row")

        self.direction = angle
        self.current_speed = speed

        distance = self.current_speed * time_in_seconds
        rad_angle = math.radians(angle)
        delta_x = distance * math.cos(rad_angle)
        delta_y = distance * math.sin(rad_angle)
        new_x = self.position[0] + delta_x
        new_y = self.position[1] + delta_y
        self.position = (new_x, new_y)
        # time.sleep(time_in_seconds)
        logger.info(f"Rowing complete. New position: {self.position}")


# Пример использования:
boat = Boat(max_passengers=4, max_weight=200)
boat.add_passenger(2)
cargo1 = Cargo("cargo1", 100)
cargo2 = Cargo("cargo2", 1010)
boat.load_cargo(cargo1)
boat.unload_cargo(cargo1)
boat.drop_anchor()
boat.raise_anchor()
boat.rowing_to(45, 10, 30)
