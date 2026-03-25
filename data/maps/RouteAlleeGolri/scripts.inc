RouteAlleeGolri_MapScripts::
# 2 "data/maps/RouteAlleeGolri/scripts.pory"
	map_script MAP_SCRIPT_ON_TRANSITION, RouteAlleeGolri_MapScripts_MAP_SCRIPT_ON_TRANSITION
	.byte 0

RouteAlleeGolri_MapScripts_MAP_SCRIPT_ON_TRANSITION:
# 3 "data/maps/RouteAlleeGolri/scripts.pory"
	setvar VAR_TEMP_1, 1
	return


RouteAlleeGolri_GoRight::
# 8 "data/maps/RouteAlleeGolri/scripts.pory"
	lock
# 10 "data/maps/RouteAlleeGolri/scripts.pory"
	applymovement LOCALID_PLAYER, RouteAlleeGolri_GoRight_Movement_0
# 14 "data/maps/RouteAlleeGolri/scripts.pory"
	waitmovement 0
# 15 "data/maps/RouteAlleeGolri/scripts.pory"
	release
	return


# 10 "data/maps/RouteAlleeGolri/scripts.pory"
RouteAlleeGolri_GoRight_Movement_0:
# 11 "data/maps/RouteAlleeGolri/scripts.pory"
	face_right
# 12 "data/maps/RouteAlleeGolri/scripts.pory"
	walk_right
	step_end
