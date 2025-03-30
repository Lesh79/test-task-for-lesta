import math

import pytest

from boat import Boat, Cargo, AnchorState


class TestBoatPassengers:
    @pytest.mark.parametrize("initial, addition, expected", [(0, 2, 2), (1, 3, 4)])
    def test_add_passenger_success(self, initial, addition, expected):
        boat = Boat(max_passengers=5, max_weight=200)
        boat.count_passengers = initial
        boat.add_passenger(addition)
        assert boat.count_passengers == expected

    @pytest.mark.parametrize(
        "initial, removal, error_msg",
        [
            (1, 2, "There are fewer people on board"),
            (0, 1, "There are fewer people on board"),
        ],
    )
    def test_remove_passenger_failure(self, initial, removal, error_msg):
        boat = Boat(max_passengers=5, max_weight=200)
        boat.count_passengers = initial
        with pytest.raises(ValueError, match=error_msg):
            boat.remove_passenger(removal)


class TestBoatCargo:
    @pytest.mark.parametrize(
        "current_weight, cargo_weight, expected_total", [(0, 50, 50), (20, 70, 90)]
    )
    def test_load_cargo_success(self, current_weight, cargo_weight, expected_total):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.current_weight = current_weight
        cargo = Cargo("cargo1", cargo_weight)
        boat.load_cargo(cargo)
        assert "cargo1" in boat.cargo_map
        assert boat.current_weight == expected_total

    @pytest.mark.parametrize(
        "current_weight, cargo_weight, error_msg", [(100, 150, "Too much cargo")]
    )
    def test_load_cargo_overweight(self, current_weight, cargo_weight, error_msg):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.current_weight = current_weight
        cargo = Cargo("cargo1", cargo_weight)
        with pytest.raises(ValueError, match=error_msg):
            boat.load_cargo(cargo)

    @pytest.mark.parametrize(
        "initial_weight, cargo_weight, error_msg",
        [(0, 50, "Cargo cargo1 already on board")],
    )
    def test_load_cargo_duplicate(self, initial_weight, cargo_weight, error_msg):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.current_weight = initial_weight
        cargo = Cargo("cargo1", cargo_weight)
        boat.load_cargo(cargo)
        with pytest.raises(ValueError, match=error_msg):
            boat.load_cargo(cargo)

    @pytest.mark.parametrize(
        "current_weight, cargo_weight, expected_total", [(50, 50, 0)]
    )
    def test_unload_cargo_success(self, current_weight, cargo_weight, expected_total):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.current_weight = current_weight
        cargo = Cargo("cargo1", cargo_weight)
        boat.cargo_map[cargo.id] = cargo
        boat.unload_cargo(cargo)
        assert cargo.id not in boat.cargo_map
        assert boat.current_weight == expected_total

    @pytest.mark.parametrize(
        "cargo_present, cargo_weight, error_msg",
        [(False, 50, "Cargo cargo1 not on board")],
    )
    def test_unload_cargo_not_found(self, cargo_present, cargo_weight, error_msg):
        boat = Boat(max_passengers=4, max_weight=200)
        cargo = Cargo("cargo1", cargo_weight)
        if cargo_present:
            boat.cargo_map[cargo.id] = cargo
        with pytest.raises(ValueError, match=error_msg):
            boat.unload_cargo(cargo)


class TestBoatAnchor:
    @pytest.mark.parametrize(
        "initial_anchor, method, final_anchor",
        [
            (AnchorState.UP, "drop_anchor", AnchorState.DOWN),
            (AnchorState.DOWN, "raise_anchor", AnchorState.UP),
        ],
    )
    def test_anchor_success(self, initial_anchor, method, final_anchor):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.anchor = initial_anchor
        if method == "drop_anchor":
            boat.drop_anchor()
        else:
            boat.raise_anchor()
        assert boat.anchor == final_anchor

    @pytest.mark.parametrize(
        "initial_anchor, method, error_msg",
        [
            (AnchorState.DOWN, "drop_anchor", "Anchor is already down"),
            (AnchorState.UP, "raise_anchor", "Anchor is already up"),
        ],
    )
    def test_anchor_failure(self, initial_anchor, method, error_msg):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.anchor = initial_anchor
        if method == "drop_anchor":
            with pytest.raises(ValueError, match=error_msg):
                boat.drop_anchor()
        else:
            with pytest.raises(ValueError, match=error_msg):
                boat.raise_anchor()


