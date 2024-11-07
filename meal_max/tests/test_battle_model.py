import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

#@pytest.fixture
#def mock_update_play_count(mocker):
    #"""Mock the update_play_count function for testing purposes."""
    #return mocker.patch("music_collection.models.playlist_model.update_play_count")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 12.0, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 3.5, 'HIGH')

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

# need tests for battle(), clear_combatants(), get_battle_score(),
# get_combatants(), and prep_coombatants