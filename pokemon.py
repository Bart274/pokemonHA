"""
Allows to configure custom shell commands to turn a value for a sensor.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.command_sensor/
"""
import logging
import subprocess
from datetime import timedelta
import random
import os

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers.event import track_utc_time_change
from homeassistant.helpers.entity import generate_entity_id

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Ash"
DEFAULT_ENEMY = "Gary"

DOMAIN = "pokemon"

MOVES = {"tackle": range(18, 26),
         "thundershock": range(10, 36),
         "heal": range(10, 20)}

MOVES_LOW_HEALTH = {"tackle": range(18, 26),
                    "thundershock": range(10, 36),
                    "heal": range(10, 20),
                    "heal": range(10, 20),
                    "heal": range(10, 20)}

ENTITY_ID_FORMAT = DOMAIN + '.{}'

POKEDEX = []
IV = 30
EV = 85
STAB = 1.5
POKEMONDICTIONARY = {}
TYPEDICTIONARY = {}
MOVES_DICTIONARY = {}

def setup(hass, config):
    """ Set up the iCloud Scanner. """
    
    if config.get(DOMAIN) is None:
        return False
        
    fin = open(os.path.join(os.getcwd(),"pokemon.csv"), 'r')
    # Creating a dictionary with each Pokemon's name as a key
    for line in fin:
        line = line.strip()
        pokeList = line.split(",")
        POKEMONDICTIONARY[pokeList[1]] = pokeList
    fin.close()

    # Taking the keys from above, turning them into a list, and sorting them
    for key in POKEMONDICTIONARY:
        POKEDEX.append(POKEMONDICTIONARY[key][1].lower())
        POKEDEX.sort()
        
    # Reading "Type Advantages.csv" file to determine type advantages and the damage modifier
    # Stores the line number in the csv as the key and a list giving information about type advantage for the value
    fin = open(os.path.join(os.getcwd(),"pokemontypeadvantages.csv"), 'r')
    for line in fin:
        line = line.strip()
        typeList = line.split(",")
        TYPEDICTIONARY[typeList[0]] = typeList
        # This list contains a number in the first position, the attack type in the second, the defending type in the third,
        # and the appropriate damage multiplier in the fourth
    fin.close()

    pokemon_config = config[DOMAIN]

    # Get the username and password from the configuration
    playername = pokemon_config.get('playername', DEFAULT_NAME)
    enemyname = pokemon_config.get('enemyname', DEFAULT_ENEMY)
        
    player = Pokemon(hass, 'player', playername)
    player.update_ha_state()
        
    enemy = Pokemon(hass, 'enemy', enemyname)
    enemy.update_ha_state()
        
    pokemonplayer1 = Pokemon(hass, 'pokemon', '1', player)
    pokemonplayer1.update_ha_state()
        
    pokemonplayer2 = Pokemon(hass, 'pokemon', '2', player)
    pokemonplayer2.update_ha_state()
       
    pokemonplayer3 = Pokemon(hass, 'pokemon', '3', player)
    pokemonplayer3.update_ha_state()
        
    pokemonplayer4 = Pokemon(hass, 'pokemon', '4', player)
    pokemonplayer4.update_ha_state()
        
    pokemonplayer5 = Pokemon(hass, 'pokemon', '5', player)
    pokemonplayer5.update_ha_state()
        
    pokemonplayer6 = Pokemon(hass, 'pokemon', '6', player)
    pokemonplayer6.update_ha_state()
        
    pokemonenemy1 = Pokemon(hass, 'pokemon', '1', enemy)
    pokemonenemy1.update_ha_state()
        
    pokemonenemy2 = Pokemon(hass, 'pokemon', '2', enemy)
    pokemonenemy2.update_ha_state()
        
    pokemonenemy3 = Pokemon(hass, 'pokemon', '3', enemy)
    pokemonenemy3.update_ha_state()
        
    pokemonenemy4 = Pokemon(hass, 'pokemon', '4', enemy)
    pokemonenemy4.update_ha_state()
        
    pokemonenemy5 = Pokemon(hass, 'pokemon', '5', enemy)
    pokemonenemy5.update_ha_state()
        
    pokemonenemy6 = Pokemon(hass, 'pokemon', '6', enemy)
    pokemonenemy6.update_ha_state()
        
    pokemonbattle = Pokemon(hass, 'battle', 'battle', player, enemy,
                            pokemonplayer1, pokemonplayer2, pokemonplayer3,
                            pokemonplayer4, pokemonplayer5, pokemonplayer6,
                            pokemonenemy1, pokemonenemy2, pokemonenemy3,
                            pokemonenemy4, pokemonenemy5, pokemonenemy6)
    pokemonbattle.update_ha_state()
        
    def update(now):
        """ Keeps the api logged in of all account """
        pokemonbattle.update()
        player.update()
        enemy.update()
        pokemonplayer1.update()
        pokemonplayer2.update()
        pokemonplayer3.update()
        pokemonplayer4.update()
        pokemonplayer5.update()
        pokemonplayer6.update()
        pokemonenemy1.update()
        pokemonenemy2.update()
        pokemonenemy3.update()
        pokemonenemy4.update()
        pokemonenemy5.update()
        pokemonenemy6.update()
            
    track_utc_time_change(
        hass, update,
        second=0
    )
    
    # Tells the bootstrapper that the component was successfully initialized
    return True

