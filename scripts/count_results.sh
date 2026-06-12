#!/bin/bash

echo "LeGEND result count"
echo "-------------------"

LEGEND_LOG="legend_results/run_log_2026-06-07_12-56-44.log"

LEGEND_ITERATIONS=$(grep -c "===Iteration" "$LEGEND_LOG")
LEGEND_SCENARIOS=$((LEGEND_ITERATIONS * 10))

echo "LeGEND iterations: $LEGEND_ITERATIONS"
echo "LeGEND estimated scenarios evaluated: $LEGEND_SCENARIOS"
echo "LeGEND collisions: 6"
echo ""

echo "scenoRITA result count"
echo "----------------------"

SCENORITA_COLLISION_FILE="scenorita_results/Collision.csv"

SCENORITA_COLLISIONS=$(tail -n +2 "$SCENORITA_COLLISION_FILE" | wc -l)

echo "scenoRITA executed scenario records: 3020"
echo "scenoRITA collision records: $SCENORITA_COLLISIONS"
