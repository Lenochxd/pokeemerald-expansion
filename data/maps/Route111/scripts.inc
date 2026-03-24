Route111_MapScripts::
# 4 "data/maps/Route111/scripts.pory"
	map_script MAP_SCRIPT_ON_LOAD, Route111_OnLoad
# 5 "data/maps/Route111/scripts.pory"
	map_script MAP_SCRIPT_ON_TRANSITION, Route111_OnTransition
# 6 "data/maps/Route111/scripts.pory"
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, Route111_MapScripts_MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE
# 9 "data/maps/Route111/scripts.pory"
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route111_MapScripts_MAP_SCRIPT_ON_FRAME_TABLE
	.byte 0

Route111_MapScripts_MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE:
# 7 "data/maps/Route111/scripts.pory"
	map_script_2 VAR_MIRAGE_TOWER_STATE, 1, Route111_EventScript_HidePlayerForMirageTower
	.2byte 0

Route111_MapScripts_MAP_SCRIPT_ON_FRAME_TABLE:
# 10 "data/maps/Route111/scripts.pory"
	map_script_2 VAR_MIRAGE_TOWER_STATE, 1, Route111_EventScript_MirageTowerDisappear
	.2byte 0


Route111_OnLoad:
# 15 "data/maps/Route111/scripts.pory"
	goto_if_unset FLAG_REGI_DOORS_OPENED, Route111_OnLoad_2
Route111_OnLoad_1:
# 18 "data/maps/Route111/scripts.pory"
	compare VAR_MIRAGE_TOWER_STATE, 1
	goto_if_eq Route111_OnLoad_5
Route111_OnLoad_4:
	end

Route111_OnLoad_2:
# 16 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseDesertRuins
	goto Route111_OnLoad_1

Route111_OnLoad_5:
# 19 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_ShowTemporaryMirageTower
	goto Route111_OnLoad_4


Route111_EventScript_CloseDesertRuins::
# 25 "data/maps/Route111/scripts.pory"
	setmetatile 29, 86, METATILE_General_RockWall_RockBase, TRUE
# 26 "data/maps/Route111/scripts.pory"
	setmetatile 29, 87, METATILE_General_RockWall_SandBase, TRUE
	return


Route111_EventScript_ShowTemporaryMirageTower::
# 33 "data/maps/Route111/scripts.pory"
	setmetatile 18, 53, METATILE_Mauville_MirageTower_Tile0, FALSE
# 34 "data/maps/Route111/scripts.pory"
	setmetatile 19, 53, METATILE_Mauville_MirageTower_Tile1, FALSE
# 35 "data/maps/Route111/scripts.pory"
	setmetatile 20, 53, METATILE_Mauville_MirageTower_Tile2, FALSE
# 36 "data/maps/Route111/scripts.pory"
	setmetatile 18, 54, METATILE_Mauville_MirageTower_Tile3, FALSE
# 37 "data/maps/Route111/scripts.pory"
	setmetatile 19, 54, METATILE_Mauville_MirageTower_Tile4, FALSE
# 38 "data/maps/Route111/scripts.pory"
	setmetatile 20, 54, METATILE_Mauville_MirageTower_Tile5, FALSE
# 39 "data/maps/Route111/scripts.pory"
	setmetatile 18, 55, METATILE_Mauville_MirageTower_Tile6, FALSE
# 40 "data/maps/Route111/scripts.pory"
	setmetatile 19, 55, METATILE_Mauville_MirageTower_Tile7, FALSE
# 41 "data/maps/Route111/scripts.pory"
	setmetatile 20, 55, METATILE_Mauville_MirageTower_Tile8, FALSE
# 42 "data/maps/Route111/scripts.pory"
	setmetatile 18, 56, METATILE_Mauville_MirageTower_Tile9, FALSE
# 43 "data/maps/Route111/scripts.pory"
	setmetatile 19, 56, METATILE_Mauville_MirageTower_TileA, FALSE
# 44 "data/maps/Route111/scripts.pory"
	setmetatile 20, 56, METATILE_Mauville_MirageTower_TileB, FALSE
# 45 "data/maps/Route111/scripts.pory"
	setmetatile 18, 57, METATILE_Mauville_MirageTower_TileC, FALSE
# 46 "data/maps/Route111/scripts.pory"
	setmetatile 19, 57, METATILE_Mauville_MirageTower_TileD, FALSE
# 47 "data/maps/Route111/scripts.pory"
	setmetatile 20, 57, METATILE_Mauville_MirageTower_TileE, FALSE
# 48 "data/maps/Route111/scripts.pory"
	setmetatile 18, 58, METATILE_Mauville_MirageTower_TileF, FALSE
# 49 "data/maps/Route111/scripts.pory"
	setmetatile 19, 58, METATILE_Mauville_MirageTower_Tile10, FALSE
# 50 "data/maps/Route111/scripts.pory"
	setmetatile 20, 58, METATILE_Mauville_MirageTower_Tile11, FALSE
	return


Route111_OnTransition:
# 55 "data/maps/Route111/scripts.pory"
	setvar VAR_TRAINER_HILL_IS_ACTIVE, 0
# 56 "data/maps/Route111/scripts.pory"
	special SetMirageTowerVisibility
# 57 "data/maps/Route111/scripts.pory"
	goto_if_unset FLAG_MIRAGE_TOWER_VISIBLE, Route111_OnTransition_2
Route111_OnTransition_1:
# 60 "data/maps/Route111/scripts.pory"
	compare VAR_MIRAGE_TOWER_STATE, 1
	goto_if_eq Route111_OnTransition_5
Route111_OnTransition_4:
# 63 "data/maps/Route111/scripts.pory"
	compare VAR_MIRAGE_TOWER_STATE, 2
	goto_if_eq Route111_OnTransition_8
