gText_PkmnTransferredSomeonesPC::
	.string "{STR_VAR_2} a été transféré sur le\nPC de ???.\pIl a été placé dans la BOITE\nappelée “{STR_VAR_1}“$"

gText_PkmnTransferredLanettesPC::
	.string "{STR_VAR_2} a été transféré sur le\n"
#if IS_FRLG
	.string "PC de BILL.\p"
#else
	.string "PC d'ANNETTE.\p"
#endif
	.string "Il a été placé dans la BOITE\n"
	.string "appelée “{STR_VAR_1}“$"

gText_PkmnTransferredSomeonesPCBoxFull::
	.string "La BOITE {STR_VAR_3} sur le PC\nde ??? est pleine.\p{STR_VAR_2} a été placé dans la\nBOITE appelée “{STR_VAR_1}“.$"

gText_PkmnTransferredLanettesPCBoxFull::
	.string "BOX “{STR_VAR_3}” on\n"
#if IS_FRLG
	.string "BILL'S PC was full.\p"
#else
	.string "LANETTE'S PC was full.\p"
#endif
	.string "{STR_VAR_2} was transferred to\n"
	.string "BOX “{STR_VAR_1}.”$"

gText_PkmnSentToPCAfterCatch::
	.string "{STR_VAR_2} was sent to\n"
	.string "{B_PC_CREATOR_NAME} PC.\p"
	.string "It was placed in \n"
	.string "BOX “{STR_VAR_1}”.$"

gText_PlayerObtainedTheMon::
	.string "{PLAYER} obtained\n"
	.string "the {STR_VAR_1}!$"

gText_NoMoreRoomForPokemon::
	.string "Il n'y a plus de place pour\nles POKéMON.\pLes BOITES sont pleines et\nne peuvent plus rien recevoir.$"

gText_NicknameThisPokemon::
	.string "Voulez-vous donner un surnom\n"
	.string "à {STR_VAR_1}?$"
