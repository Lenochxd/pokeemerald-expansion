BourgEnBiol_House2_MapScripts::
	.byte 0

BourgEnBiol_House2_EventScript_Woman::
	msgbox BourgEnBiol_House2_Text_PokemonLevelUp, MSGBOX_NPC
	end

BourgEnBiol_House2_EventScript_Man::
	msgbox BourgEnBiol_House2_Text_YoullGoFurtherWithStrongPokemon, MSGBOX_NPC
	end

BourgEnBiol_House2_Text_PokemonLevelUp:
	.string "When POKéMON battle, they eventually\n"
	.string "level up and become stronger.$"

BourgEnBiol_House2_Text_YoullGoFurtherWithStrongPokemon:
	.string "If the POKéMON with you become\n"
	.string "stronger, you'll be able to go farther\l"
	.string "away from here.$"