Route111_OnTransition_7:
# 66 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CheckSetSandstorm
# 67 "data/maps/Route111/scripts.pory"
	call GabbyAndTy_EventScript_UpdateLocation
# 68 "data/maps/Route111/scripts.pory"
	goto_if_not_defeated TRAINER_VICKY, Route111_EventScript_SetWinstratesNotDefeated
	end

Route111_OnTransition_2:
# 58 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_SetLayoutNoMirageTower
	goto Route111_OnTransition_1

Route111_OnTransition_5:
# 61 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_SetFallingPlayerGfx
	goto Route111_OnTransition_4

Route111_OnTransition_8:
# 64 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_SetMirageTowerGone
	goto Route111_OnTransition_7


Route111_EventScript_SetFallingPlayerGfx::
# 73 "data/maps/Route111/scripts.pory"
	checkplayergender
# 74 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, MALE
	goto_if_eq Route111_EventScript_SetFallingPlayerGfx_2
# 77 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, FEMALE
	goto_if_eq Route111_EventScript_SetFallingPlayerGfx_3
Route111_EventScript_SetFallingPlayerGfx_1:
	return

Route111_EventScript_SetFallingPlayerGfx_2:
# 75 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_SetFallingPlayerGfxMale
	goto Route111_EventScript_SetFallingPlayerGfx_1

Route111_EventScript_SetFallingPlayerGfx_3:
# 78 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_SetFallingPlayerGfxFemale
	goto Route111_EventScript_SetFallingPlayerGfx_1


Route111_EventScript_SetFallingPlayerGfxMale::
# 84 "data/maps/Route111/scripts.pory"
	setvar VAR_OBJ_GFX_ID_0, OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL
	return


Route111_EventScript_SetFallingPlayerGfxFemale::
# 89 "data/maps/Route111/scripts.pory"
	setvar VAR_OBJ_GFX_ID_0, OBJ_EVENT_GFX_RIVAL_MAY_NORMAL
	return


Route111_EventScript_CheckSetSandstorm::
# 94 "data/maps/Route111/scripts.pory"
	getplayerxy VAR_TEMP_0, VAR_TEMP_1
# 95 "data/maps/Route111/scripts.pory"
	compare VAR_TEMP_1, 34
	goto_if_lt Route111_EventScript_CheckSetSandstorm_1
# 98 "data/maps/Route111/scripts.pory"
	compare VAR_TEMP_1, 107
	goto_if_gt Route111_EventScript_CheckSetSandstorm_2
# 101 "data/maps/Route111/scripts.pory"
	compare VAR_TEMP_1, 72
	goto_if_gt Route111_EventScript_CheckSetSandstorm_3
# 104 "data/maps/Route111/scripts.pory"
	compare VAR_TEMP_0, 2000
	goto_if_gt Route111_EventScript_CheckSetSandstorm_4
# 107 "data/maps/Route111/scripts.pory"
	compare VAR_TEMP_0, 8
	goto_if_lt Route111_EventScript_CheckSetSandstorm_5
	return

Route111_EventScript_CheckSetSandstorm_1:
# 96 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_EndCheckSetSandstorm
	return

Route111_EventScript_CheckSetSandstorm_2:
# 99 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_EndCheckSetSandstorm
	return

Route111_EventScript_CheckSetSandstorm_3:
# 102 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_SetSandstorm
	return

Route111_EventScript_CheckSetSandstorm_4:
# 105 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_EndCheckSetSandstorm
	return

Route111_EventScript_CheckSetSandstorm_5:
# 108 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_EndCheckSetSandstorm
	return


Route111_EventScript_SetSandstorm::
# 113 "data/maps/Route111/scripts.pory"
	setweather WEATHER_SANDSTORM
	return


Route111_EventScript_EndCheckSetSandstorm::
	return


Route111_EventScript_SetWinstratesNotDefeated::
# 121 "data/maps/Route111/scripts.pory"
	clearflag FLAG_HIDE_ROUTE_111_VICTOR_WINSTRATE
# 122 "data/maps/Route111/scripts.pory"
	setflag FLAG_HIDE_ROUTE_111_VICTORIA_WINSTRATE
# 123 "data/maps/Route111/scripts.pory"
	setflag FLAG_HIDE_ROUTE_111_VIVI_WINSTRATE
# 124 "data/maps/Route111/scripts.pory"
	setflag FLAG_HIDE_ROUTE_111_VICKY_WINSTRATE
# 125 "data/maps/Route111/scripts.pory"
	cleartrainerflag TRAINER_VICTOR
# 126 "data/maps/Route111/scripts.pory"
	cleartrainerflag TRAINER_VICTORIA
# 127 "data/maps/Route111/scripts.pory"
	cleartrainerflag TRAINER_VIVI
	end


Route111_EventScript_SetLayoutNoMirageTower::
# 132 "data/maps/Route111/scripts.pory"
	setmaplayoutindex LAYOUT_ROUTE111_NO_MIRAGE_TOWER
	return


Route111_EventScript_SetMirageTowerGone::
# 137 "data/maps/Route111/scripts.pory"
	setvar VAR_MIRAGE_TOWER_STATE, 3
	return


Route111_EventScript_HidePlayerForMirageTower::
# 142 "data/maps/Route111/scripts.pory"
	hideobjectat LOCALID_PLAYER, MAP_LITTLEROOT_TOWN
	end


Route111_EventScript_MirageTowerDisappear::
# 147 "data/maps/Route111/scripts.pory"
	lockall
# 148 "data/maps/Route111/scripts.pory"
	special StartMirageTowerShake
