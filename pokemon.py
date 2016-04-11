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
import shutil
import os.path
import requests

from math import floor

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers.event import track_utc_time_change
from homeassistant.helpers.entity import generate_entity_id
import homeassistant.loader as loader

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Ash"
DEFAULT_ENEMY = "Gary"

DOMAIN = "pokemon"

ENTITY_ID_FORMAT = DOMAIN + '.{}'

TOTALPOKEDEX = 721

NUMBEROFVICTORIESPERBADGE = 1

POKEDEX = []
IV = 30
EV = 85
STAB = 1.5
POKEMONDICTIONARY = {}
POKEMONDICTIONARYGEN1 = {}
POKEMONDICTIONARYGEN2 = {}
POKEMONDICTIONARYGEN3 = {}
POKEMONDICTIONARYGEN4 = {}
POKEMONDICTIONARYGEN5 = {}
POKEMONDICTIONARYGEN6 = {}
TYPEDICTIONARY = {}
MOVES_DICTIONARY = {}
MOVES_PER_LEVELDICTIONARY = {}
POKEMON_DIR = None

def setup(hass, config):
    """ Set up the iCloud Scanner. """
    
    if config.get(DOMAIN) is None:
        return False
        
    POKEMON_DIR = hass.config.path(DOMAIN)

    if not os.path.exists(POKEMON_DIR):
        os.makedirs(POKEMON_DIR)
        
    picture_dir = os.path.join(hass.config.path('www'), DOMAIN)

    if not os.path.exists(picture_dir):
        os.makedirs(picture_dir)
        
    full_filename = "pokemon.csv"
    file_path = os.path.join(POKEMON_DIR, full_filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    if not os.path.isfile(file_path):
        url = "https://raw.githubusercontent.com/Bart274/pokemonHA/master/pokemon.csv"
        pokemoncsv = requests.get(url, stream=True)
        if pokemoncsv.status_code == 200:
            with open(file_path, 'wb') as opened_file:
                pokemoncsv.raw.decode_content = True
                shutil.copyfileobj(pokemoncsv.raw, opened_file)
        else:
            err = "An error happened when requesting the pokemon.csv!"
            _LOGGER.error(err)
            return False
    full_filename = "pokemontypeadvantages.csv"
    file_path = os.path.join(POKEMON_DIR, full_filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    if not os.path.isfile(file_path):
        url = "https://raw.githubusercontent.com/Bart274/pokemonHA/master/pokemontypeadvantages.csv"
        pokemontypeadvantagescsv = requests.get(url, stream=True)
        if pokemontypeadvantagescsv.status_code == 200:
            with open(file_path, 'wb') as opened_file:
                pokemontypeadvantagescsv.raw.decode_content = True
                shutil.copyfileobj(pokemontypeadvantagescsv.raw, opened_file)
        else:
            err = "An error happened when requesting the pokemontypeadvantages.csv!"
            _LOGGER.error(err)
            return False
    full_filename = "pokemonmoves.csv"
    file_path = os.path.join(POKEMON_DIR, full_filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    if not os.path.isfile(file_path):
        url = "https://raw.githubusercontent.com/Bart274/pokemonHA/master/pokemonmoves.csv"
        pokemonmovescsv = requests.get(url, stream=True)
        if pokemonmovescsv.status_code == 200:
            with open(file_path, 'wb') as opened_file:
                pokemonmovescsv.raw.decode_content = True
                shutil.copyfileobj(pokemonmovescsv.raw, opened_file)
        else:
            err = "An error happened when requesting the pokemonmoves.csv!"
            _LOGGER.error(err)
            return False
    full_filename = "pokemonmovesperlevel.csv"
    file_path = os.path.join(POKEMON_DIR, full_filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    if not os.path.isfile(file_path):
        url = "https://raw.githubusercontent.com/Bart274/pokemonHA/master/pokemonmovesperlevel.csv"
        pokemoncsv = requests.get(url, stream=True)
        if pokemoncsv.status_code == 200:
            with open(file_path, 'wb') as opened_file:
                pokemoncsv.raw.decode_content = True
                shutil.copyfileobj(pokemoncsv.raw, opened_file)
        else:
            err = "An error happened when requesting the pokemon.csv!"
            _LOGGER.error(err)
            return False
        
    fin = open(os.path.join(POKEMON_DIR,"pokemon.csv"), 'r')
    # Creating a dictionary with each Pokemon's name as a key
    for line in fin:
        line = line.strip()
        pokeList = line.split(",")
        if pokeList[17] == 'yes' and pokeList[0].strip(' \t\n\r') != '' and pokeList[0].lower().strip(' \t\n\r') != 'nat':
            POKEMONDICTIONARY[pokeList[0]] = pokeList
            if int(pokeList[14]) <= 1:
                POKEMONDICTIONARYGEN1[pokeList[0]] = pokeList
            if int(pokeList[14]) <= 2:
                POKEMONDICTIONARYGEN2[pokeList[0]] = pokeList
            if int(pokeList[14]) <= 3:
                POKEMONDICTIONARYGEN3[pokeList[0]] = pokeList
            if int(pokeList[14]) <= 4:
                POKEMONDICTIONARYGEN4[pokeList[0]] = pokeList
            if int(pokeList[14]) <= 5:
                POKEMONDICTIONARYGEN5[pokeList[0]] = pokeList
            if int(pokeList[14]) <= 6:
                POKEMONDICTIONARYGEN6[pokeList[0]] = pokeList
    fin.close()

    # Taking the keys from above, turning them into a list, and sorting them
    for key in POKEMONDICTIONARY:
        POKEDEX.append(POKEMONDICTIONARY[key][0].lower())
        POKEDEX.sort()
        
    # Reading "Type Advantages.csv" file to determine type advantages and the damage modifier
    # Stores the line number in the csv as the key and a list giving information about type advantage for the value
    fin = open(os.path.join(POKEMON_DIR,"pokemontypeadvantages.csv"), 'r')
    for line in fin:
        line = line.strip()
        typeList = line.split(",")
        TYPEDICTIONARY[typeList[0]] = typeList
        # This list contains a number in the first position, the attack type in the second, the defending type in the third,
        # and the appropriate damage multiplier in the fourth
    fin.close()

    fin = open(os.path.join(POKEMON_DIR,"pokemonmoves.csv"), 'r')
    for line in fin:
        line = line.strip()
        movelist = line.split(",")
        MOVES_DICTIONARY[movelist[0]] = movelist  # The name of the move is the key while the rest of the
        # list is the value
    fin.close()
    
    fin = open(os.path.join(POKEMON_DIR,"pokemonmovesperlevel.csv"), 'r')
    for line in fin:
        line = line.strip()
        movelist = line.split(",")
        MOVES_PER_LEVELDICTIONARY[int(movelist[0]) * 1000 + int(movelist[1])] = movelist  # The name of the move is the key while the rest of the
        # list is the value
    fin.close()
    
    pokemon_config = config[DOMAIN]

    # Get the username and password from the configuration
    playername = pokemon_config.get('playername', DEFAULT_NAME)
    enemyname = pokemon_config.get('enemyname', DEFAULT_ENEMY)
        
    player = Pokemon(hass, 'player', playername, picture_dir)
    player.update_ha_state()
        
    enemy = Pokemon(hass, 'enemy', enemyname, picture_dir)
    enemy.update_ha_state()
        
    pokemonplayer1 = Pokemon(hass, 'pokemon', '1', picture_dir, player, enemy)
    pokemonplayer1.update_ha_state()
        
    pokemonplayer2 = Pokemon(hass, 'pokemon', '2', picture_dir, player, enemy)
    pokemonplayer2.update_ha_state()
       
    pokemonplayer3 = Pokemon(hass, 'pokemon', '3', picture_dir, player, enemy)
    pokemonplayer3.update_ha_state()
        
    pokemonplayer4 = Pokemon(hass, 'pokemon', '4', picture_dir, player, enemy)
    pokemonplayer4.update_ha_state()
        
    pokemonplayer5 = Pokemon(hass, 'pokemon', '5', picture_dir, player, enemy)
    pokemonplayer5.update_ha_state()
        
    pokemonplayer6 = Pokemon(hass, 'pokemon', '6', picture_dir, player, enemy)
    pokemonplayer6.update_ha_state()
        
    pokemonenemy1 = Pokemon(hass, 'pokemon', '1', picture_dir, enemy, player)
    pokemonenemy1.update_ha_state()
        
    pokemonenemy2 = Pokemon(hass, 'pokemon', '2', picture_dir, enemy, player)
    pokemonenemy2.update_ha_state()
        
    pokemonenemy3 = Pokemon(hass, 'pokemon', '3', picture_dir, enemy, player)
    pokemonenemy3.update_ha_state()
        
    pokemonenemy4 = Pokemon(hass, 'pokemon', '4', picture_dir, enemy, player)
    pokemonenemy4.update_ha_state()
        
    pokemonenemy5 = Pokemon(hass, 'pokemon', '5', picture_dir, enemy, player)
    pokemonenemy5.update_ha_state()
        
    pokemonenemy6 = Pokemon(hass, 'pokemon', '6', picture_dir, enemy, player)
    pokemonenemy6.update_ha_state()
        
    pokemonbattle = Pokemon(hass, 'battle', 'battle', picture_dir, player, enemy,
                            pokemonplayer1, pokemonplayer2, pokemonplayer3,
                            pokemonplayer4, pokemonplayer5, pokemonplayer6,
                            pokemonenemy1, pokemonenemy2, pokemonenemy3,
                            pokemonenemy4, pokemonenemy5, pokemonenemy6)
    pokemonbattle.update_ha_state()
    
    group = loader.get_component('group')
    group.Group(hass, 'Pokemon', [
        pokemonbattle.entity_id, player.entity_id, pokemonplayer1.entity_id,
        pokemonplayer2.entity_id, pokemonplayer3.entity_id,
        pokemonplayer4.entity_id, pokemonplayer5.entity_id,
        pokemonplayer6.entity_id, enemy.entity_id, pokemonenemy1.entity_id,
        pokemonenemy2.entity_id, pokemonenemy3.entity_id,
        pokemonenemy4.entity_id, pokemonenemy5.entity_id,
        pokemonenemy6.entity_id])
        
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
    def __init__(self, hass, type, name, picture_dir, person1=None,
                 person2=None, pokemonplayer1=None, pokemonplayer2=None,
                 pokemonplayer3=None, pokemonplayer4=None, pokemonplayer5=None,
                 pokemonplayer6=None, pokemonenemy1=None, pokemonenemy2=None,
                 pokemonenemy3=None, pokemonenemy4=None, pokemonenemy5=None,
                 pokemonenemy6=None):
        self.hass = hass
        self.type = type
        if type == 'pokemon':
            self.pname = type + name
        else:
            self.pname = name
        self.person1 = person1
        self.person2 = person2
        self.picture_dir = picture_dir
        self.health = 100
        self._state = None
        self.lastmove = None
        self.attackedwith = None
        self.damage = 0
        self.resetting = 1
        self.victories = 0
        self.badges = 0
        self.pokedex = 0
        self.pokedexcaught = 0
        self.pokedexseen = 0
        self.caughtpokemon = []
        self.seenpokemon = []
        self.level = 1
        self.won = False
        self.attacker = None
        self.victim = None
        self.activepokemonplayer = None
        self.activepokemonenemy = None
        self.battlestate = "Battle beginning"
        self.pokemonplayer1 = pokemonplayer1
        if self.pokemonplayer1 is not None:
            self.pokemonplayer1.choosepokemon()
            self.pokemonplayer1.won = True
        self.pokemonplayer2 = pokemonplayer2
        if self.pokemonplayer2 is not None:
            self.pokemonplayer2.choosepokemon()
            self.pokemonplayer2.won = True
        self.pokemonplayer3 = pokemonplayer3
        if self.pokemonplayer3 is not None:
            self.pokemonplayer3.choosepokemon()
            self.pokemonplayer3.won = True
        self.pokemonplayer4 = pokemonplayer4
        if self.pokemonplayer4 is not None:
            self.pokemonplayer4.choosepokemon()
            self.pokemonplayer4.won = True
        self.pokemonplayer5 = pokemonplayer5
        if self.pokemonplayer5 is not None:
            self.pokemonplayer5.choosepokemon()
            self.pokemonplayer5.won = True
        self.pokemonplayer6 = pokemonplayer6
        if self.pokemonplayer6 is not None:
            self.pokemonplayer6.choosepokemon()
            self.pokemonplayer6.won = True
        self.pokemonenemy1 = pokemonenemy1
        if self.pokemonenemy1 is not None:
            self.pokemonenemy1.choosepokemon()
            self.pokemonenemy1.won = True
        self.pokemonenemy2 = pokemonenemy2
        if self.pokemonenemy2 is not None:
            self.pokemonenemy2.choosepokemon()
            self.pokemonenemy2.won = True
        self.pokemonenemy3 = pokemonenemy3
        if self.pokemonenemy3 is not None:
            self.pokemonenemy3.choosepokemon()
            self.pokemonenemy3.won = True
        self.pokemonenemy4 = pokemonenemy4
        if self.pokemonenemy4 is not None:
            self.pokemonenemy4.choosepokemon()
            self.pokemonenemy4.won = True
        self.pokemonenemy5 = pokemonenemy5
        if self.pokemonenemy5 is not None:
            self.pokemonenemy5.choosepokemon()
            self.pokemonenemy5.won = True
        self.pokemonenemy6 = pokemonenemy6
        if self.pokemonenemy6 is not None:
            self.pokemonenemy6.choosepokemon()
            self.pokemonenemy6.won = True
        
        self.fainted = True
        self.active = False
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
        self.generation = None
        self.height = None
        self.weight = None
        
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
                "Name": self.pname,
                "Victories": self.victories,
                "Badges": self.badges,
                "Pokedex completed": self.pokedex,
                "Pokemon caught": self.pokedexcaught,
                "Pokemon seen": self.pokedexseen
            }
        elif self.type == 'pokemon':
            if self.person1.type == 'enemy':
                if not self.active and not self.fainted:
                    return {
                        "Health": '?',
                        "Level": '?',
                        "Owner": self.person1.pname,
                        "Generation": '?',
                        "Type": '?',
                        "Attack": '?',
                        "Defense": '?',
                        "Special Attack": '?',
                        "Special Defense": '?',
                        "Speed": '?',
                        "Height": '?',
                        "Weight": '?'
                    }
            
            temptype = self.type1
            if self.type2 is not None and self.type2.strip(' \t\n\r') != '':
                temptype += '/' + self.type2
            if self.chosenpokemon is None or self.active is False:
                return {
                    "Health": self.health,
                    "Level": self.level,
                    "Owner": self.person1.pname,
                    "Generation": self.generation,
                    "Type": temptype,
                    "Attack": self.battleATK,
                    "Defense": self.battleDEF,
                    "Special Attack": self.battleSpATK,
                    "Special Defense": self.battleSpDEF,
                    "Speed": self.battleSpeed,
                    "Height": self.height,
                    "Weight": self.weight
                }
            else:
                tempentitypicture = "/local/" + DOMAIN + "/"
                full_filename = self.__id.zfill(3) +".gif"
                file_path = os.path.join(self.picture_dir, full_filename)
                if os.path.isfile(file_path):
                    tempentitypicture += full_filename
                else:
                    tempentitypicture += "missingpicture.jpg"
                return {
                    "Health": self.health,
                    "Level": self.level,
                    "Owner": self.person1.pname,
                    "Generation": self.generation,
                    "Type": temptype,
                    "Attack": self.battleATK,
                    "Defense": self.battleDEF,
                    "Special Attack": self.battleSpATK,
                    "Special Defense": self.battleSpDEF,
                    "Speed": self.battleSpeed,
                    "Height": self.height,
                    "Weight": self.weight,
                    "entity_picture": tempentitypicture
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
                "Attacker": tempattacker,
                "Victim": tempvictim,
                "Active pokemon player": tempapp,
                "Active pokemon enemy": tempape,
                "Action": self.battlestate
            }
            
    @property
    def hidden(self):
        """If device should be hidden."""
        """ returns the friendlyname of the icloud tracker """
        if self.type == 'pokemon':
            if self.chosenpokemon is None:
                return True
            else:
                return self.fainted
        else:
            return False
    
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
                return 'mdi:sword'
        else:
            if not self.active:
                if self.chosenpokemon is None or self.fainted:
                    return 'mdi:ghost'
                elif not self.fainted:
                    return 'mdi:pokeball'
    
    @property
    def state(self):
        """Return the state of the device."""
        if self.type == 'player' or self.type == 'enemy':
            self._state = self.victories
        elif self.type == 'pokemon':
            tempname = self.pokemonname
            if self.person1.type == 'enemy':
                if not self.active and not self.fainted:
                    tempname = '?' 
            self._state = tempname
        else:
            self._state = self.battlestate
            
        return self._state
        
    @property
    def unit_of_measurement(self):
        """ Unit of measurement of this entity """
        if self.type == 'player' or self.type == 'enemy':
            return "WINS"
            
    def levelup(self):
        self.level += 1
        self.level = min(self.level, 100)
        self.battleHP = round((self.__hp * 2 + IV + (EV / 4)) * self.level / 100 + 10 + self.level,0)
        self.battleATK = round(((self.__atk * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleDEF = round(((self.__defense * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleSpATK = round(((self.__spAtk * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleSpDEF = round(((self.__spDef * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleSpeed = round(((self.__speed * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.originalATK = self.battleATK
        self.originalDEF = self.battleDEF
        self.originalSpATK = self.battleSpATK
        self.originalSpDEF = self.battleSpDEF
        self.originalSpeed = self.battleSpeed
        self.health = self.battleHP
        self.atkStage = 0
        self.defStage = 0
        self.spAtkStage = 0
        self.spDefStage = 0
        self.speedStage = 0
        self.movelist = []
        x = 1
        while x <= self.level:
            key = int(self.__id) * 1000 + x
            if key in MOVES_PER_LEVELDICTIONARY:
                moveInfo = MOVES_PER_LEVELDICTIONARY[key]
                if moveInfo[2] != '':
                    self.movelist.append(moveInfo[2])
                if moveInfo[3] != '':
                    self.movelist.append(moveInfo[3])
                if moveInfo[4] != '':
                    self.movelist.append(moveInfo[4])
                if moveInfo[5] != '':
                    self.movelist.append(moveInfo[5])
                if moveInfo[6] != '':
                    self.movelist.append(moveInfo[6])
                if moveInfo[7] != '':
                    self.movelist.append(moveInfo[7])
                if moveInfo[8] != '':
                    self.movelist.append(moveInfo[8])
                if moveInfo[9] != '':
                    self.movelist.append(moveInfo[9])
                if moveInfo[10] != '':
                    self.movelist.append(moveInfo[10])
                if moveInfo[11] != '':
                    self.movelist.append(moveInfo[11])
                if moveInfo[12] != '':
                    self.movelist.append(moveInfo[12])
                if moveInfo[13] != '':
                    self.movelist.append(moveInfo[13])
                if moveInfo[14] != '':
                    self.movelist.append(moveInfo[14])
                if moveInfo[15] != '':
                    self.movelist.append(moveInfo[15])
            x += 1
        
    def choosepokemon(self, chosenpokemon=None):
        if chosenpokemon is None:
            if floor(self.person1.badges / 8) == 0:
                chosenpokemon = random.choice(list(POKEMONDICTIONARYGEN1))
            elif floor(self.person1.badges / 8) == 1:
                chosenpokemon = random.choice(list(POKEMONDICTIONARYGEN2))
            elif floor(self.person1.badges / 8) == 2:
                chosenpokemon = random.choice(list(POKEMONDICTIONARYGEN3))
            elif floor(self.person1.badges / 8) == 3:
                chosenpokemon = random.choice(list(POKEMONDICTIONARYGEN4))
            elif floor(self.person1.badges / 8) == 4:
                chosenpokemon = random.choice(list(POKEMONDICTIONARYGEN5))
            elif floor(self.person1.badges / 8) == 5:
                chosenpokemon = random.choice(list(POKEMONDICTIONARYGEN6))
            else:
                chosenpokemon = random.choice(list(POKEMONDICTIONARY))
            self.level = 1
        self.chosenpokemon = chosenpokemon
        _LOGGER.info("POKEMON: chosenpokemon: %s", self.chosenpokemon)
        if self.chosenpokemon in POKEMONDICTIONARY:
            pokemonInfo = POKEMONDICTIONARY[self.chosenpokemon]
        
        if self.chosenpokemon not in self.person1.caughtpokemon:
            self.person1.caughtpokemon.append(self.chosenpokemon)
            self.person1.pokedexcaught += 1
            self.person1.pokedex = str(round(self.person1.pokedexcaught / TOTALPOKEDEX * 100, 2)) + '%'
        
        if self.chosenpokemon not in self.person1.seenpokemon:
            self.person1.seenpokemon.append(self.chosenpokemon)
            self.person1.pokedexseen += 1
                
        
        self.fainted = False
        self.active = False
        self.won = False
        
        # ATTRIBUTES
        # Referring to the pokemonInfo list to fill in the rest of the attributes
        # ID Info
        self.__id = pokemonInfo[0]
        self.pokemonname = pokemonInfo[1]
        
        full_filename = self.__id.zfill(3) +".gif"
        file_path = os.path.join(self.picture_dir, full_filename)
        if not os.path.isfile(file_path):
            url = "https://raw.githubusercontent.com/Bart274/pokemonHA/master/Sprites/" + full_filename
            picture = requests.get(url, stream=True)
            if picture.status_code == 200:
                with open(file_path, 'wb') as opened_file:
                    picture.raw.decode_content = True
                    shutil.copyfileobj(picture.raw, opened_file)

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
        #self.battleHP = int(self.__hp + (0.5*IV) + (0.125*EV) + 60)
        #self.battleATK = self.__atk + (0.5*IV) + (0.125*EV) + 5
        #self.battleDEF = self.__defense + (0.5*IV) + (0.125*EV) + 5
        #self.battleSpATK = self.__spAtk + (0.5*IV) + (0.125*EV) + 5
        #self.battleSpDEF = self.__spDef + (0.5*IV) + (0.125*EV) + 5
        #self.battleSpeed = self.__speed + (0.5*IV) + (0.125*EV) + 5
        self.battleHP = round((self.__hp * 2 + IV + (EV / 4)) * self.level / 100 + 10 + self.level,0)
        self.battleATK = round(((self.__atk * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleDEF = round(((self.__defense * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleSpATK = round(((self.__spAtk * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleSpDEF = round(((self.__spDef * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)
        self.battleSpeed = round(((self.__speed * 2 + IV + (EV / 4)) * self.level / 100 + 5),0)

        # These variables are used to just hold the values of the original stat for stat modification purposes
        #self.originalATK = self.__atk + (0.5*IV) + (0.125*EV) + 5
        #self.originalDEF = self.__defense + (0.5*IV) + (0.125*EV) + 5
        #self.originalSpATK = self.__spAtk + (0.5*IV) + (0.125*EV) + 5
        #self.originalSpDEF = self.__spDef + (0.5*IV) + (0.125*EV) + 5
        #self.originalSpeed = self.__speed + (0.5*IV) + (0.125*EV) + 5
        self.originalATK = self.battleATK
        self.originalDEF = self.battleDEF
        self.originalSpATK = self.battleSpATK
        self.originalSpDEF = self.battleSpDEF
        self.originalSpeed = self.battleSpeed

        self.health = self.battleHP

        # In Battle Stats
        # Raised or lowered based on different moves used in battle. Affects the in battle stats (more info in the Overview of Battle Mechanics in readme.txt)
        self.atkStage = 0
        self.defStage = 0
        self.spAtkStage = 0
        self.spDefStage = 0
        self.speedStage = 0
        
        self.movelist = []
        x = 1
        while x <= self.level:
            key = int(self.__id) * 1000 + x
            if key in MOVES_PER_LEVELDICTIONARY:
                moveInfo = MOVES_PER_LEVELDICTIONARY[key]
                if moveInfo[2] != '':
                    self.movelist.append(moveInfo[2])
                if moveInfo[3] != '':
                    self.movelist.append(moveInfo[3])
                if moveInfo[4] != '':
                    self.movelist.append(moveInfo[4])
                if moveInfo[5] != '':
                    self.movelist.append(moveInfo[5])
                if moveInfo[6] != '':
                    self.movelist.append(moveInfo[6])
                if moveInfo[7] != '':
                    self.movelist.append(moveInfo[7])
                if moveInfo[8] != '':
                    self.movelist.append(moveInfo[8])
                if moveInfo[9] != '':
                    self.movelist.append(moveInfo[9])
                if moveInfo[10] != '':
                    self.movelist.append(moveInfo[10])
                if moveInfo[11] != '':
                    self.movelist.append(moveInfo[11])
                if moveInfo[12] != '':
                    self.movelist.append(moveInfo[12])
                if moveInfo[13] != '':
                    self.movelist.append(moveInfo[13])
                if moveInfo[14] != '':
                    self.movelist.append(moveInfo[14])
                if moveInfo[15] != '':
                    self.movelist.append(moveInfo[15])
            x += 1

        _LOGGER.info("POKEMON: movelist: %s", self.movelist)
        
        self.generation = pokemonInfo[14]
        
        self.height = int(pokemonInfo[15])
        self.weight = int(pokemonInfo[16])
        
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
        msg = self.pokemonname + " lost " + str(lostHP) + " HP! "
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
        multiplier = 1
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
        if self.attacker.person1.type == 'player':
            tempMsg += self.attacker.useMove(move)
        else:
            tempMsg += "Foe's " + self.attacker.useMove(move)

        # ATK/DEF or SpATK/SpDEF or Status? Using the Pokemon damage formula
        # If the move is "Physical", the damage formula will take into account attack and defense
        if move.kind == "Physical":
            self.damage = int((((2*self.attacker.getLevel()) + 10)/250 * (self.attacker.battleATK/self.victim.battleDEF) * move.getPower() + 2) * modifier)
            if self.attacker.person1.type == 'player':
                tempMsg += "\nFoe's " + self.victim.loseHP(self.damage)
            else:
                tempMsg += "\n" + self.victim.loseHP(self.damage)
        # If the move is "Special", the damage formula will take into account special attack and special defense
        elif move.kind == "Special":
            self.damage = int((((2*self.attacker.getLevel()) + 10)/250 * (self.attacker.battleSpATK/self.victim.battleSpDEF) * move.getPower() + 2) * modifier)
            if self.attacker.person1.type == 'player':
                tempMsg += "\nFoe's " + self.victim.loseHP(self.damage)
            else:
                tempMsg += "\n" + self.victim.loseHP(self.damage)

        # Stat Changing moves
        else:
            # If the move is stat-changing, it does 0 damage and the modifier is set to 1 (so it doesn't return super effective or not very effective)
            self.damage = 0
            modifier = 1

            # Going through each kind of different stat change based on the move type
            if move.kind == "a-":
                self.victim.atkStage -= 1
                self.victim.battleATK = round(self.victim.originalATK * self.statMod(self.victim.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s attack fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s attack fell! "
                    
            elif move.kind == "a=d":
                tempattack = self.attacker.atkStage
                self.attacker.atkStage = self.attacker.defStage
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                self.attacker.defStage = tempattack
                self.attacker.battleDEF = round(self.attacker.originalDEF * self.statMod(self.attacker.defStage),0)
                tempattack = self.attacker.spAtkStage
                self.attacker.spAtkStage = self.attacker.spDefStage
                self.attacker.battleSpATK = round(self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage),0)
                self.attacker.spDefStage = tempattack
                self.attacker.battleSpDef = round(self.attacker.originalSpDEF * self.statMod(self.attacker.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s attack and defense are changed! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s attack and defense are changed! "
            
            elif move.kind == "a><a":
                tempattack = self.attacker.atkStage
                self.attacker.atkStage = self.victim.atkStage
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                self.victim.atkStage = tempattack
                self.victim.battleATK = round(self.victim.originalATK * self.statMod(self.victim.atkStage),0)
                tempattack = self.attacker.spAtkStage
                self.attacker.spAtkStage = self.victim.spAtkStage
                self.attacker.battleSpATK = round(self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage),0)
                self.victim.spAtkStage = tempattack
                self.victim.battleSpATK = round(self.victim.originalSpATK * self.statMod(self.victim.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + " changed attack stats with Foe's " + self.victim.pokemonname + "! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + " changed attack stats with " + self.victim.pokemonname + "! "

            elif move.kind == "d><d":
                tempattack = self.attacker.defStage
                self.attacker.defStage = self.victim.defStage
                self.attacker.battleDEF = round(self.attacker.originalDEF * self.statMod(self.attacker.defStage),0)
                self.victim.defStage = tempattack
                self.victim.battleDEF = round(self.victim.originalDEF * self.statMod(self.victim.defStage),0)
                tempattack = self.attacker.spDefStage
                self.attacker.spDefStage = self.victim.spDefStage
                self.attacker.battleSpDef = round(self.attacker.originalSpDEF * self.statMod(self.attacker.spDefStage),0)
                self.victim.spDefStage = tempattack
                self.victim.battleSpDef = round(self.victim.originalSpDEF * self.statMod(self.victim.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + " changed defense stats with Foe's " + self.victim.pokemonname + "! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + " changed defense stats with " + self.victim.pokemonname + "! "

            elif move.kind == "avgatt-":
                tempattack = floor((self.victim.atkStage + self.victim.spAtkStage) / 2)
                self.victim.atkStage = tempattack
                self.victim.battleATK = round(self.victim.originalATK * self.statMod(self.victim.atkStage),0)
                self.victim.spAtkStage = tempattack
                self.victim.battleSpATK = round(self.victim.originalSpATK * self.statMod(self.victim.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s attack and special attack averaged! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s attack and special attack averaged! "

            elif move.kind == "avgdef-":
                tempattack = floor((self.victim.defStage + self.victim.spDefStage) / 2)
                self.victim.defStage = tempattack
                self.victim.battleDEF = round(self.victim.originalDEF * self.statMod(self.victim.defStage),0)
                self.victim.spDefStage = tempattack
                self.victim.battleSpDef = round(self.victim.originalSpDEF * self.statMod(self.victim.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s defense and special defense averaged! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s defense and special defense averaged! "

            elif move.kind == "a+":
                self.attacker.atkStage +=1
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s attack rose! "

            elif move.kind == "d+":
                self.attacker.defStage +=1
                self.attacker.battleDEF = round(self.attacker.originalDEF * self.statMod(self.attacker.defStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s defense rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s defense rose! "
                    
            elif move.kind == "d+++":
                self.attacker.defStage +=3
                self.attacker.battleDEF = round(self.attacker.originalDEF * self.statMod(self.attacker.defStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s defense sharply rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s defense sharply rose! "

            elif move.kind == "sa+":
                self.attacker.spAtkStage +=1
                self.attacker.battleSpATK = round(self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special attack rose! "

            elif move.kind == "sa-":
                self.victim.spAtkStage -=1
                self.victim.battleSpATK = round(self.victim.originalSpATK * self.statMod(self.victim.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s special attack fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s special attack fell! "

            elif move.kind == "sa--":
                self.victim.spAtkStage -=2
                self.victim.battleSpATK = round(self.victim.originalSpATK * self.statMod(self.victim.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s special attack greatly fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s special attack greatly fell! "

            elif move.kind == "sd+":
                self.attacker.spDefStage +=1
                self.attacker.battleSpDef = round(self.attacker.originalSpDEF * self.statMod(self.attacker.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special defense rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special defense rose! "

            elif move.kind == "s+":
                self.attacker.speedStage +=1
                self.attacker.battleSpeed = round(self.attacker.originalSpeed * self.statMod(self.attacker.speedStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s speed rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s speed rose! "

            elif move.kind == "s++":
                self.attacker.speedStage +=2
                self.attacker.battleSpeed = round(self.attacker.originalSpeed * self.statMod(self.attacker.speedStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s speed greatly rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s speed greatly rose! "

            elif move.kind == "s++w/2":
                self.attacker.speedStage +=2
                self.attacker.battleSpeed = round(self.attacker.originalSpeed * self.statMod(self.attacker.speedStage),0)
                self.attacker.weight = floor(self.attacker.weight / 2)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s speed greatly rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s speed greatly rose! "
                    
            elif move.kind == "sa+sd+s+":
                self.attacker.spAtkStage +=1
                self.attacker.battleSpATK = round(self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special attack rose! "
                self.attacker.spDefStage +=1
                self.attacker.battleSpDef = round(self.attacker.originalSpDEF * self.statMod(self.attacker.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special defense rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special defense rose! "
                self.attacker.speedStage +=1
                self.attacker.battleSpeed = round(self.attacker.originalSpeed * self.statMod(self.attacker.speedStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s speed rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s speed rose! "
                    
            elif move.kind == "a++sa++s++":
                self.attacker.atkStage +=2
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s attack greatly rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s attack greatly rose! "
                self.attacker.spAtkStage +=2
                self.attacker.battleSpATK = round(self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special attack greatly rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special attack greatly rose! "
                self.attacker.speedStage +=2
                self.attacker.battleSpeed = round(self.attacker.originalSpeed * self.statMod(self.attacker.speedStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s speed greatly rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s speed greatly rose! "
                    
            elif move.kind == "a+sa+":
                self.attacker.atkStage +=1
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s attack rose! "
                self.attacker.spAtkStage +=1
                self.attacker.battleSpATK = round(self.attacker.originalSpATK * self.statMod(self.attacker.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special attack rose! "
                    
            elif move.kind == "a+d+":
                self.attacker.atkStage +=1
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s attack rose! "
                self.attacker.defStage +=1
                self.attacker.battleDEF = round(self.attacker.originalDEF * self.statMod(self.attacker.defStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s defense rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s defense rose! "
                    
            elif move.kind == "a+s++":
                self.attacker.atkStage +=1
                self.attacker.battleATK = round(self.attacker.originalATK * self.statMod(self.attacker.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s attack rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s attack rose! "
                self.attacker.speedStage +=2
                self.attacker.battleSpeed = round(self.attacker.originalSpeed * self.statMod(self.attacker.speedStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s speed greatly rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s speed greatly rose! "
                    
            elif move.kind == "d+sd+":
                self.attacker.defStage +=1
                self.attacker.battleDEF = round(self.attacker.originalDEF * self.statMod(self.attacker.defStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s defense rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s defense rose! "
                self.attacker.spDefStage +=1
                self.attacker.battleSpDef = round(self.attacker.originalSpDEF * self.statMod(self.attacker.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s special defense rose! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s special defense rose! "
                    
            elif move.kind == "twater-":
                if self.victim.type2 == '':
                    self.victim.type1 = 'Water'
                    if self.attacker.person1.type == 'player':
                        tempMsg += "\nFoe's " + self.victim.pokemonname + "'s type changed to Water! "
                    else:
                        tempMsg += "\n" + self.victim.pokemonname + "'s type changed to Water! "
                        
            elif move.kind == "tghost-":
                if self.victim.type2 == '':
                    self.victim.type2 = 'Ghost'
                    if self.attacker.person1.type == 'player':
                        tempMsg += "\nFoe's " + self.victim.pokemonname + "'s type changed to " + self.attacker.type1 + "/" + self.attacker.type2 + "! "
                    else:
                        tempMsg += "\n" + self.victim.pokemonname + "'s type changed to " + self.attacker.type1 + "/" + self.attacker.type2 + "! "
            
            elif move.kind == "tgrass-":
                if self.victim.type2 == '':
                    self.victim.type2 = 'Grass'
                    if self.attacker.person1.type == 'player':
                        tempMsg += "\nFoe's " + self.victim.pokemonname + "'s type changed to " + self.attacker.type1 + "/" + self.attacker.type2 + "! "
                    else:
                        tempMsg += "\n" + self.victim.pokemonname + "'s type changed to " + self.attacker.type1 + "/" + self.attacker.type2 + "! "
            
            elif move.kind == "typetarget":
                self.attacker.type1 = self.victim.type1
                self.attacker.type2 = self.victim.type2
                temptype = self.attacker.type1
                if self.attacker.type2 != '':
                    temptype += "/" + self.attacker.type2
                if self.attacker.person1.type == 'player':
                    tempMsg += "\n" + self.attacker.pokemonname + "'s type changed to " + temptype + "! "
                else:
                    tempMsg += "\nFoe's " + self.attacker.pokemonname + "'s type changed to " + temptype + "! "

            elif move.kind == "d-":
                self.victim.defStage -=1
                self.victim.battleDEF = round(self.victim.originalDEF * self.statMod(self.victim.defStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s defense fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s defense fell! "

            elif move.kind == "sa-":
                self.victim.spAtkStage -=1
                self.victim.battleSpATK = round(self.victim.originalSpATK * self.statMod(self.victim.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s special attack fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s special attack fell! "
                    
            elif move.kind == "a-sa-":
                self.victim.atkStage -= 1
                self.victim.battleATK = round(self.victim.originalATK * self.statMod(self.victim.atkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s attack fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s attack fell! "
                self.victim.spAtkStage -=1
                self.victim.battleSpATK = round(self.victim.originalSpATK * self.statMod(self.victim.spAtkStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s special attack fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s special attack fell! "

            elif move.kind == "sd-":
                self.victim.spDefStage -=1
                self.victim.battleSpDEF = round(self.victim.originalSpDEF * self.statMod(self.victim.spDefStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s special defense fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s special defense fell! "

            elif move.kind == "s-":
                self.victim.speedStage -=1
                self.victim.battleSpeed = round(self.victim.originalSpeed * self.statMod(self.victim.speedStage),0)
                if self.attacker.person1.type == 'player':
                    tempMsg += "\nFoe's " + self.victim.pokemonname + "'s speed fell! "
                else:
                    tempMsg += "\n" + self.victim.pokemonname + "'s speed fell! "

        # Super effective, not very effective, or no effect?
        # Appending the result to tempMsg
        if modifier < 0.85 and modifier > 0:
            tempMsg += "\nIt's not very effective..."

        elif modifier > 1.5:
            tempMsg += "\nIt's super effective!"

        elif modifier == 0.0:
            if self.attacker.person1.type == 'player':
                tempMsg += "\nIt doesn't affect foe's " + self.victim.pokemonname + "..."
            else:
                tempMsg += "\nIt doesn't affect " + self.victim.pokemonname + "..."

        # String containing useMove(), damage, and type effectiveness
        return tempMsg


    def useMove(self, move):
        msg = self.pokemonname + " used " + move.name + "! "
        return msg
        
    def createattack(self):
        _LOGGER.info('POKEMON: %s will attack %s', self.attacker.pokemonname, self.victim.pokemonname)
        cpu_choice = random.choice(self.attacker.movelist)
        self.attackedwith = cpu_choice
        self.battlestate = self.attack(cpu_choice)
        self.victim.health -= self.damage
        if self.victim.health <= 0:
            self.victim.health = 'FNT'
            self.victim.fainted = True
            if self.attacker.person1.type == 'player':
                self.battlestate += "\nFoe's " + self.victim.pokemonname + " fainted..."
            else:
                self.battlestate += "\n" + self.victim.pokemonname + " fainted..."
            self.attacker.won = True
            self.attacker.levelup()
        
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
                if not self.pokemonplayer1.won:
                    self.pokemonplayer1.choosepokemon()
                else:
                    self.pokemonplayer1.choosepokemon(self.pokemonplayer1.chosenpokemon)
                if not self.pokemonplayer2.won:
                    self.pokemonplayer2.choosepokemon()
                else:
                    self.pokemonplayer2.choosepokemon(self.pokemonplayer2.chosenpokemon)
                if not self.pokemonplayer3.won:
                    self.pokemonplayer3.choosepokemon()
                else:
                    self.pokemonplayer3.choosepokemon(self.pokemonplayer3.chosenpokemon)
                if not self.pokemonplayer4.won:
                    self.pokemonplayer4.choosepokemon()
                else:
                    self.pokemonplayer4.choosepokemon(self.pokemonplayer4.chosenpokemon)
                if not self.pokemonplayer5.won:
                    self.pokemonplayer5.choosepokemon()
                else:
                    self.pokemonplayer5.choosepokemon(self.pokemonplayer5.chosenpokemon)
                if not self.pokemonplayer6.won:
                    self.pokemonplayer6.choosepokemon()
                else:
                    self.pokemonplayer6.choosepokemon(self.pokemonplayer6.chosenpokemon)
                if not self.pokemonenemy1.won:
                    self.pokemonenemy1.choosepokemon()
                else:
                    self.pokemonenemy1.choosepokemon(self.pokemonenemy1.chosenpokemon)
                if not self.pokemonenemy2.won:
                    self.pokemonenemy2.choosepokemon()
                else:
                    self.pokemonenemy2.choosepokemon(self.pokemonenemy2.chosenpokemon)
                if not self.pokemonenemy3.won:
                    self.pokemonenemy3.choosepokemon()
                else:
                    self.pokemonenemy3.choosepokemon(self.pokemonenemy3.chosenpokemon)
                if not self.pokemonenemy4.won:
                    self.pokemonenemy4.choosepokemon()
                else:
                    self.pokemonenemy4.choosepokemon(self.pokemonenemy4.chosenpokemon)
                if not self.pokemonenemy5.won:
                    self.pokemonenemy5.choosepokemon()
                else:
                    self.pokemonenemy5.choosepokemon(self.pokemonenemy5.chosenpokemon)
                if not self.pokemonenemy6.won:
                    self.pokemonenemy6.choosepokemon()
                else:
                    self.pokemonenemy6.choosepokemon(self.pokemonenemy6.chosenpokemon)
                self.activepokemonplayer = None
                self.activepokemonenemy = None
            self.update_ha_state()
            return
                
        if self.activepokemonplayer is None or self.activepokemonplayer.health == 'FNT':
            self.pokemonplayer1.active = False
            self.pokemonplayer2.active = False
            self.pokemonplayer3.active = False
            self.pokemonplayer4.active = False
            self.pokemonplayer5.active = False
            self.pokemonplayer6.active = False
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
                self.activepokemonplayer.active = True
                if self.activepokemonplayer.chosenpokemon not in self.person2.seenpokemon:
                    self.person2.seenpokemon.append(self.activepokemonplayer.chosenpokemon)
                    self.person2.pokedexseen += 1
                self.update_ha_state()
                return
        
        if self.activepokemonenemy is None or self.activepokemonenemy.health == 'FNT':
            self.pokemonenemy1.active = False
            self.pokemonenemy2.active = False
            self.pokemonenemy3.active = False
            self.pokemonenemy4.active = False
            self.pokemonenemy5.active = False
            self.pokemonenemy6.active = False
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
            if self.activepokemonenemy.health != 'FNT':
                self.battlestate = self.person2.pname + " chose " + self.activepokemonenemy.pokemonname
                self.lastmove = None
                self.activepokemonenemy.active = True
                if self.activepokemonenemy.chosenpokemon not in self.person1.seenpokemon:
                    self.person1.seenpokemon.append(self.activepokemonenemy.chosenpokemon)
                    self.person1.pokedexseen += 1
                self.update_ha_state()
                return
        
        # outcome
        if self.activepokemonenemy.health == 'FNT':
            self.battlestate = self.person1.pname + " defeated " + self.person2.pname
            self.person1.victories += 1
            if self.person1.victories % NUMBEROFVICTORIESPERBADGE == 0:
                self.person1.badges += 1
            self.resetting = 5
            if self.pokemonplayer1.health != 'FNT' and self.pokemonplayer1.level > 1:
                self.pokemonplayer1.won = True
            if self.pokemonplayer2.health != 'FNT' and self.pokemonplayer2.level > 1:
                self.pokemonplayer2.won = True
            if self.pokemonplayer3.health != 'FNT' and self.pokemonplayer3.level > 1:
                self.pokemonplayer3.won = True
            if self.pokemonplayer4.health != 'FNT' and self.pokemonplayer4.level > 1:
                self.pokemonplayer4.won = True
            if self.pokemonplayer5.health != 'FNT' and self.pokemonplayer5.level > 1:
                self.pokemonplayer5.won = True
            if self.pokemonplayer6.health != 'FNT' and self.pokemonplayer6.level > 1:
                self.pokemonplayer6.won = True
            self.update_ha_state()
            return
        
        if self.activepokemonplayer.health == 'FNT':
            self.battlestate = self.person2.pname + " defeated " + self.person1.pname
            self.person2.victories += 1
            if self.person2.victories % NUMBEROFVICTORIESPERBADGE == 0:
                self.person2.badges += 1
            self.resetting = 5
            if self.pokemonenemy1.health != 'FNT' and self.pokemonenemy1.level > 1:
                self.pokemonenemy1.won = True
            if self.pokemonenemy2.health != 'FNT' and self.pokemonenemy2.level > 1:
                self.pokemonenemy2.won = True
            if self.pokemonenemy3.health != 'FNT' and self.pokemonenemy3.level > 1:
                self.pokemonenemy3.won = True
            if self.pokemonenemy4.health != 'FNT' and self.pokemonenemy4.level > 1:
                self.pokemonenemy4.won = True
            if self.pokemonenemy5.health != 'FNT' and self.pokemonenemy5.level > 1:
                self.pokemonenemy5.won = True
            if self.pokemonenemy6.health != 'FNT' and self.pokemonenemy6.level > 1:
                self.pokemonenemy6.won = True
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
        # if self.attacker.person1.type == 'player':
        #     self.battlestate = self.battlestate + "\n" + self.attacker.pokemonname + " attacked foe's " + self.victim.pokemonname + " with " + self.attackedwith + " doing " + str(self.damage) + " damage"
        # else:
        #     self.battlestate = self.battlestate + "\nFoe's " + self.attacker.pokemonname + " attacked " + self.victim.pokemonname + " with " + self.attackedwith + " doing " + str(self.damage) + " damage"

        self.update_ha_state()

###############################################################################        
class Move(object):
    def __init__(self, move):
        moveInfo = [None, None, None, None, 0]
        # Only reading through the file if no information is stored in the Moves Dictionary
        _LOGGER.info("POKEMON: selected new Move: %s", move)
        # Finding the matching key in the dictionary, then assigning the list to a variable called moveInfo
        if move in MOVES_DICTIONARY:
            moveInfo = MOVES_DICTIONARY[move]

        # ATTRIBUTES
        # ID info
        self.moveInfo = moveInfo
        self.id = moveInfo[0]  # Move's number id
        self.name = moveInfo[1]  # Move's name

        self.type = moveInfo[2]  # Move type
        self.kind = moveInfo[3]  # Can be special, physical, or stat-changing

        # For in-battle calculations
        self.power = int(moveInfo[4])  # Move's base damage

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

    def getType(self):
        return self.type

    def getKind(self):
        return self.kind

    def getPower(self):
        return self.power

    # SET Methods
    def setName(self, name):
        self.name = name

    def setType(self, type):
        self.type = type

    def setPower(self, power):
        self.power = power
