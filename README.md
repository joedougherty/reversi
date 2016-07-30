# reversi game tree generation #

So you'd like to play around a bit with generating game trees? Very good!

`gameanalysis.py` should include enough to get you creating your own game trees. 

`midas.py` contains game tree creation/manipulation functions. Feel free to start at the bottom by reading `simulate_turns`: this ought to show how a game tree is generated.

## Notes ## 

**Create a new game tree for each experminent**:

If you're going to create a number of game trees, you'll need to start with a new `game_tree = Node(Board(), parent=None)` each time. The game trees themselves are passed around by reference. Technically, some of the `return` statements are not required (ex: `add_level_to_game_tree`), though I've included them regardless. 

**Be careful with the num_of_turns argument in `simulate_turns'**:

I've only been able to successfully simulate 4 turns (from the opening board). On my machine, this takes ~45 seconds. Setting `num_of_turns` > 4 could probably pin a core. By the time a mere 4 turns have been simluated, there are already 390,216 possible resutling boards (if you believe my code is correct). It's a complex game!
