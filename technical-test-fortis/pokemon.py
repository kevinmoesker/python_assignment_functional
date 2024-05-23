from abc import ABC, abstractmethod


class Pokemon(ABC):
    def __init__(self, type_: str, hp: int) -> None:
        self.type_ = type_
        self.hp = hp

    @abstractmethod
    def special_attack(self, opponent_pokemon: "Pokemon") -> int:
        ...

# FirePokemon
# 1/ Add a class constant weak_type = "grass"
# 2/ Initialize wth a "attack_damage" being an int
# 3/ Write expected method with the following logic:
  # - if opponent pokemon type is the weak type of the fire pokemon, deals twice the damage
  # - if opponent pokemon type is the same as "fire", deals half the damage
  # - else, deals the normal damage


# combat()
def combat(my_pokemon: Pokemon, opponent_pokemon: Pokemon) -> Pokemon:
    """
    Simulates a fight between Pokemons.
    "my_pokemon" always attacks first.
    Then, they attack one after the other until one is dead (hp<=0).
    Args:
      - my_pokemon: Pokemon that will attack 1st
      - opponent_pokemon: Pokemon that will attack 2nd

    Returns:
      - The victorious pokemon
    """
    ...
