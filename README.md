# pokemonHA
pokemon simulator for Home-Assistant.io

Use config.txt to see the example config for HA.
Both the `playername` and `enemyname` are optional. If you don't use them Ash & Gary will be used.

The following entities will be added:
- pokemon.battle (the entity in which you'll see the current activity of the battle between both persons)
- pokemon.enemy and pokemon.player (both will the trainer card of the player and the enemy)
- pokemon.pokemon1player ... pokemon.pokemon6player (the 6 pokemon of the player)
- pokemon.pokemon1enemy ... pokemon.pokemon6enemy (the 6 pokemon of the enemy)

Each 25 victories will give a trainer a badge. In this version only the original 151 pokemon are included. In the future, more pokemon will be added and each 8 badges will unlock the next generation of pokemon.

The pokedex will display the amount of unique pokemon a trainer has used.

At the beginning of each battle all fainted pokemon will be replaced by new randomly choosen pokemon. The not fainted pokemon will go up one level and that will make their attacks stronger.
