"""TurtleBot-style driving: W/S forward/backward, Q/E left/right."""

from module import move


move.view("all")

# To execute a sequence instead:
# move.view("all", commands=["forward 0.3", "rotate 90", "backward 0.2"])
