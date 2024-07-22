from __future__ import annotations
from typing import Union
from dataclasses import dataclass
from enum import Enum, auto
from result import Result, Ok, Err

# Constants
CURRENT_YEAR = 2024  # Hardcoded for example; in practice, use datetime.now().year
CAR_EFFICIENCY_THRESHOLD_YEAR = 2000
CAR_OLD_EFFICIENCY_FACTOR = 0.9
MOTORBIKE_EFFICIENCY_THRESHOLD_YEAR = 2010
MOTORBIKE_OLD_EFFICIENCY_FACTOR = 0.95
MAX_LEAN_ANGLE = 45
STANDARD_RIDER_WEIGHT = 70  # kg
MAX_LEAN_ANGLE_FACTOR = 0.1


class InvalidValueError(ValueError):
    pass


def validate_positive(value: float, name: str) -> float:
    if value <= 0:
        raise InvalidValueError(f"{name} must be positive")
    return value


def validate_non_negative(value: float, name: str) -> float:
    if value < 0:
        raise InvalidValueError(f"{name} must be non-negative")
    return value


class Year:
    def __init__(self, value: int):
        if not 1900 <= value <= CURRENT_YEAR:
            raise InvalidValueError(f"Year must be between 1900 and {CURRENT_YEAR}")
        self.value = value


class Angle:
    def __init__(self, value: float):
        if not 0 <= value <= 360:
            raise InvalidValueError("Angle must be between 0 and 360 degrees")
        self.value = value


class VehicleError(Enum):
    UNKNOWN_VEHICLE_TYPE = auto()


class CarError(Enum):
    FAILED_INSPECTION = auto()


class BikeError(Enum):
    HELMET_NOT_WORN = auto()
    EXCESSIVE_LEAN_ANGLE = auto()


@dataclass(frozen=True)
class BaseVehicle:
    year: Year
    fuel_consumption: float  # LitersPer100Km
    distance: float  # Kilometers

    def __post_init__(self):
        validate_positive(self.fuel_consumption, "Fuel consumption")
        validate_non_negative(self.distance, "Distance")


@dataclass(frozen=True)
class Car(BaseVehicle):
    inspection_passed: bool


@dataclass(frozen=True)
class Motorbike(BaseVehicle):
    rider_weight: float  # Kilograms
    lean_angle: Angle
    helmet_worn: bool

    def __post_init__(self):
        super().__post_init__()
        validate_positive(self.rider_weight, "Rider weight")


Vehicle = Union[Car, Motorbike]


def calculate_car_distance(car: Car) -> Result[float, CarError]:
    match car:
        case Car(inspection_passed=False):
            return Err(CarError.FAILED_INSPECTION)
        case Car(year=year, fuel_consumption=fc, distance=d):
            efficiency_factor = CAR_OLD_EFFICIENCY_FACTOR if year.value < CAR_EFFICIENCY_THRESHOLD_YEAR else 1.0
            max_distance = (d / (fc / 100)) * efficiency_factor
            return Ok(max_distance)


def calculate_motorbike_distance(motorbike: Motorbike) -> Result[float, BikeError]:
    match motorbike:
        case Motorbike(helmet_worn=False):
            return Err(BikeError.HELMET_NOT_WORN)
        case Motorbike(lean_angle=lean_angle) if lean_angle.value > MAX_LEAN_ANGLE:
            return Err(BikeError.EXCESSIVE_LEAN_ANGLE)
        case Motorbike(year=year, fuel_consumption=fc, distance=d, rider_weight=rw, lean_angle=lean_angle):
            base_distance = d / (fc / 100)
            weight_factor = 1 - (rw - STANDARD_RIDER_WEIGHT) / 1000
            lean_factor = 1 + (lean_angle.value / 90) * MAX_LEAN_ANGLE_FACTOR
            year_factor = MOTORBIKE_OLD_EFFICIENCY_FACTOR if year.value < MOTORBIKE_EFFICIENCY_THRESHOLD_YEAR else 1.0
            max_distance = base_distance * weight_factor * lean_factor * year_factor
            return Ok(max_distance)


def calculate_distance(vehicle: Vehicle) -> Result[float, Union[VehicleError, CarError, BikeError]]:
    match vehicle:
        case Car():
            return calculate_car_distance(vehicle)
        case Motorbike():
            return calculate_motorbike_distance(vehicle)
        case _:
            return Err(VehicleError.UNKNOWN_VEHICLE_TYPE)


def find_best_vehicle(vehicle1: Vehicle, vehicle2: Vehicle) -> Result[Vehicle, str]:
    result1 = calculate_distance(vehicle1)
    result2 = calculate_distance(vehicle2)

    match (result1, result2):
        case (Ok(distance1), Ok(distance2)):
            if distance1 > distance2:
                return Ok(vehicle1)
            elif distance2 > distance1:
                return Ok(vehicle2)
            else:
                return Ok(vehicle1)  # Arbitrarily choose vehicle1 if distances are equal
        case (Ok(_), Err(_)):
            return Ok(vehicle1)
        case (Err(_), Ok(_)):
            return Ok(vehicle2)
        case (Err(error1), Err(error2)):
            return Err(f"Both vehicles have errors: {error1.name}, {error2.name}")
        case _:
            return Err("Unexpected error occurred during comparison")


def print_result(vehicle_type: str, result: Result[float, Union[VehicleError, CarError, BikeError]]) -> None:
    match result:
        case Ok(distance):
            print(f"{vehicle_type} distance: {distance:.2f} km")
        case Err(error):
            print(f"{vehicle_type} error: {error.name}")


def main() -> None:
    try:
        vehicles: list[Vehicle] = [
            Car(Year(2020), 5, 100, True),
            Car(Year(1995), 7, 100, True),
            Car(Year(2022), 6, 100, False),
            Motorbike(Year(2020), 3, 100, 70, Angle(30), True),
            Motorbike(Year(2005), 4, 100, 90, Angle(20), True),
            Motorbike(Year(2023), 2, 100, 60, Angle(50), False)
        ]

        for vehicle in vehicles:
            result = calculate_distance(vehicle)
            print_result(type(vehicle).__name__, result)

        # Example of using find_best_vehicle
        car = Car(Year(2020), 5, 100, True)
        bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), True)
        best_vehicle_result = find_best_vehicle(car, bike)

        match best_vehicle_result:
            case Ok(best_vehicle):
                print(f"\nBest vehicle is: {type(best_vehicle).__name__}")
                distance_result = calculate_distance(best_vehicle)
                match distance_result:
                    case Ok(distance):
                        print(f"It can travel {distance:.2f} km")
                    case Err(error):
                        print(f"Error calculating distance: {error.name}")
            case Err(error_message):
                print(f"Error finding best vehicle: {error_message}")

    except InvalidValueError as e:
        print(f"Error creating vehicle: {e}")
