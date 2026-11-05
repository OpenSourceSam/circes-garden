## Story text for Circe's Garden. Edit here, not in the entity scripts.
## Written 2026-10-25. Speakers: "Circe", "Hermes", or "" for narration.
## Format codes the code fills in: crafting_need_more keeps one %d (moly count);
## MINIGAME_TEXT "correct" keeps %d/%d and "wrong" keeps %s (the herb name).
## Sleep dialogue ids are built in code as "sleep_day_%d"; their lines are SLEEP_THOUGHTS.

const LINES := {
	"hermes_intro": [
		{"speaker": "", "text": "*A young god lounges in the sun. His golden sandals have small, impatient wings.*"},
		{"speaker": "Hermes", "text": "Witch. Do you always talk to the pigs when I'm away?"},
		{"speaker": "Circe", "text": "They interrupt less than you do."},
		{"speaker": "Hermes", "text": "Cruel. Also, Apollo is chasing me, for reasons that are completely unrelated."},
		{"speaker": "Circe", "text": "What did you steal?"},
		{"speaker": "Hermes", "text": "Borrowed a lyre. And his cattle, once, but I was a baby and babies get forgiven."},
		{"speaker": "Hermes", "text": "But you have your Scylla face on. Go on, ask."},
		{"speaker": "Circe", "text": "I want to undo what I did to her."},
		{"speaker": "Hermes", "text": "She eats sailors now, six at a time. The gods don't mind; think of all the prayers."},
		{"speaker": "Circe", "text": "I made her what she is. That makes her mine to mend."},
		{"speaker": "Hermes", "text": "Then you want moly: black root, white flower. It breaks spells, if anything does."},
		{"speaker": "Hermes", "text": "First, show me you know it from nightshade. I won't be blamed for a second monster."},
	],
	"hermes_farming": [
		{"speaker": "Hermes", "text": "Now the dull part: farming. I'll supervise, which is the hard part."},
		{"speaker": "Circe", "text": "You've watched me garden for years. You've never once held a spade."},
		{"speaker": "Hermes", "text": "Plant my moly in the three plots, then sleep. Three nights, and it flowers."},
		{"speaker": "Circe", "text": "Your moly? I found it and named it."},
		{"speaker": "Hermes", "text": "And I tell the story better. That's how credit works, witch."},
		{"speaker": "Hermes", "text": "Be patient. Mortals manage it, and they have far less time than you."},
	],
	"hermes_crafting": [
		{"speaker": "Hermes", "text": "Three moly, and only a little dirt on your face. I'm proud of you."},
		{"speaker": "Hermes", "text": "Grind them at your table and brew the Calming Draught. Try not to breathe it in."},
		{"speaker": "Circe", "text": "And it will cure her?"},
		{"speaker": "Hermes", "text": "I said it would calm her. I never said cure."},
		{"speaker": "Circe", "text": "You might have mentioned that sooner."},
		{"speaker": "Hermes", "text": "I just did. Messengers are known for being prompt."},
	],
	"hermes_sailing": [
		{"speaker": "Hermes", "text": "That draught smells awful. In my experience, that's a good sign."},
		{"speaker": "Circe", "text": "Will it work?"},
		{"speaker": "Hermes", "text": "Honestly, no. But you'll go anyway, and I'd hate to miss the story."},
		{"speaker": "Circe", "text": "Your concern moves me."},
		{"speaker": "Hermes", "text": "Take the boat south. Keep to the cliff side, away from the whirlpool."},
		{"speaker": "Hermes", "text": "That puts her right above you. I can't help with that part."},
		{"speaker": "Hermes", "text": "Come back, Circe. I'd have no one left to gossip at."},
	],
	"hermes_epilogue": [
		{"speaker": "Hermes", "text": "Don't tell me. Your face is telling me already, at length."},
		{"speaker": "Circe", "text": "She drank it. For one breath she was calm, and then she was Scylla again."},
		{"speaker": "Hermes", "text": "One breath of calm. That's more than any sailor ever got from her."},
		{"speaker": "Circe", "text": "She didn't know me, Hermes. She looked at me the way you'd look at weather."},
		{"speaker": "Hermes", "text": "Witch, if you weep for every monster, you'll drown by spring."},
		{"speaker": "Circe", "text": "I'm not weeping. I'm deciding what to plant next."},
		{"speaker": "Hermes", "text": "You'll carry her a long time, you know. Forever is very long."},
		{"speaker": "Circe", "text": "Then I'll carry her. I dig for a living; my arms are strong."},
		{"speaker": "Hermes", "text": "Gods, you're dull when you're wise. I'll come back when something awful happens."},
		{"speaker": "", "text": "*He is gone in a flicker of golden sandals. The pigs come to see if you have food.*"},
		{"speaker": "", "text": "*You kneel in the garden. The soil is warm, and there is work to do.*"},
	],
	"hermes_default": [
		{"speaker": "Hermes", "text": "Still here? I've delivered three messages and a lie since you last moved."},
		{"speaker": "Circe", "text": "I was thinking."},
		{"speaker": "Hermes", "text": "Dangerous habit in a witch. Go do something I can gossip about."},
	],
	"scylla_not_ready": [
		{"speaker": "", "text": "*Gray necks sway in the mist above the cliff, each one longer than a mast.*"},
		{"speaker": "", "text": "*From somewhere up there comes a sound like a pack of dogs howling at once.*"},
		{"speaker": "Circe", "text": "I made that, with a handful of flowers and one jealous night."},
		{"speaker": "Circe", "text": "I have nothing in my hands she would take from me. Not today."},
	],
	"scylla_no_potion": [
		{"speaker": "Circe", "text": "I can't go to her with empty hands."},
		{"speaker": "Circe", "text": "Back to the boat, and back to my table. The draught first."},
	],
	"scylla_cure_attempt": [
		{"speaker": "", "text": "*Mist fills the strait. Across the water, the whirlpool roars.*"},
		{"speaker": "Circe", "text": "Scylla. It's me, Circe."},
		{"speaker": "", "text": "*Six heads slide out of the fog on necks longer than masts, gray as the cliff.*"},
		{"speaker": "", "text": "*Twelve eyes settle on you, flat and dark as holes in the rock.*"},
		{"speaker": "Circe", "text": "You laughed at everyone, in those silver sandals. I hated that laugh."},
		{"speaker": "Circe", "text": "I would give a great deal to hear it again. Please, drink this."},
		{"speaker": "", "text": "*You throw the vial. One head snaps it out of the air and swallows, glass and all.*"},
		{"speaker": "", "text": "*All six heads go still. For one breath, the draught holds, and she is calm.*"},
		{"speaker": "", "text": "*Then she breathes out, and she is exactly what she was.*"},
		{"speaker": "", "text": "*She screams like a thousand dogs and strikes the rock beside you.*"},
		{"speaker": "Circe", "text": "Scylla, please. It's me."},
		{"speaker": "", "text": "*She does not know you. There is no one left in there to know you.*"},
		{"speaker": "", "text": "*Her heads swing back toward the open sea, watching for ships.*"},
		{"speaker": "Circe", "text": "I'm sorry, Scylla. It changes nothing, and I'm sorry anyway."},
	],
	"farm_planting": [
		{"speaker": "", "text": "*You press the seed into the dark soil and smooth the earth over it.*"},
		{"speaker": "Circe", "text": "Grow well. And quickly, if you can manage both."},
	],
	"farm_no_seeds": [
		{"speaker": "Circe", "text": "No seeds left. Even a witch can't grow moly out of nothing."},
		{"speaker": "", "text": "*You check your pouch twice. It is still empty.*"},
	],
	"farm_harvest": [
		{"speaker": "", "text": "*You ease the moly from the earth. The root is black and thick, and smells of salt.*"},
		{"speaker": "Circe", "text": "Strong enough to break a curse. I hope."},
	],
	"farm_growing": [
		{"speaker": "Circe", "text": "Not yet. Moly flowers on its own schedule, not mine."},
		{"speaker": "Circe", "text": "Sleep, and let the night do the work."},
	],
	"crafting_not_ready": [
		{"speaker": "Circe", "text": "My worktable. Mortar, pestle, knives, and a hundred stoppered jars."},
		{"speaker": "Circe", "text": "It can wait. Witchcraft starts in the dirt, not at the table."},
	],
	"crafting_need_more": [
		{"speaker": "Circe", "text": "The draught needs three moly, and I have %d."},
		{"speaker": "Circe", "text": "Back to the garden. The moly won't pull itself up."},
	],
	"crafting_success": [
		{"speaker": "", "text": "*You grind the black roots to powder and crush the white petals by hand.*"},
		{"speaker": "", "text": "*You stir. The draught clears, then gleams, like moonlight caught in a jar.*"},
		{"speaker": "Circe", "text": "The Calming Draught. The strongest thing I know how to make."},
		{"speaker": "Circe", "text": "Now I sail south, and face what I made."},
	],
	"boat_blocked": [
		{"speaker": "Circe", "text": "South, past the edge of sight, is Scylla's strait."},
		{"speaker": "Circe", "text": "Not yet. I won't go to her with empty hands."},
		{"speaker": "", "text": "*The boat rocks at its rope, in no hurry at all.*"},
	],
}

