
[![Join the chat at https://gitter.im/Bart274/pokemonHA](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Bart274/pokemonHA?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# pokemonHA
pokemon simulator for Home-Assistant.io

Use config.txt to see the example config for HA.
Both the `playername` and `enemyname` are optional. If you don't use them Ash & Gary will be used.

The following entities will be added:
- pokemon.battle (the entity in which you'll see the current activity of the battle between both persons)
- pokemon.enemy and pokemon.player (both will the trainer card of the player and the enemy)
- pokemon.pokemon1player ... pokemon.pokemon6player (the 6 pokemon of the player)
- pokemon.pokemon1enemy ... pokemon.pokemon6enemy (the 6 pokemon of the enemy)

Each victory will give a trainer a badge. Each 8 badges will unlock the next generation of pokemon.

The pokedex will display the amount of unique pokemon a trainer has used.

At the beginning of each battle all fainted pokemon that haven't won a battle will be replaced by new randomly choosen pokemon. The not fainted pokemon will go up one level and that will make their attacks stronger.

# Pokemon Group containing the battle, player cards and pokemon details:

![Pokemon group](https://raw.githubusercontent.com/Bart274/pokemonHA/master/screenshots/pok1.PNG)

# Trainer Card:

![Trainer card](https://raw.githubusercontent.com/Bart274/pokemonHA/master/screenshots/pok2.PNG)

The trainer card shows the number of badges the trainer has collected.
It also shows the unique amount of pokemon the trainer has caught and has seen, together with the percentage of the pokedex the trainer has collected.

# Pokemon Details:

![Pokemon details](https://raw.githubusercontent.com/Bart274/pokemonHA/master/screenshots/pok3.PNG)

The details on the card are the current active details for the current battle. These stats change depending on the level of the pokemon and the moves used in the battle.
