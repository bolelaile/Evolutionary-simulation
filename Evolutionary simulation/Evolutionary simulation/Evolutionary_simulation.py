import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from config import Config  # 配置文件



class Environment:
    def __init__(self):
        self.size = Config.ENV_SIZE
        self.food_spawn_rate = Config.FOOD_SPAWN_RATE
        self.food = []
        self.prey = []      # 原有物种
        self.predators = [] # 新增捕食者
        self.cycle_count = 0
        self.initialize_population()
        self.init_plot()

    def initialize_population(self):
        """初始化生态系统"""
        for _ in range(Config.INITIAL_PREY):
            self.prey.append(Herbivore(self))
        for _ in range(Config.INITIAL_PREDATORS):
            self.predators.append(Predator(self))

    def spawn_food(self):
        # 调整食物生成概率和数量
        food_spawn_attempts = int(20 + len(self.prey) / 50)  # 根据猎物数量调整尝试次数
        for _ in range(food_spawn_attempts):
            if random.random() < self.food_spawn_rate * (1 + len(self.prey)/50):
                self.food.append(Food(
                    x=random.uniform(2, self.size-2),
                    y=random.uniform(2, self.size-2),
                    energy=random.uniform(15, 45)
                ))

    def update(self):
        self.cycle_count += 1
        self.spawn_food()
        
        for org_list in [self.prey, self.predators]:
            dead_orgs = []
            new_orgs = []
            
            for org in org_list:
                org.update()  # 调用每个生物的更新方法
                
                if org.death_check():
                    dead_orgs.append(org)
                    continue
                
                if org.can_reproduce():
                    new_org = org.reproduce()
                    if new_org: 
                        new_orgs.append(new_org)
            
            org_list[:] = [org for org in org_list if org not in dead_orgs]
            org_list.extend(new_orgs)
        
        self.prey = [prey for prey in self.prey if not prey.eaten]
        self.food = [f for f in self.food if not f.eaten]

    def init_plot(self):
        """初始化图表"""
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, self.size)  # 根据需要调整x轴范围
        self.ax.set_ylim(0, self.size)  # 根据需要调整y轴范围
        self.lines = {}
        self.lines['food'], = self.ax.plot([], [], 'o', label='Food')
        self.lines['prey'], = self.ax.plot([], [], 'o', label='Prey')
        self.lines['predator'], = self.ax.plot([], [], 'o', label='Predator')
        self.ax.legend()
        self.x_data = []
        self.food_counts = []
        self.prey_counts = []
        self.predator_counts = []

    def update_plot(self):
        """更新图表数据"""
        self.x_data.append(self.cycle_count)
        self.food_counts.append(len(self.food))
        self.prey_counts.append(len(self.prey))
        self.predator_counts.append(len(self.predators))
        
        for key, line in self.lines.items():
            if key == 'food':
                x_coords = [food.x for food in self.food]
                y_coords = [food.y for food in self.food]
            elif key == 'prey':
                x_coords = [herb.x for herb in self.prey]
                y_coords = [herb.y for herb in self.prey]
            else:
                x_coords = [pred.x for pred in self.predators]
                y_coords = [pred.y for pred in self.predators]
            
            line.set_data(x_coords, y_coords)
        
        self.ax.relim()
        self.ax.autoscale_view()
        return self.lines.values()

    def run_simulation(self, num_cycles=1000):
        """运行模拟"""
        ani = FuncAnimation(self.fig, self._animate, frames=num_cycles, interval=200, repeat=False)
        plt.show()

    def _animate(self, frame):
        """动画更新函数"""
        self.update()
        self.update_plot()