# 149 "data/maps/Route111/scripts.pory"
	waitstate
# 150 "data/maps/Route111/scripts.pory"
	delay 24
# 151 "data/maps/Route111/scripts.pory"
	playse SE_FALL
# 152 "data/maps/Route111/scripts.pory"
	addobject LOCALID_ROUTE111_PLAYER_FALLING
# 153 "data/maps/Route111/scripts.pory"
	special StartPlayerDescendMirageTower
# 154 "data/maps/Route111/scripts.pory"
	waitstate
# 155 "data/maps/Route111/scripts.pory"
	showobjectat LOCALID_PLAYER, MAP_LITTLEROOT_TOWN
# 156 "data/maps/Route111/scripts.pory"
	removeobject LOCALID_ROUTE111_PLAYER_FALLING
# 157 "data/maps/Route111/scripts.pory"
	delay 16
# 158 "data/maps/Route111/scripts.pory"
	turnobject LOCALID_PLAYER, DIR_NORTH
# 159 "data/maps/Route111/scripts.pory"
	delay 16
# 160 "data/maps/Route111/scripts.pory"
	special StartMirageTowerDisintegration
# 161 "data/maps/Route111/scripts.pory"
	waitstate
# 162 "data/maps/Route111/scripts.pory"
	special StartMirageTowerFossilFallAndSink
# 163 "data/maps/Route111/scripts.pory"
	waitstate
# 164 "data/maps/Route111/scripts.pory"
	setvar VAR_MIRAGE_TOWER_STATE, 2
# 165 "data/maps/Route111/scripts.pory"
	clearflag FLAG_HIDE_DESERT_UNDERPASS_FOSSIL
# 166 "data/maps/Route111/scripts.pory"
	goto_if_set FLAG_CHOSE_CLAW_FOSSIL, Route111_EventScript_MirageTowerDisappear_2
Route111_EventScript_MirageTowerDisappear_1:
# 169 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_ClawFossilDisappeared, MSGBOX_DEFAULT
# 170 "data/maps/Route111/scripts.pory"
	releaseall
	end

Route111_EventScript_MirageTowerDisappear_2:
# 167 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_RootFossilDisappeared
	goto Route111_EventScript_MirageTowerDisappear_1


Route111_EventScript_RootFossilDisappeared::
# 175 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_RootFossilDisappeared, MSGBOX_DEFAULT
# 176 "data/maps/Route111/scripts.pory"
	releaseall
	end


# 182 "data/maps/Route111/scripts.pory"
Route111_Movement_PlayerFall::
# 183 "data/maps/Route111/scripts.pory"
	lock_anim
# 184 "data/maps/Route111/scripts.pory"
	walk_fast_down
# 185 "data/maps/Route111/scripts.pory"
	walk_fast_down
# 186 "data/maps/Route111/scripts.pory"
	walk_fast_down
# 187 "data/maps/Route111/scripts.pory"
	walk_fast_down
# 188 "data/maps/Route111/scripts.pory"
	walk_fast_down
# 189 "data/maps/Route111/scripts.pory"
	walk_fast_down
# 190 "data/maps/Route111/scripts.pory"
	step_end

Route111_EventScript_Girl::
# 194 "data/maps/Route111/scripts.pory"
	lock
# 195 "data/maps/Route111/scripts.pory"
	faceplayer
# 196 "data/maps/Route111/scripts.pory"
	dotimebasedevents
# 197 "data/maps/Route111/scripts.pory"
	goto_if_set FLAG_DAILY_ROUTE_111_RECEIVED_BERRY, Route111_EventScript_Girl_2
Route111_EventScript_Girl_1:
# 200 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WateredPlantsEveryDayTakeBerry, MSGBOX_DEFAULT
# 201 "data/maps/Route111/scripts.pory"
	giveitem ITEM_RAZZ_BERRY
# 202 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, FALSE
	goto_if_eq Route111_EventScript_Girl_5
Route111_EventScript_Girl_4:
# 205 "data/maps/Route111/scripts.pory"
	setflag FLAG_DAILY_ROUTE_111_RECEIVED_BERRY
# 206 "data/maps/Route111/scripts.pory"
	special GetPlayerBigGuyGirlString
# 207 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_GoingToTryToMakeDifferentColorBerries, MSGBOX_DEFAULT
# 208 "data/maps/Route111/scripts.pory"
	release
	end

Route111_EventScript_Girl_2:
# 198 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_ReceivedBerry
	goto Route111_EventScript_Girl_1

Route111_EventScript_Girl_5:
# 203 "data/maps/Route111/scripts.pory"
	goto Common_EventScript_ShowBagIsFull
	goto Route111_EventScript_Girl_4


Route111_EventScript_ReceivedBerry::
# 213 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WhatColorBerriesToLookForToday, MSGBOX_DEFAULT
# 214 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_ViciousSandstormTriggerUp::
# 221 "data/maps/Route111/scripts.pory"
	lockall
# 222 "data/maps/Route111/scripts.pory"
	setvar VAR_0x8004, 0
# 223 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_ViciousSandstormTrigger
	end


Route111_EventScript_ViciousSandstormTriggerDown::
# 228 "data/maps/Route111/scripts.pory"
	lockall
# 229 "data/maps/Route111/scripts.pory"
	setvar VAR_0x8004, 1
# 230 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_ViciousSandstormTrigger
	end


Route111_EventScript_ViciousSandstormTriggerLeft::
# 235 "data/maps/Route111/scripts.pory"
	lockall
# 236 "data/maps/Route111/scripts.pory"
	setvar VAR_0x8004, 2
# 237 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_ViciousSandstormTrigger
	end


Route111_EventScript_ViciousSandstormTriggerRight::
# 244 "data/maps/Route111/scripts.pory"
	lockall