## One entry per night, in order. Night 1 shows on day 1, night 2 on day 2, and so on.
const SLEEP_THOUGHTS := [
	[
		{"speaker": "", "text": "*Night falls on Aiaia. The pigs snore in a heap by the wall.*"},
		{"speaker": "Circe", "text": "Grow while I sleep, garden. It's all I ask of anyone."},
	],
	[
		{"speaker": "", "text": "*You dream of your father's halls. Scylla is laughing and tossing back her hair.*"},
		{"speaker": "", "text": "*Then her neck keeps stretching, and the laugh turns into a scream.*"},
		{"speaker": "Circe", "text": "Only a dream. I can wake from mine; she never wakes from hers."},
	],
	[
		{"speaker": "", "text": "*Rain ticks on the roof. Out in the dark, the garden drinks.*"},
		{"speaker": "Circe", "text": "On this island the days stopped having names long ago."},
		{"speaker": "Circe", "text": "Now I count them again. A little hope does that."},
	],
	[
		{"speaker": "", "text": "*You lie awake listing herbs, the way mortals count sheep.*"},
		{"speaker": "Circe", "text": "Elecampane, fennel, henbane, silver fir, and moly. Always moly."},
	],
	[
		{"speaker": "", "text": "*The wind turns south and brings a sound with it, like dogs howling far away.*"},
		{"speaker": "Circe", "text": "I hear you, Scylla. I always will."},
	],
]

