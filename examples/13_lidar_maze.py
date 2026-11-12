# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from math import pi
from module import sensor
from module.move import move
from examples.runtime import Lab
from examples.world import SCENES