class Pokemon(Entity):
    def __init__(self, hass, type, name, person1=None, person2=None,
                 pokemonplayer1=None, pokemonplayer2=None, pokemonplayer3=None,
                 pokemonplayer4=None, pokemonplayer5=None, pokemonplayer6=None,
                 pokemonenemy1=None, pokemonenemy2=None, pokemonenemy3=None,
                 pokemonenemy4=None, pokemonenemy5=None, pokemonenemy6=None):
        self.hass = hass
        self.type = type
        if type == 'pokemon':
            self.pname = type + name
        else:
            self.pname = name
        self.person1 = person1
        self.person2 = person2
        self.health = 100
        self._state = None
        self.lastmove = None
        self.attackedwith = None
        self.damage = 0
        self.resetting = 0
        self.victories = 0
        self.badges = 0
        self.pokedex = 0
        self.caughtpokemon = []
        self.level = 1
        self.attacker = None
        self.victim = None
        self.activepokemonplayer = None
        self.activepokemonenemy = None
        self.battlestate = None
        self.pokemonplayer1 = pokemonplayer1
        if self.pokemonplayer1 is not None:
            self.pokemonplayer1.choosepokemon()
        self.pokemonplayer2 = pokemonplayer2
        if self.pokemonplayer2 is not None:
            self.pokemonplayer2.choosepokemon()
        self.pokemonplayer3 = pokemonplayer3
        if self.pokemonplayer3 is not None:
            self.pokemonplayer3.choosepokemon()
        self.pokemonplayer4 = pokemonplayer4
        if self.pokemonplayer4 is not None:
            self.pokemonplayer4.choosepokemon()
        self.pokemonplayer5 = pokemonplayer5
        if self.pokemonplayer5 is not None:
            self.pokemonplayer5.choosepokemon()
        self.pokemonplayer6 = pokemonplayer6
        if self.pokemonplayer6 is not None:
            self.pokemonplayer6.choosepokemon()
        self.pokemonenemy1 = pokemonenemy1
        if self.pokemonenemy1 is not None:
            self.pokemonenemy1.choosepokemon()
        self.pokemonenemy2 = pokemonenemy2
        if self.pokemonenemy2 is not None:
            self.pokemonenemy2.choosepokemon()
        self.pokemonenemy3 = pokemonenemy3
        if self.pokemonenemy3 is not None:
            self.pokemonenemy3.choosepokemon()
        self.pokemonenemy4 = pokemonenemy4
        if self.pokemonenemy4 is not None:
            self.pokemonenemy4.choosepokemon()
        self.pokemonenemy5 = pokemonenemy5
        if self.pokemonenemy5 is not None:
            self.pokemonenemy5.choosepokemon()
        self.pokemonenemy6 = pokemonenemy6
        if self.pokemonenemy6 is not None:
            self.pokemonenemy6.choosepokemon()
        
        self.chosenpokemon = None
        self.__id = None
        self.pokemonname = None
        self.type1 = None
        self.type2 = None
        self.__hp = None
        self.__atk = None
        self.__defense = None
        self.__spAtk = None
        self.__spDef = None
        self.__speed = None
        self.battleHP = None
        self.battleATK = None
        self.battleDEF = None
        self.battleSpATK = None
        self.battleSpDEF = None
        self.battleSpeed = None
        self.originalATK = None
        self.originalDEF = None
        self.originalSpATK = None
        self.originalSpDEF = None
        self.originalSpeed = None
        self.move1 = None
        self.move2 = None
        self.move3 = None
        self.move4 = None
        self.movelist = None
        self.atkStage = None
        self.defStage = None
        self.spAtkStage = None
        self.spDefStage = None
        self.speedStage = None
        
        if self.type == 'pokemon':
            self.entity_id = generate_entity_id(
                ENTITY_ID_FORMAT, self.pname + self.person1.type,
                hass=self.hass)
                
        else:
            self.entity_id = generate_entity_id(
                ENTITY_ID_FORMAT, self.type,
                hass=self.hass)
        
    @property
    def state_attributes(self):
        """ returns the friendlyname of the icloud tracker """
        if self.type == 'player' or self.type == 'enemy':
            return {
                "name": self.pname,
                "victories": self.victories,
                "badges": self.badges,
                "pokedex": self.pokedex
            }
        elif self.type == 'pokemon':
            return {
                "name": self.pname,
                "health": self.health,
                "level": self.level,
                "owner": self.person1.pname
            }
        else:
            if self.attacker is None:
                tempattacker = None
            else:
                tempattacker = self.attacker.person1.pname
            if self.victim is None:
                tempvictim = None
            else:
                tempvictim = self.victim.person1.pname
            if self.activepokemonplayer is None:
                tempapp = None
            else:
                tempapp = self.activepokemonplayer.pokemonname
            if self.activepokemonenemy is None:
                tempape = None
            else:
                tempape = self.activepokemonenemy.pokemonname
            
            return {
                "attacker": tempattacker,
                "victim": tempvictim,
                "active pokemon player": tempapp,
                "active pokemon enemy": tempape,
                "action": self.battlestate
            }
    
    @property
    def icon(self):
        """Return the icon to use for device if any."""
        if self.type == 'player' or self.type == 'enemy':
            return 'mdi:account-card-details'
        elif self.type == 'battle':
            if self.resetting > 0:
                return 'mdi:cached'
            elif self.battlestate == self.person1.pname + " defeated " + self.person2.pname:
                return 'mdi:trophy'
            elif self.battlestate == self.person2.pname + " defeated " + self.person1.pname:
                return 'mdi:emoticon-sad'
            else:
                return 'mdi:gamepad-variant'
        else:
            return 'mdi:pokeball'
    
    @property
    def state(self):
        """Return the state of the device."""
        if self.type == 'player' or self.type == 'enemy':
            self._state = self.victories
        elif self.type == 'pokemon':
            self._state = self.pokemonname
        else:
            self._state = self.battlestate
            
        return self._state
        
    def choosepokemon(self, chosenpokemon=None):
        if chosenpokemon is None:
            chosenpokemon = random.choice(list(POKEMONDICTIONARY))
        self.chosenpokemon = chosenpokemon
        
        for key in POKEMONDICTIONARY:
            if key.lower() == chosenpokemon.lower():
                pokemonInfo = POKEMONDICTIONARY[key]
        
        if self.chosenpokemon not in self.person1.caughtpokemon:
                self.person1.caughtpokemon.append(self.chosenpokemon)
                self.person1.pokedex += 1

        # ATTRIBUTES
        # Referring to the pokemonInfo list to fill in the rest of the attributes
        # ID Info
        self.__id = pokemonInfo[0]
        self.pokemonname = pokemonInfo[1]
        
        # Type
        self.type1 = pokemonInfo[2]
        self.type2 = pokemonInfo[3]

        # BASE STATS
        self.__hp = int(pokemonInfo[4])
        self.__atk = int(pokemonInfo[5])
        self.__defense = int(pokemonInfo[6])
        self.__spAtk = int(pokemonInfo[7])
        self.__spDef = int(pokemonInfo[8])
        self.__speed = int(pokemonInfo[9])

        # In Battle Stats
        # The base stat is different from the in battle stat. The base stat is just used for calculating the in-battle stat
        # The in battle stats are calculated based on a formula from the games
        self.battleHP = int(self.__hp + (0.5*IV) + (0.125*EV) + 60)
        self.battleATK = self.__atk + (0.5*IV) + (0.125*EV) + 5
        self.battleDEF = self.__defense + (0.5*IV) + (0.125*EV) + 5
        self.battleSpATK = self.__spAtk + (0.5*IV) + (0.125*EV) + 5
        self.battleSpDEF = self.__spDef + (0.5*IV) + (0.125*EV) + 5
        self.battleSpeed = self.__speed + (0.5*IV) + (0.125*EV) + 5

        # These variables are used to just hold the values of the original stat for stat modification purposes
        self.originalATK = self.__atk + (0.5*IV) + (0.125*EV) + 5
        self.originalDEF = self.__defense + (0.5*IV) + (0.125*EV) + 5
        self.originalSpATK = self.__spAtk + (0.5*IV) + (0.125*EV) + 5
        self.originalSpDEF = self.__spDef + (0.5*IV) + (0.125*EV) + 5
        self.originalSpeed = self.__speed + (0.5*IV) + (0.125*EV) + 5

        # Moves
        # The Kanto Pokemon Spreadsheet has pre-determined movesets
        self.move1 = Move(pokemonInfo[10])
        self.move2 = Move(pokemonInfo[11])
        self.move3 = Move(pokemonInfo[12])
        self.move4 = Move(pokemonInfo[13])

        # A list containing all the moves; used for error-checking later
        self.movelist = [self.move1.name.lower(), self.move2.name.lower(), self.move3.name.lower(), self.move4.name.lower()]
        
        self.health = self.battleHP

        # In Battle Stats
        # Raised or lowered based on different moves used in battle. Affects the in battle stats (more info in the Overview of Battle Mechanics in readme.txt)
        self.atkStage = 0
        self.defStage = 0
        self.spAtkStage = 0
        self.spDefStage = 0
        self.speedStage = 0

    # Get Attribute METHODS
    def getPokemonName(self):
        return self.pokemonname

    def getLevel(self):
        return self.level

    # Get BASE STAT METHODS
    def getHP(self):
        return self.__hp

    def getATK(self):
        return self.__atk

    def getDEF(self):
        return self.__defense

    def getSpATK(self):
        return self.__spAtk

    def getSpDEF(self):
        return self.__spDef

    def getSpeed(self):
        return self.__speed

    # Get STAT STAGE Methods
    def getAtkStage(self):
        return self.atkStage

    def getDefStage(self):
        return self.defStage

    def getSpAtkStage(self):
        return self.spAtkStage

    def getSpDefStage(self):
        return self.spDefStage

    def getSpeedStage(self):
        return self.speed

    # Set STAT STAGE Methods
    def setAtkStage(self, atkStage):
        self.atkStage = atkStage

    def setDefStage(self, defStage):
        self.defStage = defStage

    def setSpAtkStage(self, spAtkStage):
        self.spAtkStage = spAtkStage

    def setSpDefStage(self, spDefStage):
        self.spDefStage = spDefStage

    def setSpeedStage(self, speedStage):
        self.speedStage = speedStage

    # MOVE Methods
    def getMove1(self):
        return self.move1

    def getMove2(self):
        return self.move2

    def getMove3(self):
        return self.move3

    def getMove4(self):
        return self.move4

    def setMove1(self, move1):
        self.move1 = Move(move1)

    def setMove2(self, move2):
        self.move2 = Move(move2)

    def setMove3(self, move3):
        self.move3 = Move(move3)

    def setMove4(self, move4):
        self.move4 = Move(move4)
        
    # Takes an int as input and returns a string with the pokemon losing that much HP
    def loseHP(self, lostHP):
        self.battleHP -= lostHP
        # Making sure battlHP doesn't fall below 0
        if self.battleHP <= 0:
            self.battleHP = 0
        msg = self.pokemonname + " lost " + str(lostHP) + " HP!"
        return msg

    # Takes an int as input and returns a string with the pokemon gaining that much HP
    def gainHP(self, gainedHP):
        self.__hp += gainedHP

    # Determines if the Pokemon still has HP and returns a boolean
    def isAlive(self):
        if self.battleHP > 0:
            return True
        else:
            return False
            
    # Stat modification function; will be called inside the attack function if the move alters the defending Pokemon's stats
    # Takes the current statStage as input and returns a multiplier that will be used to calculate the new statStage
    def statMod(self, statStage):
        if statStage == 1:
            multiplier = 1.5
        elif statStage == -1:
            multiplier = 2/3
        elif statStage == 2:
            multiplier = 2
        elif statStage == -2:
            multiplier = 1/2
        elif statStage == 3:
            multiplier = 2.5
        elif statStage == -3:
            multiplier = 0.4
        elif statStage == 4:
            multiplier = 3
        elif statStage == -4:
            multiplier = 1/3
        elif statStage == 5:
            multiplier = 3.5
        elif statStage == -5:
            multiplier = 2/7
        elif statStage == 6:
            multiplier = 4
        elif statStage == -6:
            multiplier = 1/4

        return multiplier  # This multiplier affects the value of the in-battle stat

    # Will take a move, the attacking Pokemon object, and the defending Pokemon object as input
    # Will return a string that contains the amount of damage done and the effectiveness of the move
    def attack(self, move):
        # Creating an empty string to store the results of the attack function
        tempMsg= ""

        # Making the input string into an actual move object
        move = Move(move)

        # This modifier is used in damage calculations; it takes into account type advantage and STAB bonus
        modifier = 1

        # Calculating Type advantages using "Type Advantages.csv" file
        for key in TYPEDICTIONARY:
            # If the attacking and defending types match up, multiply the modifier by the damage multiplier from the list
            if TYPEDICTIONARY[key][1] == move.type and TYPEDICTIONARY[key][2] == self.victim.type1:
                modifier *= float(TYPEDICTIONARY[key][3])

            # Didn't use elif; Just in case you get a 4x or 0.25x modifier based on double type
            if TYPEDICTIONARY[key][1] == move.type and TYPEDICTIONARY[key][2] == self.victim.type2:
                modifier *= float(TYPEDICTIONARY[key][3])

        # Calculating STAB (Same-type Attack Bonus)
        if move.type == self.attacker.type1:
            modifier *= STAB
        elif move.type == self.attacker.type2:
            modifier *= STAB

        # Damage formula also has a random element
        modifier *= random.uniform(0.85, 1.0)

        # Appending the useMove function to the output
        tempMsg += self.attacker.useMove(move)

        # ATK/DEF or SpATK/SpDEF or Status? Using the Pokemon damage formula
        # If the move is "Physical", the damage formula will take into account attack and defense
        if move.kind == "Physical":
            self.damage = int((((2*self.attacker.getLevel()) + 10)/250 * (self.attacker.battleATK/self.victim.battleDEF) * move.getPower() + 2) * modifier)
            tempMsg += "\n" + self.victim.loseHP(self.damage)
        # If the move is "Special", the damage formula will take into account special attack and special defense
        elif move.kind == "Special":
            self.damage = int((((2*self.attacker.getLevel()) + 10)/250 * (self.attacker.battleSpATK/self.victim.battleSpDEF) * move.getPower() + 2) * modifier)
            tempMsg += "\n" + self.victim.loseHP(self.damage)

        # Stat Changing moves
        else:
            # If the move is stat-changing, it does 0 damage and the modifier is set to 1 (so it doesn't return super effective or not very effective)
            self.damage = 0
            modifier = 1

            # Going through each kind of different stat change based on the move type
            if move.kind == "a-":
                self.victim.atkStage -= 1
                self.victim.battleATK = self.victim.originalATK * self.statMod(self.victim.atkStage)
                tempMsg += "\n" + self.victim.pokemonname + "'s attack fell! "

            elif move.kind == "a+":
                self.attacker.atkStage +=1
                self.attacker.battleATK = self.attacker.originalATK * self.statMod(self.attacker.atkStage)
                tempMsg += "\n" + self.attacker.pokemonname + "'s attack rose! "

            elif move.kind == "d+":
                self.attacker.defStage +=1
                self.attacker.battleDEF = self.attacker.originalDEF * self.statMod(self.attacker.defStage)
                tempMsg += "\n" + self.attacker.pokemonname + "'s defense rose! "

            elif move.kind == "sa+":
                self.attacker.spAtkStage +=1
                self.attacker.battleSpATK = self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage)
                tempMsg += "\n" + self.attacker.pokemonname + "'s special attack rose! "

            elif move.kind == "sd+":
                self.attacker.spDefStage +=1
                self.attacker.battleSpDef = self.attacker.originalSpDEF * self.statMod(self.attacker.spDefStage)
                tempMsg += "\n" + self.attacker.pokemonname + "'s special defense rose! "

            elif move.kind == "s+":
                self.attacker.speedStage +=1
                self.attacker.battleSpeed = self.attacker.originalSpeed * self.statMod(self.attacker.speedStage)
                tempMsg += "\n" + self.attacker.pokemonname + "'s speed fell! "

            elif move.kind == "d-":
                self.victim.defStage -=1
                self.victim.battleDEF = self.victim.originalDEF * self.statMod(self.victim.defStage)
                tempMsg += "\n" + self.victim.pokemonname + "'s defense fell! "

            elif move.kind == "sa-":
                self.victim.spAtkStage -=1
                self.victim.battleSpATK = self.victim.originalSpATK * self.statMod(self.victim.spAtkStage)
                tempMsg += "\n" + self.victim.pokemonname + "'s special attack fell! "

            elif move.kind == "sd-":
                self.victim.spDefStage -=1
                self.victim.battleSpDEF = self.victim.originalSpDEF * self.statMod(self.victim.spDefStage)
                tempMsg += "\n" + self.victim.pokemonname + "'s special defense fell! "

            elif move.kind == "s-":
                self.victim.speedStage -=1
                self.victim.battleSpeed = self.victim.originalSpeed * self.statMod(self.victim.speedStage)
                tempMsg += "\n" + self.victim.pokemonname + "'s speed fell! "

        # Super effective, not very effective, or no effect?
        # Appending the result to tempMsg
        if modifier < 0.85 and modifier > 0:
            tempMsg += "\nIt's not very effective..."

        elif modifier > 1.5:
            tempMsg += "\nIt's super effective!"

        elif modifier == 0.0:
            tempMsg += "\nIt doesn't affect " + self.victim.pokemonname + "..."

        # String containing useMove(), damage, and type effectiveness
        return tempMsg


    def useMove(self, move):
        msg = self.pokemonname + " used " + move.name + "!"
        return msg
        
    def createattack(self):
        _LOGGER.info('POKEMON: %s will attack %s', self.attacker.pokemonname, self.victim.pokemonname)
        cpu_choice = random.choice(self.attacker.movelist)
        self.attackedwith = cpu_choice
        self.battlestate = self.attack(cpu_choice)
        self.victim.health -= self.damage
        if self.victim.health <= 0:
            self.victim.health = 'FNT'
        
    def update(self):
        """Get the latest data and updates the state."""
        _LOGGER.info("POKEMON: update called for: %s", self.entity_id)
        if self.type != 'battle':
            self.update_ha_state()
            return
            
        if self.battlestate is None:
            self.battlestate = "Battle beginning"
            self.resetting = 1
            self.update_ha_state()
            return
            
        if self.resetting > 0:
            self.battlestate = "Battle resetting in " + str(self.resetting) + " minutes"
            self.resetting -= 1
            if self.resetting == 0:
                self.battlestate = "Battle beginning"
                if self.pokemonplayer1.health == 'FNT':
                    self.pokemonplayer1.choosepokemon()
                else:
                    self.pokemonplayer1.choosepokemon(self.pokemonplayer1.chosenpokemon)
                if self.pokemonplayer2.health == 'FNT':
                    self.pokemonplayer2.choosepokemon()
                else:
                    self.pokemonplayer2.choosepokemon(self.pokemonplayer2.chosenpokemon)
                if self.pokemonplayer3.health == 'FNT':
                    self.pokemonplayer3.choosepokemon()
                else:
                    self.pokemonplayer3.choosepokemon(self.pokemonplayer3.chosenpokemon)
                if self.pokemonplayer4.health == 'FNT':
                    self.pokemonplayer4.choosepokemon()
                else:
                    self.pokemonplayer4.choosepokemon(self.pokemonplayer4.chosenpokemon)
                if self.pokemonplayer5.health == 'FNT':
                    self.pokemonplayer5.choosepokemon()
                else:
                    self.pokemonplayer5.choosepokemon(self.pokemonplayer5.chosenpokemon)
                if self.pokemonplayer6.health == 'FNT':
                    self.pokemonplayer6.choosepokemon()
                else:
                    self.pokemonplayer6.choosepokemon(self.pokemonplayer6.chosenpokemon)
                if self.pokemonenemy1.health == 'FNT':
                    self.pokemonenemy1.choosepokemon()
                else:
                    self.pokemonenemy1.choosepokemon(self.pokemonenemy1.chosenpokemon)
                if self.pokemonenemy2.health == 'FNT':
                    self.pokemonenemy2.choosepokemon()
                else:
                    self.pokemonenemy2.choosepokemon(self.pokemonenemy2.chosenpokemon)
                if self.pokemonenemy3.health == 'FNT':
                    self.pokemonenemy3.choosepokemon()
                else:
                    self.pokemonenemy3.choosepokemon(self.pokemonenemy3.chosenpokemon)
                if self.pokemonenemy4.health == 'FNT':
                    self.pokemonenemy4.choosepokemon()
                else:
                    self.pokemonenemy4.choosepokemon(self.pokemonenemy4.chosenpokemon)
                if self.pokemonenemy5.health == 'FNT':
                    self.pokemonenemy5.choosepokemon()
                else:
                    self.pokemonenemy5.choosepokemon(self.pokemonenemy5.chosenpokemon)
                if self.pokemonenemy6.health == 'FNT':
                    self.pokemonenemy6.choosepokemon()
                else:
                    self.pokemonenemy6.choosepokemon(self.pokemonenemy6.chosenpokemon)
                self.activepokemonplayer = None
                self.activepokemonenemy = None
            self.update_ha_state()
            return
                
        if self.activepokemonplayer is None or self.activepokemonplayer.health == 'FNT':
            if self.pokemonplayer1.health != 'FNT':
                self.activepokemonplayer = self.pokemonplayer1
            elif self.pokemonplayer2.health != 'FNT':
                self.activepokemonplayer = self.pokemonplayer2
            elif self.pokemonplayer3.health != 'FNT':
                self.activepokemonplayer = self.pokemonplayer3
            elif self.pokemonplayer4.health != 'FNT':
                self.activepokemonplayer = self.pokemonplayer4
            elif self.pokemonplayer5.health != 'FNT':
                self.activepokemonplayer = self.pokemonplayer5
            else:
                self.activepokemonplayer = self.pokemonplayer6
            if self.activepokemonplayer.health != 'FNT':
                self.battlestate = self.person1.pname + " chose " + self.activepokemonplayer.pokemonname
                self.lastmove = None
                self.update_ha_state()
                return
        
        if self.activepokemonenemy is None or self.activepokemonenemy.health == 'FNT':
            if self.pokemonenemy1.health != 'FNT':
                self.activepokemonenemy = self.pokemonenemy1
            elif self.pokemonenemy2.health != 'FNT':
                self.activepokemonenemy = self.pokemonenemy2
            elif self.pokemonenemy3.health != 'FNT':
                self.activepokemonenemy = self.pokemonenemy3
            elif self.pokemonenemy4.health != 'FNT':
                self.activepokemonenemy = self.pokemonenemy4
            elif self.pokemonenemy5.health != 'FNT':
                self.activepokemonenemy = self.pokemonenemy5
            else:
                self.activepokemonenemy = self.pokemonenemy6
            if self.activepokemonplayer.health != 'FNT':
                self.battlestate = self.person2.pname + " chose " + self.activepokemonplayer.pokemonname
                self.lastmove = None
                self.update_ha_state()
                return
        
        # outcome
        if self.activepokemonenemy.health == 'FNT':
            self.battlestate = self.person1.pname + " defeated " + self.person2.pname
            self.person1.victories += 1
            if self.person1.victories % 25 == 0:
                self.person1.badges += 1
            self.resetting = 5
                
            if self.pokemonplayer1.health != 'FNT':
                self.pokemonplayer1.level += 1
            if self.pokemonplayer2.health != 'FNT':
                self.pokemonplayer2.level += 1
            if self.pokemonplayer3.health != 'FNT':
                self.pokemonplayer3.level += 1
            if self.pokemonplayer4.health != 'FNT':
                self.pokemonplayer4.level += 1
            if self.pokemonplayer5.health != 'FNT':
                self.pokemonplayer5.level += 1
            if self.pokemonplayer6.health != 'FNT':
                self.pokemonplayer6.level += 1
            self.update_ha_state()
            return
        
        if self.activepokemonplayer.health == 'FNT':
            self.battlestate = self.person2.pname + " defeated " + self.person1.pname
            self.person2.victories += 1
            if self.person2.victories % 25 == 0:
                self.person2.badges += 1
            self.resetting = 5
                
            if self.pokemonenemy1.health != 'FNT':
                self.pokemonenemy1.level += 1
            if self.pokemonenemy2.health != 'FNT':
                self.pokemonenemy2.level += 1
            if self.pokemonenemy3.health != 'FNT':
                self.pokemonenemy3.level += 1
            if self.pokemonenemy4.health != 'FNT':
                self.pokemonenemy4.level += 1
            if self.pokemonenemy5.health != 'FNT':
                self.pokemonenemy5.level += 1
            if self.pokemonenemy6.health != 'FNT':
                self.pokemonenemy6.level += 1
            self.update_ha_state()    
            return
            
        if self.lastmove is None:
            if self.activepokemonplayer.battleSpeed >= self.activepokemonenemy.battleSpeed:
                self.attacker = self.activepokemonplayer
                self.victim = self.activepokemonenemy
            else:
                self.attacker = self.activepokemonenemy
                self.victim = self.activepokemonplayer
            self.lastmove = self.attacker.pokemonname
        else:
            if self.activepokemonplayer.battleSpeed >= self.activepokemonenemy.battleSpeed:
                self.victim = self.activepokemonplayer
                self.attacker = self.activepokemonenemy
            else:
                self.victim = self.activepokemonenemy
                self.attacker = self.activepokemonplayer
            self.lastmove = None
        
        _LOGGER.info('POKEMON: attacking')
        self.createattack()
            
        _LOGGER.info('POKEMON: attack calculated')
        self.battlestate = self.attacker.pokemonname + " attacked " + self.victim.pokemonname + " with " + self.attackedwith + " doing " + str(self.damage) + " damage"

        self.update_ha_state()

