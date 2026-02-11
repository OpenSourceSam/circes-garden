extends Node
## AudioController - Music and sound effects management

var _music_player: AudioStreamPlayer = null
var _sfx_players: Array[AudioStreamPlayer] = []
var _current_music_id: String = ""

const MUSIC_TRACKS: Dictionary = {
	"menu": "res://assets/audio/music/main_menu_theme.mp3",
	"world": "res://assets/audio/music/world_exploration_bgm.mp3",
	"minigame": "res://assets/audio/music/minigame_bgm.mp3",
	"epilogue": "res://assets/audio/music/ending_epilogue_bgm.ogg"
}

const SFX_SOUNDS: Dictionary = {
	"ui_confirm": "res://assets/audio/sfx/ui_confirm.wav",
	"ui_move": "res://assets/audio/sfx/ui_move.wav",
	"ui_open": "res://assets/audio/sfx/ui_open.wav",
	"ui_close": "res://assets/audio/sfx/ui_close.wav",
	"correct": "res://assets/audio/sfx/correct_ding.wav",
	"wrong": "res://assets/audio/sfx/wrong_buzz.wav",
	"plant": "res://assets/audio/sfx/dig_thud.wav",
	"harvest": "res://assets/audio/sfx/success_fanfare.wav",
	"catch": "res://assets/audio/sfx/catch_chime.wav",
	"failure": "res://assets/audio/sfx/failure_sad.wav",
	"urgency": "res://assets/audio/sfx/urgency_tick.wav"
}

func _ready() -> void:
	_setup_music_player()
	_setup_sfx_pool()
	print("[AudioController] Initialized")

func _setup_music_player() -> void:
	_music_player = AudioStreamPlayer.new()
	_music_player.name = "MusicPlayer"
	_music_player.bus = "Music"
	add_child(_music_player)

func _setup_sfx_pool() -> void:
	# Create pool of SFX players for overlapping sounds
	for i in range(4):
		var player = AudioStreamPlayer.new()
		player.name = "SFXPlayer%d" % i
		player.bus = "SFX"
		add_child(player)
		_sfx_players.append(player)

# ============================================
# MUSIC
# ============================================

func play_music(music_id: String, fade_in: bool = true) -> void:
	if music_id == _current_music_id and _music_player.playing:
		return

	if not MUSIC_TRACKS.has(music_id):
		push_warning("Unknown music: %s" % music_id)
		return

	var stream = load(MUSIC_TRACKS[music_id])
	if not stream:
		push_error("Failed to load music: %s" % music_id)
		return

	_current_music_id = music_id
	_music_player.stream = stream

	if fade_in:
		_music_player.volume_db = -40
		_music_player.play()
		var tween = create_tween()
		tween.tween_property(_music_player, "volume_db", 0.0, 1.0)
	else:
		_music_player.volume_db = 0
		_music_player.play()

func stop_music(fade_out: bool = true) -> void:
	if not _music_player.playing:
		return

	if fade_out:
		var tween = create_tween()
		tween.tween_property(_music_player, "volume_db", -40.0, 1.0)
		tween.tween_callback(_music_player.stop)
	else:
		_music_player.stop()

	_current_music_id = ""

# ============================================
# SFX
# ============================================

func play_sfx(sfx_id: String) -> void:
	if not SFX_SOUNDS.has(sfx_id):
		push_warning("Unknown SFX: %s" % sfx_id)
		return

	var stream = load(SFX_SOUNDS[sfx_id])
	if not stream:
		push_error("Failed to load SFX: %s" % sfx_id)
		return

	# Find available player
	for player in _sfx_players:
		if not player.playing:
			player.stream = stream
			player.play()
			return

	# All busy - use first one
	_sfx_players[0].stream = stream
	_sfx_players[0].play()

func has_sfx(sfx_id: String) -> bool:
	return SFX_SOUNDS.has(sfx_id)