# 245 "data/maps/Route111/scripts.pory"
	setvar VAR_0x8004, 3
# 246 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_ViciousSandstormTrigger
	end


Route111_EventScript_ViciousSandstormTrigger::
# 251 "data/maps/Route111/scripts.pory"
	checkitem ITEM_GO_GOGGLES
# 252 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, FALSE
	goto_if_eq Route111_EventScript_ViciousSandstormTrigger_2
Route111_EventScript_ViciousSandstormTrigger_1:
# 255 "data/maps/Route111/scripts.pory"
	setvar VAR_TEMP_3, 1
# 256 "data/maps/Route111/scripts.pory"
	releaseall
	end

Route111_EventScript_ViciousSandstormTrigger_2:
# 253 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_PreventRouteAccess
	goto Route111_EventScript_ViciousSandstormTrigger_1


Route111_EventScript_PreventRouteAccess::
# 261 "data/maps/Route111/scripts.pory"
	msgbox gText_SandstormIsVicious, MSGBOX_DEFAULT
# 262 "data/maps/Route111/scripts.pory"
	closemessage
# 263 "data/maps/Route111/scripts.pory"
	compare VAR_0x8004, 0
	goto_if_eq Route111_EventScript_PreventRouteAccess_2
# 266 "data/maps/Route111/scripts.pory"
	compare VAR_0x8004, 1
	goto_if_eq Route111_EventScript_PreventRouteAccess_3
# 269 "data/maps/Route111/scripts.pory"
	compare VAR_0x8004, 2
	goto_if_eq Route111_EventScript_PreventRouteAccess_4
# 272 "data/maps/Route111/scripts.pory"
	compare VAR_0x8004, 3
	goto_if_eq Route111_EventScript_PreventRouteAccess_5
Route111_EventScript_PreventRouteAccess_1:
# 275 "data/maps/Route111/scripts.pory"
	releaseall
	end

Route111_EventScript_PreventRouteAccess_2:
# 264 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_PushUpFromRoute
	goto Route111_EventScript_PreventRouteAccess_1

Route111_EventScript_PreventRouteAccess_3:
# 267 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_PushDownFromRoute
	goto Route111_EventScript_PreventRouteAccess_1

Route111_EventScript_PreventRouteAccess_4:
# 270 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_PushLeftFromRoute
	goto Route111_EventScript_PreventRouteAccess_1

Route111_EventScript_PreventRouteAccess_5:
# 273 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_PushRightFromRoute
	goto Route111_EventScript_PreventRouteAccess_1


Route111_EventScript_PushUpFromRoute::
# 280 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_PushUpFromRoute
# 281 "data/maps/Route111/scripts.pory"
	waitmovement 0
	return


Route111_EventScript_PushDownFromRoute::
# 286 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_PushDownFromRoute
# 287 "data/maps/Route111/scripts.pory"
	waitmovement 0
	return


Route111_EventScript_PushLeftFromRoute::
# 292 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_PushLeftFromRoute
# 293 "data/maps/Route111/scripts.pory"
	waitmovement 0
	return


Route111_EventScript_PushRightFromRoute::
# 298 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_PushRightFromRoute
# 299 "data/maps/Route111/scripts.pory"
	waitmovement 0
	return


# 303 "data/maps/Route111/scripts.pory"
Route111_Movement_PushUpFromRoute:
# 304 "data/maps/Route111/scripts.pory"
	walk_up
# 305 "data/maps/Route111/scripts.pory"
	step_end

# 308 "data/maps/Route111/scripts.pory"
Route111_Movement_PushDownFromRoute:
# 309 "data/maps/Route111/scripts.pory"
	walk_down
# 310 "data/maps/Route111/scripts.pory"
	step_end

# 313 "data/maps/Route111/scripts.pory"
Route111_Movement_PushLeftFromRoute:
# 314 "data/maps/Route111/scripts.pory"
	walk_left
# 315 "data/maps/Route111/scripts.pory"
	step_end

# 318 "data/maps/Route111/scripts.pory"
Route111_Movement_PushRightFromRoute:
# 319 "data/maps/Route111/scripts.pory"
	walk_right
# 320 "data/maps/Route111/scripts.pory"
	step_end

Route111_EventScript_SunTrigger::
# 324 "data/maps/Route111/scripts.pory"
	setweather WEATHER_SUNNY
# 325 "data/maps/Route111/scripts.pory"
	fadenewbgm MUS_ROUTE110
# 326 "data/maps/Route111/scripts.pory"
	doweather
# 327 "data/maps/Route111/scripts.pory"
	setvar VAR_TEMP_3, 0
	end


Route111_EventScript_SandstormTrigger::
# 332 "data/maps/Route111/scripts.pory"
	setweather WEATHER_SANDSTORM
# 333 "data/maps/Route111/scripts.pory"
	fadenewbgm MUS_DESERT
# 334 "data/maps/Route111/scripts.pory"
	doweather
	end


Route111_EventScript_Victor::
# 339 "data/maps/Route111/scripts.pory"
	lock
# 340 "data/maps/Route111/scripts.pory"
	faceplayer
# 341 "data/maps/Route111/scripts.pory"
	setflag FLAG_LANDMARK_WINSTRATE_FAMILY
# 342 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BattleOurFamily, MSGBOX_YESNO
# 343 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, YES
	goto_if_eq Route111_EventScript_Victor_2
Route111_EventScript_Victor_1:
# 346 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_IsThatSo, MSGBOX_DEFAULT
# 347 "data/maps/Route111/scripts.pory"
	release
	end

Route111_EventScript_Victor_2:
# 344 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_BattleWinstrates
	goto Route111_EventScript_Victor_1


