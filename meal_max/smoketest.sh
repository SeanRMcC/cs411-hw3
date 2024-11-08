#!/bin/bash

BASE_URL="http://localhost:5000/api"

ECHO_JSON=false

while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Health checks

# Function to check the health of the service
check_health() {
    echo "Checking health status..."
    curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
    if [ $? -eq 0 ]; then
        echo "Service is healthy."
    else
        echo "Health check failed."
        exit 1
    fi
}

# Function to check the database connection
check_db() {
    echo "Checking database connection..."
    curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
    if [ $? -eq 0 ]; then
        echo "Database connection is healthy."
    else
        echo "Database check failed."
        exit 1
    fi
}

# Meal management

clear_catalog() {
    echo "Clearning the meals..."
    curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

add_meal() {
    meal=$1
    cuisine=$2
    price=$3
    difficulty=$4

    echo "Adding meal ($meal - $cuisine, price: $price, difficulty: $difficulty) to the meals table.."
    curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
        -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":\"$price\", \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

    if [ $? -eq 0 ]; then 
        echo "Meal added successfully."
    else
        echo "Failed to add song."
        exit 1
    fi
}

delete_meal() {
    meal_id=$1

    echo "Deleting meal by ID ($meal_id)..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal deleted successfully by ID ($meal_id)."
    else
        echo "Failed to delete meal by ID ($meal_id)."
        exit 1
    fi
}

get_meal_by_id() {
    meal_id=$1

    echo "Getting meal by ID ($meal_id)..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by ID ($meal_id)."
        if [ "$ECHO_JSON" = true ]; then 
            echo "Meal JSON (ID $meal_id):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get meal by ID ($meal_id)."
        exit 1
    fi
}

get_meal_by_name() {
    meal_name=$1

    echo "Getting meal by name ($meal_name)..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by name ($meal_name)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON (name $meal_name):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get meal by name ($meal_name)."
        exit 1
    fi
}

# Battle

battle() {
    echo "Starting a battle..."
    response=$(curl -s -X GET "$BASE_URL/battle")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Batle finished successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Battle results:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to run battle."
        exit 1
    fi
}

clear_combatants() {
    echo "Clearing combatants..."
    curl -s -X POST "$BASE_URL/clear-combatants" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Combatants cleared successfully."
    else
        echo "Failed to clear combatants."
        exit 1
    fi
}

get_combatants() {
    echo "Getting combatants..."
    response=$(curl -s -X GET "$BASE_URL/get-combatants")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Got combatants successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Combatants:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get combatants."
        exit 1
    fi
}

prep_combatant() {
    meal=$1

    echo "Prepping combatant ($meal)..."
    response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
        -H "Content-Type: application/json" \
        -d "{\"meal\":\"$meal\"}")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Prepped combatant ($meal) successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Combatants:"
            echo "$response" | jq .
        fi
    else 
        echo "Failed to prep combatant ($meal)."
        exit 1
    fi
}

# Leaderboard

get_leaderboard() {
    echo "Getting leaderboard..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Got leaderboard successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Leaderboard:"
            echo "$response" | jq .
        fi
    else 
        echo "Failed to get leaderboard."
        exit 1
    fi
}

# Health checks
check_health
check_db

# Meal management
add_meal "Pad Tai" "Tai" 10.0 "MED"
add_meal "Lasagna" "Italian" 13.0 "LOW"
add_meal "Pizza" "New York" 10 "HIGH"

delete_meal 2
get_meal_by_id 1
get_meal_by_name "Pizza"


# Battle
prep_combatant "Pad Tai"
prep_combatant "Pizza"
get_combatants
battle
clear_combatants

# Leaderboard
get_leaderboard

clear_catalog

echo "All tests passed successfully!"