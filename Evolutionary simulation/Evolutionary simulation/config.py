# config.py

class Config:
    # Environment settings
    ENV_SIZE = 100  # 环境大小
    FOOD_SPAWN_RATE = 0.5  # 食物生成概率
    INITIAL_PREY = 50  # 初始猎物数量
    INITIAL_PREDATORS = 10  # 初始捕食者数量

    # Herbivore settings
    HERBIVORE_MAX_AGE = 180
    HERBIVORE_SPEED_RANGE = (0.6, 0.9)
    HERBIVORE_SENSE_RANGE = (8, 12)
    HERBIVORE_REPRODUCTION_THRESHOLD = 80

    # Predator settings
    PREDATOR_MAX_AGE = 80
    PREDATOR_SPEED_RANGE = (1.0, 1.25)
    PREDATOR_SENSE_RANGE = (15, 20)
    PREDATOR_REPRODUCTION_THRESHOLD = 150
    PREDATOR_ATTACK_RANGE = 2.0

    # Animation settings
    ANIMATION_INTERVAL = 100