Route111_EventScript_BattleWinstrates::
# 352 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_VictorIntro, MSGBOX_DEFAULT
# 353 "data/maps/Route111/scripts.pory"
	trainerbattle_no_intro TRAINER_VICTOR, Route111_Text_VictorDefeat
# 354 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICTOR, Common_Movement_WalkInPlaceFasterUp
# 355 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 356 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 357 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_VictorPostBattle, MSGBOX_DEFAULT
# 358 "data/maps/Route111/scripts.pory"
	closemessage
# 359 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICTOR, Route111_Movement_WinstrateEnterHouse
# 360 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 361 "data/maps/Route111/scripts.pory"
	removeobject LOCALID_ROUTE111_VICTOR
# 362 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 363 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_WaitForNextWinstrate
# 364 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 365 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 366 "data/maps/Route111/scripts.pory"
	addobject LOCALID_ROUTE111_VICTORIA
# 367 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICTORIA, Route111_Movement_WinstrateExitHouse
# 368 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 369 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 370 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_VictoriaIntro, MSGBOX_DEFAULT
# 371 "data/maps/Route111/scripts.pory"
	trainerbattle_no_intro TRAINER_VICTORIA, Route111_Text_VictoriaDefeat
# 372 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICTORIA, Common_Movement_WalkInPlaceFasterUp
# 373 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 374 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 375 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_VictoriaPostBattle, MSGBOX_DEFAULT
# 376 "data/maps/Route111/scripts.pory"
	closemessage
# 377 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICTORIA, Route111_Movement_WinstrateEnterHouse
# 378 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 379 "data/maps/Route111/scripts.pory"
	removeobject LOCALID_ROUTE111_VICTORIA
# 380 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 381 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_WaitForNextWinstrate
# 382 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 383 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 384 "data/maps/Route111/scripts.pory"
	addobject LOCALID_ROUTE111_VIVI
# 385 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VIVI, Route111_Movement_WinstrateExitHouse
# 386 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 387 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 388 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_ViviIntro, MSGBOX_DEFAULT
# 389 "data/maps/Route111/scripts.pory"
	trainerbattle_no_intro TRAINER_VIVI, Route111_Text_ViviDefeat
# 390 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VIVI, Common_Movement_WalkInPlaceFasterUp
# 391 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 392 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 393 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_ViviPostBattle, MSGBOX_DEFAULT
# 394 "data/maps/Route111/scripts.pory"
	closemessage
# 395 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VIVI, Route111_Movement_WinstrateEnterHouse
# 396 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 397 "data/maps/Route111/scripts.pory"
	removeobject LOCALID_ROUTE111_VIVI
# 398 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 399 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_PLAYER, Route111_Movement_WaitForNextWinstrate
# 400 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 401 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 402 "data/maps/Route111/scripts.pory"
	addobject LOCALID_ROUTE111_VICKY
# 403 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICKY, Route111_Movement_WinstrateExitHouse
# 404 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 405 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 406 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_VickyIntro, MSGBOX_DEFAULT
# 407 "data/maps/Route111/scripts.pory"
	trainerbattle_no_intro TRAINER_VICKY, Route111_Text_VickyDefeat
# 408 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_VickyPostBattle, MSGBOX_DEFAULT
# 409 "data/maps/Route111/scripts.pory"
	closemessage
# 410 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICKY, Common_Movement_WalkInPlaceFasterUp
# 411 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 412 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_OpenWinstrateDoor
# 413 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_VICKY, Route111_Movement_WinstrateEnterHouse
# 414 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 415 "data/maps/Route111/scripts.pory"
	removeobject LOCALID_ROUTE111_VICKY
# 416 "data/maps/Route111/scripts.pory"
	call Route111_EventScript_CloseWinstrateDoor
# 417 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_OpenWinstrateDoor::
# 422 "data/maps/Route111/scripts.pory"
	opendoor 13, 113
# 423 "data/maps/Route111/scripts.pory"
	waitdooranim
	return


Route111_EventScript_CloseWinstrateDoor::
# 428 "data/maps/Route111/scripts.pory"
	closedoor 13, 113
# 429 "data/maps/Route111/scripts.pory"
	waitdooranim
	return


# 433 "data/maps/Route111/scripts.pory"
Route111_Movement_WinstrateEnterHouse:
# 434 "data/maps/Route111/scripts.pory"
	walk_in_place_faster_up
# 435 "data/maps/Route111/scripts.pory"
	walk_up
# 436 "data/maps/Route111/scripts.pory"
	step_end

# 439 "data/maps/Route111/scripts.pory"
Route111_Movement_WinstrateExitHouse:
# 440 "data/maps/Route111/scripts.pory"
	walk_down
# 441 "data/maps/Route111/scripts.pory"
	step_end

# 444 "data/maps/Route111/scripts.pory"
Route111_Movement_WaitForNextWinstrate:
# 445 "data/maps/Route111/scripts.pory"
	delay_16
# 446 "data/maps/Route111/scripts.pory"
	delay_16
# 447 "data/maps/Route111/scripts.pory"
	delay_16
# 448 "data/maps/Route111/scripts.pory"
	step_end

Route111_EventScript_RouteSignMauville::
# 452 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_RouteSignMauville, MSGBOX_SIGN
	end


Route111_EventScript_WinstrateHouseSign::
# 457 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WinstrateHouseSign, MSGBOX_SIGN
	end


Route111_EventScript_RouteSign112::
# 462 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_RouteSign112, MSGBOX_SIGN
	end


Route111_EventScript_RouteSign113::
# 467 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_RouteSign113, MSGBOX_SIGN
	end


