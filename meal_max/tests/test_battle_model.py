import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 12.0, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 3.5, 'HIGH')

@pytest.fixture
def sample_meal3():
    return Meal(3, 'Meal 3', 'Cuisine 3', 7, 'MED')

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

##################################################
# Battle Combatants Test Cases
##################################################

def test_too_few_combatants(battle_model, sample_battle):
    """Test error when too few meals are in a battle list of combatants."""
    battle_model.combatants.extend(sample_battle)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
            battle_model.battle()

def test_battle(battle_model, sample_battle):
     """Test that battle function successfully returns a winning meal"""
     battle_model.combatants.extend(sample_battle)

     winner = battle_model.battle()
     assert type(winner) == Meal

##################################################
# Remove Combatants Test Cases
##################################################

def test_clear_combatants(battle_model, sample_battle):
    """Test clearing the combatants list."""
    battle_model.combatants.extend(sample_battle)

    battle_model.clear_combatants()
    assert len(battle_model.playlist) == 0, "Combatants list should be empty after clearing"

##################################################
# Combatants Score Test Cases
##################################################

def test_get_battle_score(battle_model, sample_battle):
     """Test that battle score function returns the correct score"""
     battle_model.combatants.extend(sample_battle)

     score = battle_model.get_battle_score()
     assert score == 105 # (12 * 9) - 3 for meal 1

##################################################
# Combatants Retrieval Test Cases
##################################################

def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving all comabtants from the battle."""
    battle_model.combatants.extend(sample_battle)

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

##################################################
# Prep Combatants Test Cases
##################################################

def test_too_many_combatants(battle_model, sample_battle, sample_meal3):
    """Test error from adding a meal to a full battle list."""
    battle_model.combatants.extend(sample_battle)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
            battle_model.prep_combatants(sample_meal3)

def test_prep_one_combatant(battle_model, sample_meal1):
    """Test successfully adding a meal to the combatant list of a battle."""
    battle_model.prep_combatants(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].id == 1

def test_prep_two_combatants(battle_model, sample_meal1, sample_meal2):
    """Test successfully adding two meals to the combatant list of a battle."""
    battle_model.prep_combatants(sample_meal1)
    battle_model.prep_combatants(sample_meal2)
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[0].id == 1
    assert battle_model.combatants[1].id == 2