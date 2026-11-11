# 파일 경로로 실행해도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module import course, motion, sensor