## The seven prologue screens, narrated by Circe.
const PROLOGUE := [
	"I am Circe, daughter of the sun.\nMy home is Aiaia: wild hills, a lion,\nand more pigs than anyone strictly needs.",
	"Most gods never lift a finger.\nI dig, grind, boil, and learn.\nThe power in herbs is called pharmaka.",
	"I loved Glaucus, and I made him a god.\nThen he fell in love with Scylla,\nthe prettiest, cruelest nymph in the hall.",
	"At night I went to the pool where she bathed\nand squeezed poison into it, drop by drop.\nI only wanted her to look as ugly as she was.",
	"The poison did more than I meant.\nSix heads. Twelve legs. Teeth like swords.\nShe has not said a word since. She only screams.",
	"I confessed, and I was exiled here forever.\nScylla lives in a strait to the south now.\nShe eats sailors, six at a time.",
	"I have a garden, and I have time.\nPerhaps pharmaka can undo\nwhat pharmaka has done.",
]

const CREDITS := {
	"title": "Circe's Garden",
	"body": "The draught calmed Scylla for one breath.\nThen she was the monster again, and she still is.\nOn Aiaia, Circe tends her garden.\nShe does not forget. She plants anyway.",
	"prompt": "Press A / E to return to menu",
}

const HERB_HINTS := {
	"Moly": "Black root, milk-white flower. Hermes calls it his gift against sorcery.",
	"Nightshade": "Purple bells and glossy black berries. A sleep you do not wake from.",
	"Hemlock": "Purple-spotted stem, umbrellas of tiny white flowers. It stops the breath.",
}

const MINIGAME_TEXT := {
	"win": "Hermes tosses you moly seeds, almost impressed.",
	"correct": "Correct! (%d/%d)",
	"wrong": "No, that was %s. Hermes winces for you.",
}

## Hermes reacts to each right answer; the herb lesson takes them in order.
const MINIGAME_CORRECT_QUIPS := [
	"Right. Hermes looks faintly disappointed.",
	"Right again. He claims he taught you that.",
]

## And to each wrong one; %s is the herb it really was.
const MINIGAME_WRONG_QUIPS := [
	"No, that was %s. Hermes winces for you.",
	"%s. Hermes mimes dying, at length.",
	"That was %s. \"A second monster, then,\" says Hermes.",
]

## Keys match the flags quest_display.gd checks, latest quest first.
const QUEST_TITLES := {
	"game_complete": "Tend your garden",
	"quest_5_active": "Sail home and find Hermes",
	"quest_4_active": "Sail south and give Scylla the draught",
	"quest_3_active": "Brew the Calming Draught at your table",
	"quest_2_active": "Grow three moly. Sleep to pass the days",
	"quest_1_active": "Find Hermes. Prove you know your herbs",
}

const MENU := {
	"title": "Circe's Garden",
	"subtitle": "Every witch has one spell she regrets.",
}
