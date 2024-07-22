import pytest
from result import Ok, Err
from technical_test_fortis.vehicle import (  # Replace 'your_module_name' with the actual module name
    Year, Angle, Car, Motorbike, Vehicle,
    VehicleError, CarError, BikeError,
    calculate_distance, find_best_vehicle, InvalidValueError,
    CURRENT_YEAR, MAX_LEAN_ANGLE,
    CAR_EFFICIENCY_THRESHOLD_YEAR, CAR_OLD_EFFICIENCY_FACTOR,
    MOTORBIKE_EFFICIENCY_THRESHOLD_YEAR, MOTORBIKE_OLD_EFFICIENCY_FACTOR
)

# Test Year and Angle classes
def test_valid_year():
    assert Year(2000).value == 2000

def test_invalid_year():
    with pytest.raises(InvalidValueError):
        Year(CURRENT_YEAR + 1)
    with pytest.raises(InvalidValueError):
        Year(1899)

def test_valid_angle():
    assert Angle(45).value == 45

def test_invalid_angle():
    with pytest.raises(InvalidValueError):
        Angle(-1)
    with pytest.raises(InvalidValueError):
        Angle(361)

# Test vehicle creation
def test_valid_car_creation():
    car = Car(Year(2020), 5, 100, True)
    assert car.year.value == 2020
    assert car.fuel_consumption == 5
    assert car.distance == 100
    assert car.inspection_passed == True

def test_invalid_car_creation():
    with pytest.raises(InvalidValueError):
        Car(Year(2020), -5, 100, True)
    with pytest.raises(InvalidValueError):
        Car(Year(2020), 5, -100, True)

def test_valid_motorbike_creation():
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), True)
    assert bike.year.value == 2020
    assert bike.fuel_consumption == 3
    assert bike.distance == 100
    assert bike.rider_weight == 70
    assert bike.lean_angle.value == 30
    assert bike.helmet_worn == True

def test_invalid_motorbike_creation():
    with pytest.raises(InvalidValueError):
        Motorbike(Year(2020), 3, 100, -70, Angle(30), True)

# Test calculate_distance function
def test_calculate_car_distance():
    car = Car(Year(2020), 5, 100, True)
    result = calculate_distance(car)
    assert isinstance(result, Ok)
    actual = result.unwrap()
    assert pytest.approx(actual, 0.01) == 2000

def test_calculate_car_distance_failed_inspection():
    car = Car(Year(2020), 5, 100, False)
    result = calculate_distance(car)
    assert isinstance(result, Err)
    assert result.unwrap_err() == CarError.FAILED_INSPECTION

def test_calculate_old_car_distance():
    old_car = Car(Year(CAR_EFFICIENCY_THRESHOLD_YEAR - 1), 5, 100, True)
    result = calculate_distance(old_car)
    assert isinstance(result, Ok)
    assert pytest.approx(result.unwrap(), 0.01) == 2000 * CAR_OLD_EFFICIENCY_FACTOR

def test_calculate_motorbike_distance():
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), True)
    result = calculate_distance(bike)
    assert isinstance(result, Ok)
    assert result.unwrap() > 3333  # Basic sanity check

def test_calculate_motorbike_distance_no_helmet():
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), False)
    result = calculate_distance(bike)
    assert isinstance(result, Err)
    assert result.unwrap_err() == BikeError.HELMET_NOT_WORN

def test_calculate_motorbike_distance_excessive_lean():
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(MAX_LEAN_ANGLE + 1), True)
    result = calculate_distance(bike)
    assert isinstance(result, Err)
    assert result.unwrap_err() == BikeError.EXCESSIVE_LEAN_ANGLE

def test_calculate_old_motorbike_distance():
    old_bike = Motorbike(Year(MOTORBIKE_EFFICIENCY_THRESHOLD_YEAR - 1), 3, 100, 70, Angle(30), True)
    old_result = calculate_distance(old_bike)
    new_bike = Motorbike(Year(MOTORBIKE_EFFICIENCY_THRESHOLD_YEAR + 1), 3, 100, 70, Angle(30), True)
    new_result = calculate_distance(new_bike)
    assert isinstance(old_result, Ok) and isinstance(new_result, Ok)
    assert old_result.unwrap() < new_result.unwrap()

# Test find_best_vehicle function
def test_find_best_vehicle_car_wins():
    car = Car(Year(2020), 5, 100, True)
    bike = Motorbike(Year(2020), 6, 100, 70, Angle(30), True)
    result = find_best_vehicle(car, bike)
    assert isinstance(result, Ok)
    assert isinstance(result.unwrap(), Car)

def test_find_best_vehicle_bike_wins():
    car = Car(Year(2020), 6, 100, True)
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), True)
    result = find_best_vehicle(car, bike)
    assert isinstance(result, Ok)
    assert isinstance(result.unwrap(), Motorbike)

def test_find_best_vehicle_one_error():
    car = Car(Year(2020), 5, 100, False)  # Failed inspection
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), True)
    result = find_best_vehicle(car, bike)
    assert isinstance(result, Ok)
    assert isinstance(result.unwrap(), Motorbike)


def test_find_best_vehicle_both_errors():
    car = Car(Year(2020), 5, 100, False)  # Failed inspection
    bike = Motorbike(Year(2020), 3, 100, 70, Angle(30), False)  # No helmet
    result = find_best_vehicle(car, bike)
    assert isinstance(result, Err)
    assert "Both vehicles have errors" in result.unwrap_err()

# Test edge cases
#def test_unknown_vehicle_type():
#    class UnknownVehicle(Vehicle):
        #pass
#    unknown = UnknownVehicle()  # type: ignore
#    result = calculate_distance(unknown)
#    assert isinstance(result, Err)
#    assert result.unwrap_err() == VehicleError.UNKNOWN_VEHICLE_TYPE

def test_motorbike_weight_factor():
    light_bike = Motorbike(Year(2020), 3, 100, 60, Angle(30), True)
    heavy_bike = Motorbike(Year(2020), 3, 100, 80, Angle(30), True)
    light_result = calculate_distance(light_bike)
    heavy_result = calculate_distance(heavy_bike)
    assert isinstance(light_result, Ok) and isinstance(heavy_result, Ok)
    assert light_result.unwrap() > heavy_result.unwrap()

def test_motorbike_lean_angle_factor():
    no_lean_bike = Motorbike(Year(2020), 3, 100, 70, Angle(0), True)
    max_lean_bike = Motorbike(Year(2020), 3, 100, 70, Angle(MAX_LEAN_ANGLE), True)
    no_lean_result = calculate_distance(no_lean_bike)
    max_lean_result = calculate_distance(max_lean_bike)
    assert isinstance(no_lean_result, Ok) and isinstance(max_lean_result, Ok)
    assert no_lean_result.unwrap() < max_lean_result.unwrap()