class OrganismBase:
    def __init__(self, env, level=None):
        self.x = random.uniform(10, env.size-10)
        self.y = random.uniform(10, env.size-10)
        self.energy = random.uniform(30, 50)
        self.age = 0
        self.hunger_timer = 0  # 饥饿计时
        self.env = env
        self.eaten = False
        self.level = level if level is not None else random.randint(1, 5)  # 默认等级
        
        self.metabolism = random.uniform(0.5, 0.8)
        self.death_prob = 0.002
    
    def update(self):
        """通用生物更新逻辑"""
        if not self.eaten:
            self.move()
            self.eat()
            self.age += 1
            
            # 通用能源消耗
            self.energy -= self.metabolism + 0.02 * self.hunger_timer
            self.hunger_timer += 1
            
            # 行动能力衰减
            if self.hunger_timer > 50:
                self.energy *= 0.95

    def can_eat(self, target):
        """判断是否可以捕食目标"""
        return isinstance(target, OrganismBase) and target.level <= self.level + 3

    def death_check(self):
        """通用死亡判定"""
        conditions = [
            self.energy <= 0,
            self.age > self.max_age,
            self.hunger_timer > 100,
            random.random() < self.death_prob,
            self.x < 2 or self.x > self.env.size-2,
            self.y < 2 or self.y > self.env.size-2
        ]
        return any(conditions)

class Herbivore(OrganismBase):
    """原有物种（食草型）"""
    def __init__(self, env):
        super().__init__(env)
        self.max_age = Config.HERBIVORE_MAX_AGE
        self.speed = random.uniform(*Config.HERBIVORE_SPEED_RANGE)  # 使用配置中的速度范围
        self.sense_range = random.uniform(*Config.HERBIVORE_SENSE_RANGE)
        self.reproduction_threshold = Config.HERBIVORE_REPRODUCTION_THRESHOLD
        
    def move(self):
        nearest_predator = self.escape_from_predator()
        if nearest_predator:
            # 如果有捕食者靠近，则优先逃跑
            dx = self.x - nearest_predator.x + random.gauss(0, 0.3)
            dy = self.y - nearest_predator.y + random.gauss(0, 0.3)
        else:
            # 没有捕食者威胁时，寻找最近的食物
            nearest_food = None
            min_dist = float('inf')
            for food in self.env.food:
                dist = math.hypot(food.x - self.x, food.y - self.y)
                if dist < self.sense_range and dist < min_dist:
                    nearest_food = food
                    min_dist = dist
            if nearest_food:
                dx = nearest_food.x - self.x + random.gauss(0, 0.3)
                dy = nearest_food.y - self.y + random.gauss(0, 0.3)
            else:
                # 如果没有找到食物，则随机移动
                angle = random.uniform(0, 2*math.pi)
                dx = math.cos(angle)
                dy = math.sin(angle)

        effective_speed = self.speed * (0.5 + (50/(self.hunger_timer + 50)))
        length = math.hypot(dx, dy)
        if length > 0:
            dx = (dx/length) * effective_speed
            dy = (dy/length) * effective_speed

        self.x = max(2, min(self.env.size-2, self.x + dx))
        self.y = max(2, min(self.env.size-2, self.y + dy))

    def escape_from_predator(self):
        nearest_predator = None
        min_dist = float('inf')
        for predator in self.env.predators:
            dist = math.hypot(predator.x - self.x, predator.y - self.y)
            if dist < self.sense_range and dist < min_dist:
                nearest_predator = predator
                min_dist = dist
        return nearest_predator

    def eat(self):
        for food in self.env.food:
            if math.hypot(food.x-self.x, food.y-self.y) < 1.5 and not food.eaten:
                self.energy += food.energy
                self.hunger_timer = -20  # 重置饥饿计时
                food.eaten = True
                break

    def can_reproduce(self):
        return self.energy >= self.reproduction_threshold

    def reproduce(self):
        if random.random() < 0.4:
            self.energy *= 0.5
            child = Herbivore(self.env)
            child.level = max(1, min(self.level + random.choice([-1, 0, 1]), 5))  # 等级变异
            child.speed = max(0.5, self.speed * random.uniform(0.9, 1.1))
            child.metabolism = max(0.1, self.metabolism * random.uniform(0.9, 1.1))
            return child

