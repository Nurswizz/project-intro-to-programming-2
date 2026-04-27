class Entity: 
    def __init__(self, hp: int, attack: int, defense: int):
        self.hp = hp
        self.attack = attack
        self.defense = defense
    
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

class Player(Entity):
    def __init__(self, hp: int, attack: int, defense: int, name: str):
        super().__init__(hp, attack, defense)
        self.name = name
    
class Enemy(Entity):
    def __init__(self, hp: int, attack: int, defense: int, type: str):
        super().__init__(hp, attack, defense)
        self.type = type
    