###############################################################################        
class Move(object):
    def __init__(self, move):
        moveInfo = []
        # Only reading through the file if no information is stored in the Moves Dictionary
        if len(MOVES_DICTIONARY) == 0:
            fin = open(os.path.join(os.getcwd(),"pokemonmoves.csv"), 'r')
            for line in fin:
                line = line.strip()
                movelist = line.split(",")
                MOVES_DICTIONARY[movelist[1]] = movelist  # The name of the move is the key while the rest of the
                # list is the value

            fin.close()

        # Finding the matching key in the dictionary, then assigning the list to a variable called moveInfo
        for key in MOVES_DICTIONARY:
            if key.lower() == move.lower():
                moveInfo = MOVES_DICTIONARY[key]


        # ATTRIBUTES
        # ID info
        self.moveInfo = moveInfo
        self.id = moveInfo[0]  # Move's number id
        self.name = moveInfo[1]  # Move's name

        # Description
        self.description = moveInfo[2]  # Move description
        self.type = moveInfo[3]  # Move type
        self.kind = moveInfo[4]  # Can be special, physical, or stat-changing

        # For in-battle calculations
        self.power = int(moveInfo[5])  # Move's base damage
        self.accuracy = moveInfo[6]
        self.pp = int(moveInfo[7])

    # METHODS
    # str method
    def __str__(self):
        msg = self.name + " " + str(self.power)
        return msg


    # GET Methods
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getType(self):
        return self.type

    def getKind(self):
        return self.kind

    def getPower(self):
        return self.power

    def getAccuracy(self):
        return self.accuracy

    def getPP(self):
        return self.pp

    # SET Methods
    def setName(self, name):
        self.name = name

    def setType(self, type):
        self.type = type

    def setPower(self, power):
        self.power = power

    def setAccuracy(self, accuracy):
        self.accuracy = accuracy

    def setPP(self, pp):
        self.pp = pp