class TestBoatRowing:
    @pytest.mark.parametrize(
        "anchor_state, passengers, angle, speed, time_in_seconds, expected_x, expected_y, error_msg",
        [
            (
                AnchorState.UP,
                2,
                0,
                10,
                5,
                50,
                0,
                None,
            ),  # угол 0: смещение только по оси x
            (AnchorState.DOWN, 2, 0, 10, 5, None, None, "Anchor is down. Cannot row."),
            (AnchorState.UP, 0, 0, 10, 5, None, None, "There is no one to row"),
        ],
    )
    def test_rowing_to(
        self,
        anchor_state,
        passengers,
        angle,
        speed,
        time_in_seconds,
        expected_x,
        expected_y,
        error_msg,
    ):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.anchor = anchor_state
        boat.count_passengers = passengers
        if error_msg:
            with pytest.raises(ValueError, match=error_msg):
                boat.rowing_to(angle, speed, time_in_seconds)
        else:
            boat.rowing_to(angle, speed, time_in_seconds)
            assert math.isclose(boat.position[0], expected_x, rel_tol=1e-3)
            assert math.isclose(boat.position[1], expected_y, rel_tol=1e-3)


class TestIntegration:
    def test_integration_passengers_and_cargo(self):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.add_passenger(3)
        cargo = Cargo("cargo1", 80)
        boat.load_cargo(cargo)
        assert boat.count_passengers == 3
        assert boat.current_weight == 80
        assert "cargo1" in boat.cargo_map
        boat.unload_cargo(cargo)
        assert boat.current_weight == 0
        assert "cargo1" not in boat.cargo_map

    def test_integration_rowing_with_anchor_operations(self):
        boat = Boat(max_passengers=4, max_weight=200)
        boat.add_passenger(2)
        boat.rowing_to(angle=90, speed=5, time_in_seconds=10)
        pos1 = boat.position
        boat.drop_anchor()
        with pytest.raises(ValueError):
            boat.rowing_to(angle=0, speed=5, time_in_seconds=10)
        boat.raise_anchor()
        boat.rowing_to(angle=0, speed=5, time_in_seconds=10)
        assert boat.position != pos1


class TestSystem:
    def test_system_scenario(self):
        """
        Полный сценарий:
        1. Добавление пассажиров.
        2. Загрузка нескольких грузов.
        3. Опускание и поднятие якоря.
        4. Гребля в указанном направлении.
        5. Удаление пассажиров и разгрузка.
        """
        boat = Boat(max_passengers=4, max_weight=300)
        boat.add_passenger(2)
        assert boat.count_passengers == 2

        cargo1 = Cargo("cargo1", 100)
        cargo2 = Cargo("cargo2", 50)
        boat.load_cargo(cargo1)
        boat.load_cargo(cargo2)
        assert boat.current_weight == 150
        assert "cargo1" in boat.cargo_map
        assert "cargo2" in boat.cargo_map

        # Go to a point А
        boat.rowing_to(angle=0, speed=10, time_in_seconds=5)
        pos_after_first_row = boat.position

        boat.drop_anchor()
        with pytest.raises(ValueError):
            boat.rowing_to(angle=90, speed=10, time_in_seconds=5)
        boat.raise_anchor()

        boat.rowing_to(angle=90, speed=5, time_in_seconds=10)
        pos_after_second_row = boat.position

        boat.remove_passenger(1)
        boat.unload_cargo(cargo1)
        assert boat.count_passengers == 1
        assert "cargo1" not in boat.cargo_map
        assert boat.current_weight == 50

        assert pos_after_first_row != (0.0, 0.0)
        assert pos_after_second_row != pos_after_first_row
