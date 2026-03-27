Route_302_MapScripts::
	.byte 0


Route302_EventScript_Boy::
# 5 "data/maps/Route_302/scripts.pory"
	lockall
# 6 "data/maps/Route_302/scripts.pory"
	msgbox Route302_EventScript_Boy_Text_0
# 7 "data/maps/Route_302/scripts.pory"
	releaseall
	return


Route302_EventScript_Andrew::
# 12 "data/maps/Route_302/scripts.pory"
	trainerbattle_single TRAINER_ANDREW, Route302_Text_AndrewIntro, Route302_Text_AndrewDefeated
# 13 "data/maps/Route_302/scripts.pory"
	msgbox Route302_Text_AndrewPostBattle, MSGBOX_AUTOCLOSE
	end


Route302_EventScript_Boy_Text_0:
# 6 "data/maps/Route_302/scripts.pory"
	.string "Mon POKéMON est épuisé…\n"
	.string "J'aurais du acheter une POTION…$"

Route302_Text_AndrewPostBattle::
# 17 "data/maps/Route_302/scripts.pory"
	.string "Argh, Tu m'as énervé…\n"
	.string "Grrrrr…$"

Route302_Text_AndrewIntro::
# 22 "data/maps/Route_302/scripts.pory"
	.string "ARghh! Ma ligne de pêche s'est emmêlée !\n"
	.string "Je deviens frustré et très méchant !\l"
	.string "Et m*rde ! Jvais te tuer !$"

Route302_Text_AndrewDefeated::
# 28 "data/maps/Route_302/scripts.pory"
	.string "Va crever.$"
