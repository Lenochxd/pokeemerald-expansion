BoisGolri_MapScripts::
# 2 "data/maps/BoisGolri/scripts.pory"
	map_script MAP_SCRIPT_ON_TRANSITION, BoisGolri_MapScripts_MAP_SCRIPT_ON_TRANSITION
	.byte 0

BoisGolri_MapScripts_MAP_SCRIPT_ON_TRANSITION:
# 3 "data/maps/BoisGolri/scripts.pory"
	setvar VAR_TEMP_1, 1
	return


BoisGolri_EventScript_DirectionSign::
# 8 "data/maps/BoisGolri/scripts.pory"
	msgbox BoisGolri_Text_DirectionSign, MSGBOX_SIGN
	return


BoisGolri_EventScript_WelcomeSign::
# 17 "data/maps/BoisGolri/scripts.pory"
	msgbox BoisGolri_Text_WelcomeSign, MSGBOX_SIGN
	return


BoisGolri_Text_DirectionSign::
# 11 "data/maps/BoisGolri/scripts.pory"
	.string "Sortie vers Matéciville$"

BoisGolri_Text_WelcomeSign::
# 20 "data/maps/BoisGolri/scripts.pory"
	.string "Bienvenue aux Bois Golri !$"
