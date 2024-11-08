import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_battle(mocker):
    """Mock the battle function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.BattleModel.battle")

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

@pytest.fixture
def sample_battle_small(sample_meal1):
    return [sample_meal1]

##################################################
# Battle Combatants Test Cases
##################################################

def test_too_few_combatants(battle_model, sample_battle_small):
    """Test error when too few meals are in a battle list of combatants."""
    battle_model.combatants.extend(sample_battle_small)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
            battle_model.battle()

def test_battle(battle_model, sample_battle, mock_battle):
    """Test that battle function successfully returns a winning meal"""
    battle_model.combatants.extend(sample_battle)

    winner = battle_model.battle()
    assert winner, "Expected a winner to be returned"
    mock_battle.assert_called_once()

def test_update_meal_stats_called(battle_model, sample_battle, mocker):
    """Test that update_meal_stats is called with correct arguments for winner and loser."""
    mock_update_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")
    battle_model.combatants.extend(sample_battle)
    battle_model.battle()
    
    # Check update_meal_stats called twice, once for each combatant
    assert mock_update_stats.call_count == 2
    mock_update_stats.assert_any_call(sample_battle[0].id, 'win')
    mock_update_stats.assert_any_call(sample_battle[1].id, 'loss')

##################################################
# Remove Combatants Test Cases
##################################################

def test_clear_combatants(battle_model, sample_battle):
    """Test clearing the combatants list."""
    battle_model.combatants.extend(sample_battle)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_clear_combatants_multiple_times(battle_model, sample_battle):
    """Test clearing an empty combatants list."""
    battle_model.combatants.extend(sample_battle)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after initial clear"
    battle_model.clear_combatants()  
    assert len(battle_model.combatants) == 0, "List should remain empty after second clear"

##################################################
# Combatants Score Test Cases
##################################################

def test_get_battle_score(battle_model, sample_battle, sample_meal1):
     """Test that battle score function returns the correct score"""
     battle_model.combatants.extend(sample_battle)

     score = battle_model.get_battle_score(sample_meal1)
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
# Prep Combatant Test Cases
##################################################

def test_too_many_combatants(battle_model, sample_battle, sample_meal3):
    """Test error from adding a meal to a full battle list."""
    battle_model.combatants.extend(sample_battle)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
            battle_model.prep_combatant(sample_meal3)

def test_prep_one_combatant(battle_model, sample_meal1):
    """Test successfully adding a meal to the combatant list of a battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].id == 1

def test_prep_two_combatants(battle_model, sample_meal1, sample_meal2):
    """Test successfully adding two meals to the combatant list of a battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[0].id == 1
    assert battle_model.combatants[1].id == 2

def test_prep_same_combatant_twice(battle_model, sample_meal1):
    """Test adding the same meal twice to the combatant list of a battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[0].id == 1
    assert battle_model.combatants[1].id == 1