Route111_EventScript_OldLadysRestStopSign::
# 472 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_OldLadysRestStopSign, MSGBOX_SIGN
	end


Route111_EventScript_TrainerTipsSpAtkSpDef::
# 477 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_TrainerTipsSpAtkSpDef, MSGBOX_SIGN
	end


Route111_EventScript_Man1::
# 482 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_ToughToKeepWinningUpTheRanks, MSGBOX_NPC
	end


Route111_EventScript_Man2::
# 487 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WinstrateFamilyDestroyedMe, MSGBOX_NPC
	end


Route111_EventScript_Hiker::
# 492 "data/maps/Route111/scripts.pory"
	lock
# 493 "data/maps/Route111/scripts.pory"
	faceplayer
# 494 "data/maps/Route111/scripts.pory"
	compare VAR_MIRAGE_TOWER_STATE, 3
	goto_if_eq Route111_EventScript_Hiker_2
# 497 "data/maps/Route111/scripts.pory"
	compare VAR_MIRAGE_TOWER_STATE, 2
	goto_if_eq Route111_EventScript_Hiker_3
# 500 "data/maps/Route111/scripts.pory"
	goto_if_set FLAG_MIRAGE_TOWER_VISIBLE, Route111_EventScript_Hiker_4
Route111_EventScript_Hiker_1:
# 503 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_ShouldBeMirageTowerAroundHere, MSGBOX_DEFAULT
# 504 "data/maps/Route111/scripts.pory"
	release
	end

Route111_EventScript_Hiker_2:
# 495 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_HikerMirageTowerGone
	goto Route111_EventScript_Hiker_1

Route111_EventScript_Hiker_3:
# 498 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_HikerMirageTowerDisintegrated
	goto Route111_EventScript_Hiker_1

Route111_EventScript_Hiker_4:
# 501 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_HikerMirageTowerVisible
	goto Route111_EventScript_Hiker_1


Route111_EventScript_HikerMirageTowerGone::
# 509 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_MirageTowerHasntBeenSeenSince, MSGBOX_DEFAULT
# 510 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_HikerMirageTowerDisintegrated::
# 515 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_ThatWasShockingSandRainedDown, MSGBOX_DEFAULT
# 516 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_HikerMirageTowerVisible::
# 521 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_MirageTowerClearlyVisible, MSGBOX_DEFAULT
# 522 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_RockSmashTipFatMan::
# 527 "data/maps/Route111/scripts.pory"
	lockall
# 528 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_ROCK_SMASH_MAN, Common_Movement_FacePlayer
# 529 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 530 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_MauvilleUncleToldMeToTakeRockSmash, MSGBOX_DEFAULT
# 531 "data/maps/Route111/scripts.pory"
	closemessage
# 532 "data/maps/Route111/scripts.pory"
	applymovement LOCALID_ROUTE111_ROCK_SMASH_MAN, Common_Movement_FaceOriginalDirection
# 533 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 534 "data/maps/Route111/scripts.pory"
	releaseall
	end


Route111_EventScript_Drew::
# 539 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_DREW, Route111_Text_DrewIntro, Route111_Text_DrewDefeat
# 540 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_DrewPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Heidi::
# 545 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_HEIDI, Route111_Text_HeidiIntro, Route111_Text_HeidiDefeat
# 546 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_HeidiPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Beau::
# 551 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_BEAU, Route111_Text_BeauIntro, Route111_Text_BeauDefeat
# 552 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BeauPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Becky::
# 557 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_BECKY, Route111_Text_BeckyIntro, Route111_Text_BeckyDefeat
# 558 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BeckyPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Dusty::
# 563 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_DUSTY_1, Route111_Text_DustyIntro, Route111_Text_DustyDefeat, Route111_EventScript_RegisterDusty
# 564 "data/maps/Route111/scripts.pory"
	specialvar VAR_RESULT, ShouldTryRematchBattle
# 565 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, TRUE
	goto_if_eq Route111_EventScript_Dusty_2
Route111_EventScript_Dusty_1:
# 568 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_DustyPostBattle, MSGBOX_DEFAULT
# 569 "data/maps/Route111/scripts.pory"
	release
	end

Route111_EventScript_Dusty_2:
# 566 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_RematchDusty
	goto Route111_EventScript_Dusty_1


Route111_EventScript_RegisterDusty::
# 574 "data/maps/Route111/scripts.pory"
	special PlayerFaceTrainerAfterBattle
# 575 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 576 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_DustyRegister, MSGBOX_DEFAULT
# 577 "data/maps/Route111/scripts.pory"
	register_matchcall TRAINER_DUSTY_1
# 578 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_RematchDusty::
# 583 "data/maps/Route111/scripts.pory"
	trainerbattle_rematch TRAINER_DUSTY_1, Route111_Text_DustyRematchIntro, Route111_Text_DustyRematchDefeat
# 584 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_DustyPostRematch, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Travis::
# 589 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_TRAVIS, Route111_Text_TravisIntro, Route111_Text_TravisDefeat
# 590 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_TravisPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Irene::
# 595 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_IRENE, Route111_Text_IreneIntro, Route111_Text_IreneDefeat
# 596 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_IrenePostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Daisuke::
# 601 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_DAISUKE, Route111_Text_DaisukeIntro, Route111_Text_DaisukeDefeat
# 602 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_DaisukePostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Wilton::
# 607 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_WILTON_1, Route111_Text_WiltonIntro, Route111_Text_WiltonDefeat, Route111_EventScript_RegisterWilton
# 608 "data/maps/Route111/scripts.pory"
	specialvar VAR_RESULT, ShouldTryRematchBattle
# 609 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, TRUE
	goto_if_eq Route111_EventScript_Wilton_2