class Predator(OrganismBase):
    """捕食者物种"""
    def __init__(self, env):
        super().__init__(env)
        self.speed = random.uniform(*Config.PREDATOR_SPEED_RANGE)  # 使用配置中的速度范围
        self.base_sense_range = random.uniform(*Config.PREDATOR_SENSE_RANGE)
        self.max_age = Config.PREDATOR_MAX_AGE
        self.metabolism = 1.2
        self.reproduction_threshold = Config.PREDATOR_REPRODUCTION_THRESHOLD
        self.attack_range = Config.PREDATOR_ATTACK_RANGE

    @property
    def sense_range(self):
        """动态调整捕食者的感知范围"""
        hunger_factor = 1 + (self.hunger_timer / 100)  # 饥饿时间越长，感知范围越大
        return self.base_sense_range * hunger_factor

    def move(self):
        nearest_prey = self.find_nearest_prey()
        if nearest_prey:
            dx = nearest_prey.x - self.x + random.gauss(0, 0.2)
            dy = nearest_prey.y - self.y + random.gauss(0, 0.2)
        else:
            angle = random.uniform(0, 2*math.pi)
            dx = math.cos(angle) * 3
            dy = math.sin(angle) * 3

        speed_factor = 0.3 + (70/(self.hunger_timer + 70))
        effective_speed = self.speed * speed_factor
        
        length = math.hypot(dx, dy)
        if length > 0:
            dx = (dx/length) * effective_speed
            dy = (dy/length) * effective_speed
        
        self.x = max(2, min(self.env.size-2, self.x + dx))
        self.y = max(2, min(self.env.size-2, self.y + dy))

    def find_nearest_prey(self):
        nearest_prey = None
        min_dist = float('inf')
        for prey in self.env.prey:
            if self.can_eat(prey):
                dist = math.hypot(prey.x - self.x, prey.y - self.y)
                if dist < self.sense_range and dist < min_dist and not prey.eaten:
                    nearest_prey = prey
                    min_dist = dist
        return nearest_prey

    def eat(self):
        for prey in self.env.prey:
            if self.can_eat(prey) and math.hypot(prey.x-self.x, prey.y-self.y) < self.attack_range and not prey.eaten:
                self.energy += prey.energy * 0.6
                self.hunger_timer = -30
                prey.eaten = True
                break
    
    def can_reproduce(self):
        return self.energy >= self.reproduction_threshold and random.random() < 0.25

    def reproduce(self):
        if random.random() < 0.25:
            self.energy *= 0.4
            child = Predator(self.env)
            child.level = max(1, min(self.level + random.choice([-1, 0, 1]), 5))
            child.speed = max(1.5, self.speed * random.uniform(0.85, 1.15))
            child.metabolism = self.metabolism * random.uniform(0.9, 1.1)
            return child

class Food:
    def __init__(self, x, y, energy):
        self.x = x
        self.y = y
        self.energy = energy
        self.eaten = False

def visualize():
    fig, ax = plt.subplots(figsize=(10, 10))
    env = Environment()

    def update(frame):
        env.update()
        ax.clear()
        ax.set_xlim(0, env.size)
        ax.set_ylim(0, env.size)
        
        food_x = [f.x for f in env.food if not f.eaten]
        food_y = [f.y for f in env.food if not f.eaten]
        ax.scatter(food_x, food_y, c='#8BC34A', s=25, marker='s', alpha=0.7)
        
        prey_x = [p.x for p in env.prey if not p.eaten]
        prey_y = [p.y for p in env.prey if not p.eaten]
        prey_energy = [p.energy/100 for p in env.prey if not p.eaten]
        ax.scatter(prey_x, prey_y, c=prey_energy, cmap='Blues', s=35, edgecolors='#2196F3', alpha=0.8)
        
        predator_x = [p.x for p in env.predators]
        predator_y = [p.y for p in env.predators]
        predator_size = [p.energy/5 + 30 for p in env.predators]
        ax.scatter(predator_x, predator_y, c='#FF5722', s=predator_size, edgecolors='#BF360C', alpha=0.9)
        
        stats = (f"Cycle: {env.cycle_count}\n"
                f"Prey: {len(env.prey)}  Predators: {len(env.predators)}\n"
                f"Avg Age (Prey): {np.mean([p.age for p in env.prey]):.1f}\n"
                f"Avg Hunger: {np.mean([p.hunger_timer for p in env.prey]):.1f}")
        ax.text(1, 58, stats, ha='left', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=0.8))
        ax.grid(color='gray', linestyle=':', alpha=0.3)

    ani = FuncAnimation(fig, update, interval=Config.ANIMATION_INTERVAL)  # 使用配置中的动画间隔
    plt.show()

if __name__ == "__main__":
    visualize()