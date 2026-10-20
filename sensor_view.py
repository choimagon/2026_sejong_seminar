"""Open Controls first, then select any sensor present in the chosen XML."""

from module import sensor


if __name__ == "__main__":
    sensor.view("all")