Route111_EventScript_Wilton_1:
# 612 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WiltonPostBattle, MSGBOX_DEFAULT
# 613 "data/maps/Route111/scripts.pory"
	release
	end

Route111_EventScript_Wilton_2:
# 610 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_RematchWilton
	goto Route111_EventScript_Wilton_1


Route111_EventScript_RegisterWilton::
# 618 "data/maps/Route111/scripts.pory"
	special PlayerFaceTrainerAfterBattle
# 619 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 620 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WiltonRegister, MSGBOX_DEFAULT
# 621 "data/maps/Route111/scripts.pory"
	register_matchcall TRAINER_WILTON_1
# 622 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_RematchWilton::
# 627 "data/maps/Route111/scripts.pory"
	trainerbattle_rematch TRAINER_WILTON_1, Route111_Text_WiltonRematchIntro, Route111_Text_WiltonRematchDefeat
# 628 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_WiltonPostRematch, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Brooke::
# 633 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_BROOKE_1, Route111_Text_BrookeIntro, Route111_Text_BrookeDefeat, Route111_EventScript_RegisterBrooke
# 634 "data/maps/Route111/scripts.pory"
	specialvar VAR_RESULT, ShouldTryRematchBattle
# 635 "data/maps/Route111/scripts.pory"
	compare VAR_RESULT, TRUE
	goto_if_eq Route111_EventScript_Brooke_2
Route111_EventScript_Brooke_1:
# 638 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BrookePostBattle, MSGBOX_DEFAULT
# 639 "data/maps/Route111/scripts.pory"
	release
	end

Route111_EventScript_Brooke_2:
# 636 "data/maps/Route111/scripts.pory"
	goto Route111_EventScript_RematchBrooke
	goto Route111_EventScript_Brooke_1


Route111_EventScript_RegisterBrooke::
# 644 "data/maps/Route111/scripts.pory"
	special PlayerFaceTrainerAfterBattle
# 645 "data/maps/Route111/scripts.pory"
	waitmovement 0
# 646 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BrookeRegister, MSGBOX_DEFAULT
# 647 "data/maps/Route111/scripts.pory"
	register_matchcall TRAINER_BROOKE_1
# 648 "data/maps/Route111/scripts.pory"
	release
	end


Route111_EventScript_RematchBrooke::
# 653 "data/maps/Route111/scripts.pory"
	trainerbattle_rematch TRAINER_BROOKE_1, Route111_Text_BrookeRematchIntro, Route111_Text_BrookeRematchDefeat
# 654 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BrookePostRematch, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Hayden::
# 659 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_HAYDEN, Route111_Text_HaydenIntro, Route111_Text_HaydenDefeat
# 660 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_HaydenPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Bianca::
# 665 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_BIANCA, Route111_Text_BiancaIntro, Route111_Text_BiancaDefeat
# 666 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BiancaPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Tyron::
# 671 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_TYRON, Route111_Text_TyronIntro, Route111_Text_TyronDefeat
# 672 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_TyronPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Celina::
# 677 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_CELINA, Route111_Text_CelinaIntro, Route111_Text_CelinaDefeat
# 678 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_CelinaPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Celia::
# 683 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_CELIA, Route111_Text_CeliaIntro, Route111_Text_CeliaDefeat
# 684 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_CeliaPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Bryan::
# 689 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_BRYAN, Route111_Text_BryanIntro, Route111_Text_BryanDefeat
# 690 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BryanPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_Branden::
# 695 "data/maps/Route111/scripts.pory"
	trainerbattle_single TRAINER_BRANDEN, Route111_Text_BrandenIntro, Route111_Text_BrandenDefeat
# 696 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_BrandenPostBattle, MSGBOX_AUTOCLOSE
	end


Route111_EventScript_TrainerHillSign::
# 701 "data/maps/Route111/scripts.pory"
	msgbox Route111_Text_TrainerHillSign, MSGBOX_SIGN
	end


Route111_Text_BattleOurFamily:
# 705 "data/maps/Route111/scripts.pory"
	.string "Hello! I take it you're a traveler.\p"
	.string "How's this? What do you say to taking\n"
	.string "on our family of four in a series of\l"
	.string "POKéMON battles?$"

Route111_Text_IsThatSo:
# 712 "data/maps/Route111/scripts.pory"
	.string "Is that so?\n"
	.string "Drop in, if you change your mind!$"

Route111_Text_VictorIntro:
# 717 "data/maps/Route111/scripts.pory"
	.string "That's the spirit! I like you!$"

Route111_Text_VictorDefeat:
# 721 "data/maps/Route111/scripts.pory"
	.string "Aiyah!\n"
	.string "You're a lot tougher than I expected!$"

Route111_Text_VictorPostBattle:
# 726 "data/maps/Route111/scripts.pory"
	.string "Hey, all!\n"
	.string "I've found a pretty strong TRAINER!$"

Route111_Text_VictoriaIntro:
# 731 "data/maps/Route111/scripts.pory"
	.string "Oh, my goodness! Aren't you young?\p"
	.string "You must be quite the TRAINER to beat\n"
	.string "my husband, though.\p"
	.string "It's my turn to battle now!$"

Route111_Text_VictoriaDefeat:
# 738 "data/maps/Route111/scripts.pory"
	.string "Oh, gosh!\n"
	.string "I can't get over how strong you are!$"

Route111_Text_VictoriaPostBattle:
# 743 "data/maps/Route111/scripts.pory"
	.string "There's a strong TRAINER here!\n"
	.string "This one's really strong!$"

Route111_Text_ViviIntro:
# 748 "data/maps/Route111/scripts.pory"
	.string "You're stronger than Mommy? Wow!\p"
	.string "But I'm strong, too!\n"
	.string "Really! Honestly!$"

