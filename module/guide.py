"""The initial Controls tab: keyboard guide and distance/angle command entry."""

import mujoco

from .motion.commands import FORWARD_SPEED, TURN_SPEED
from .motion.speed import angular_speed


def guide_layout(width):
    """Click rectangles in logical pixels, with the origin at the top left."""
    return {"entry": (24, 376, width - 176, 46), "submit": (width - 140, 376, 116, 46)}


def contains(rect, x, y):
    left, top, width, height = rect
    return left <= x < left + width and top <= y < top + height


def draw_guide(width, height, scale, context, latest, entry, editing, message, *, motor_speed=FORWARD_SPEED,
               playback_controls=False):
    font = mujoco.mjtFont.mjFONT_NORMAL

    def rect(box):
        x, y, w, h = box
        return mujoco.MjrRect(int(x * scale), int((height - y - h) * scale), int(w * scale), int(h * scale))

    def text(box, caption, values=""):
        mujoco.mjr_overlay(font, mujoco.mjtGridPos.mjGRID_TOPLEFT, rect(box), caption, values, context)

    text((24, 136, width - 48, 40), "KEYBOARD DRIVING\nClick this window, then hold W / S / Q / E.")
    turn_speed = angular_speed(motor_speed)
    cards = (("W", "Forward", f"max {motor_speed:g} m/s"), ("S", "Backward", f"max {motor_speed:g} m/s"),
             ("Q", "Turn left", f"max {turn_speed:.2g} rad/s"), ("E", "Turn right", f"max {turn_speed:.2g} rad/s"))
    card_width = (width - 72) / 4
    for index, (key, action, speed) in enumerate(cards):
        x = 24 + index * (card_width + 8)
        mujoco.mjr_rectangle(rect((x, 182, card_width, 88)), 0.12, 0.16, 0.21, 1)
        mujoco.mjr_label(rect((x + 10, 194, 42, 46)), font, key,
                         0.13, 0.34, 0.58, 1, 1, 1, 1, context)
        text((x + 62, 194, card_width - 70, 58), f"{action}\n{speed}")
    if playback_controls:
        text((24, 282, width - 48, 52),
             "F: follow robot. H: overview. Space: pause. R: retry same maze.\n"
             "Playback: [ half / ] double. Type speed <multiplier> for any positive rate.")
    else:
        text((24, 282, width - 48, 52),
             "Release keys to stop. F: follow robot. H: overview.\n"
             "Examples: forward 0.3   |   backward 0.2   |   rotate 90 / rotate -90")
    caption = ("COMMAND   (metres / degrees; speed = playback multiplier)" if playback_controls else
               "DISTANCE / ANGLE COMMAND   (metres / degrees, positive turn = left)")
    text((24, 344, width - 48, 26), caption)
    layout = guide_layout(width)
    color = (0.12, 0.23, 0.34) if editing else (0.10, 0.13, 0.18)
    mujoco.mjr_rectangle(rect(layout["entry"]), *color, 1)
    shown = entry + ("_" if editing else "") if entry or editing else "Click here and type: forward 0.3"
    text((34, 386, width - 196, 28), shown[-80:])
    mujoco.mjr_label(rect(layout["submit"]), font, "Queue / Enter",
                     0.13, 0.34, 0.58, 1, 0.95, 0.97, 1, context)
    text((24, 434, width - 48, 36), message or "Commands execute one at a time. Type stop or click Stop to cancel.")
    status = latest.get("motion", {}) if latest else {}
    if status.get("state") == "running" and status.get("kind") == "velocity":
        description = status.get("message", "Sensor-guided driving")
        progress = f"{status['linear']:.3f} m/s, {status['angular']:.3f} rad/s"
    elif status.get("state") == "running":
        description = f"{status['kind']} {status['amount']:g} {status['unit']}"
        progress = f"{status['progress']:.3f} / {status['amount']:g} {status['unit']}"
    else:
        description = status.get("message", "Waiting for MuJoCo...")
        progress = status.get("state", "waiting").upper()
    text((24, 478, width - 48, 72), "CURRENT TASK\nProgress / result\nWaiting commands",
         f"{description}\n{progress}\n{status.get('pending', 0)}")