Route111_Text_ViviDefeat:
# 754 "data/maps/Route111/scripts.pory"
	.string "Huh? Did I just lose?$"

Route111_Text_ViviPostBattle:
# 758 "data/maps/Route111/scripts.pory"
	.string "This stinks…\p"
	.string "…Snivel… Grandma!$"

Route111_Text_VickyIntro:
# 763 "data/maps/Route111/scripts.pory"
	.string "How dare you make my granddaughter\n"
	.string "cry!\p"
	.string "For that, I'm going to smack you!\n"
	.string "Prepare to lose!$"

Route111_Text_VickyDefeat:
# 770 "data/maps/Route111/scripts.pory"
	.string "Kwah! You are strong…\n"
	.string "My granddaughter was right…$"

Route111_Text_VickyPostBattle:
# 775 "data/maps/Route111/scripts.pory"
	.string "If you're not in any hurry,\n"
	.string "visit with us awhile.$"

Route111_Text_ToughToKeepWinningUpTheRanks:
# 780 "data/maps/Route111/scripts.pory"
	.string "If you don't raise your POKéMON some\n"
	.string "more, it could be tough to keep winning\l"
	.string "up through the ranks.\p"
	.string "I've heard the POKéMON LEAGUE's\n"
	.string "ELITE FOUR are far stronger than\l"
	.string "any GYM LEADER.$"

Route111_Text_WinstrateFamilyDestroyedMe:
# 789 "data/maps/Route111/scripts.pory"
	.string "I challenged the WINSTRATE family,\n"
	.string "but four matches in a row is tough\l"
	.string "going… They destroyed me.$"

Route111_Text_RouteSignMauville:
# 795 "data/maps/Route111/scripts.pory"
	.string "ROUTE 111\n"
	.string "{DOWN_ARROW} MAUVILLE CITY$"

Route111_Text_WinstrateHouseSign:
# 800 "data/maps/Route111/scripts.pory"
	.string "“Our family's hearts beat as one!”\n"
	.string "THE WINSTRATE'S HOUSE$"

Route111_Text_RouteSign112:
# 805 "data/maps/Route111/scripts.pory"
	.string "ROUTE 111\n"
	.string "{LEFT_ARROW} ROUTE 112$"

Route111_Text_RouteSign113:
# 810 "data/maps/Route111/scripts.pory"
	.string "ROUTE 111\n"
	.string "{LEFT_ARROW} ROUTE 113$"

Route111_Text_OldLadysRestStopSign:
# 815 "data/maps/Route111/scripts.pory"
	.string "OLD LADY'S REST STOP\n"
	.string "“Come in and rest your tired bones.”$"

Route111_Text_TrainerTipsSpAtkSpDef:
# 820 "data/maps/Route111/scripts.pory"
	.string "TRAINER TIPS\p"
	.string "One of the indicators of a POKéMON's\n"
	.string "powerfulness is SP. ATK. It stands for\l"
	.string "“SPECIAL ATTACK.”\p"
	.string "Likewise, SP. DEF stands for “SPECIAL\n"
	.string "DEFENSE.”$"

Route111_Text_ShouldBeMirageTowerAroundHere:
# 829 "data/maps/Route111/scripts.pory"
	.string "There should be a tower made of sand\n"
	.string "around here somewhere.\p"
	.string "But for some reason, it can be seen\n"
	.string "sometimes, and sometimes not.\p"
	.string "That's why I call it the MIRAGE TOWER.$"

Route111_Text_MirageTowerClearlyVisible:
# 837 "data/maps/Route111/scripts.pory"
	.string "I see it!\n"
	.string "The tower of sand!\p"
	.string "The sand tower they called a mirage\n"
	.string "is clearly visible!\p"
	.string "But it looks so fragile…\n"
	.string "It could crumble away anytime…\p"
	.string "I want to go inside it, but I can't\n"
	.string "get my courage up for it…$"

Route111_Text_ThatWasShockingSandRainedDown:
# 848 "data/maps/Route111/scripts.pory"
	.string "Whoa…\n"
	.string "That was shocking.\p"
	.string "Sand rained down in chunks all of\n"
	.string "a sudden.\p"
	.string "What was it like inside?\n"
	.string "Were there sandy ghosts and such?$"

Route111_Text_MirageTowerHasntBeenSeenSince:
# 857 "data/maps/Route111/scripts.pory"
	.string "Since I spoke to you, the tower of sand\n"
	.string "hasn't been seen.\p"
	.string "Perhaps it really was\n"
	.string "the MIRAGE TOWER…$"

Route111_Text_ClawFossilDisappeared:
# 864 "data/maps/Route111/scripts.pory"
	.string "The CLAW FOSSIL disappeared into\n"
	.string "the sand…$"

Route111_Text_RootFossilDisappeared:
# 869 "data/maps/Route111/scripts.pory"
	.string "The ROOT FOSSIL disappeared into\n"
	.string "the sand…$"

Route111_Text_MauvilleUncleToldMeToTakeRockSmash:
# 874 "data/maps/Route111/scripts.pory"
	.string "Oh, no!\p"
	.string "My uncle in MAUVILLE told me to take\n"
	.string "ROCK SMASH with me if I was going to\l"
	.string "ROUTE 111!\p"
	.string "My uncle? He lives across from\n"
	.string "the bike shop in MAUVILLE.$"

Route111_Text_TrainerHillSign:
# 883 "data/maps/Route111/scripts.pory"
	.string "{RIGHT_ARROW} TRAINER HILL ENTRANCE\p"
	.string "“Scale the heights, you hot-blooded\n"
	.string "TRAINERS!”$"
