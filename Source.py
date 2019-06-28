# Written by Josh#5318 for Discord Hack Week 2019
# Project started: 24/06/19
# Last edited: 29/06/19 00:57 BST

import discord, uuid, asyncio, random, json
from discord.utils import get
from requests.utils import requote_uri

Token = "Enter Token Here"
client = discord.Client()

Data = json.loads(open("Data.json", "r").read())
Words = json.loads(open("BasicWords.json", "r").read())
AllWords = json.loads(open("AllWords.json", "r").read())

GameList = {
	"2048": "g:2048",
	"Connect 4": "g:connect4",
	"Countdown": "g:countdown",
	"Guess the Code": "g:code",
	"Hangman": "g:hangman",
	"Minesweeper": "g:minesweeper",
	#"Simon Says!": "g:simonsays", # unused because its bedtime zzzzzzzzzzz
	"Rock, Paper, Scissors!": "g:rps",
	"Tic-Tac-Toe": "g:tictactoe",
	"Trivia": "g:trivia"
}

BG2048 = "<:Background:593530206782881802>"
Game2048Tiles = {
	2: "<:2_:593530206002741279>",
	4: "<:4_:593530206954717194>",
	8: "<:8_:593530206632017941>",
	16: "<:16:593530206808047619>",
	32: "<:32:593530206552064010>",
	64: "<:64:593530206883414047>",
	128: "<:128:593530206988271656>",
	256: "<:256:593530206736613377>",
	512: "<:512:593530206594138127>",
	1024: "<:1024:593530206527029279>",
	2048: "<:2048:593530206753521667>",
}

HangmanStates = [
	"``` ____\n|  |\n|  O\n| /|\\\n| / \\\n|```",
	"``` ____\n|  |\n|  O\n| /|\\\n| /\n|```",
	"``` ____\n|  |\n|  O\n| /|\\\n|\n|```",
	"``` ____\n|  |\n|  O\n| /|\n|\n|```",
	"``` ____\n|  |\n|  O\n|  |\n|\n|```",
	"``` ____\n|  |\n|  O\n|\n|\n|```",
	"``` ____\n|  |\n|\n|\n|\n|```",
	"``` ____\n|\n|\n|\n|\n|```",
	"``` \n|\n|\n|\n|\n|```",
][::-1]

AllDigit = "<a:7f_all:594216883608223755>"
Digits = [
	"<:7f_0:594216883494846464>",
	"<:7f_1:594216883083804683>",
	"<:7f_2:594216883473874954>"
]

EmojiNumbers = ["\u0030\u20E3","\u0031\u20E3","\u0032\u20E3","\u0033\u20E3","\u0034\u20E3","\u0035\u20E3", "\u0036\u20E3","\u0037\u20E3","\u0038\u20E3","\u0039\u20E3"]
Vowels = list("AEIOU")
Consonants = list("BCDFGHJKLMNPQRSTVWXYZ")

SimilarNames = ["Siimon", "S!mon", "Sim0n", "Simin", "Siman", "Simmon", "5imon"]

GamesInPlay = {}
Searching = {}
ServerTriviaChannels = {}
HangmanChannels = {}
CountdownChannels = {}

def GetNumberFromEmoji(Emoji):
	Count = 0
	for i in EmojiNumbers:
		if i == Emoji:
			return Count
		Count += 1
	return False

def IsInList(List, Value):
	Count = 0
	for i in List:
		if i == Value:
			return Count
		Count += 1
	return None

async def SimonSays(message, Reaction, ID): # unused because its early and i cant think and i want to go to bed pls send tshirt thx
	async def GenerateTask():
		Text = ""
		Correct = False
		Value = random.randint(1, 3)
		if Value == 1:
			Text = "Simon says react with a "
			Correct = True
		elif Value == 2:
			Text = random.choice(SimilarNames) + " says react with a "
		elif Value == 3:
			Text = "React with a "
		Number = random.randint(1, 4)
		return Text + EmojiNumbers[Number] + " ", Correct, EmojiNumbers[Number]

	async def Main():
		Embed = discord.Embed(
			title = "Simon Says!",
			description = "Preparing game <a:loading:401798527325569034>",
			color = 0x7289da
		)
		Embed.set_footer(text = "Game ID: " + GameID)
		Message = await client.send_message(message.channel, embed = Embed)
		for i in range(1, 5):
			await client.add_reaction(Message, EmojiNumbers[i])

		while len(GamesInPlay[GameID]["Players"]) > 1:
			GamesInPlay[GameID]["Responses"] = {}
			Text, Correct, Num = await GenerateTask()
			GamesInPlay[GameID]["Value"] = Num
			GamesInPlay[GameID]["Correct"] = Correct
			Embed.description = Text + AllDigit + "\n\nPlayers remaining: " + ", ".join([i.name for i in GamesInPlay[GameID]["Players"]])
			await client.edit_message(Message, embed = Embed)
			await asyncio.sleep(10)

		Players = GamesInPlay[GameID]["Players"]
		if len(Players) == 1:
			Embed.description = "**" + Players[0].name + " wins!**"
			await client.edit_message(Message, embed = Embed)
		else:
			Embed.description = "No one wins!"
			await client.edit_message(Message, embed = Embed)
		del GamesInPlay[GameID]

	if not Reaction:
		GameID = uuid.uuid1()
		GamesInPlay[GameID] = {
			"ID": GameID,
			"Game": "simonsays",
			"Players": [],
			"Started": False,
			"Correct": True,
			"Responses": {},
			"Value": 0
		}
		Embed = discord.Embed(
			title = "Simon Says!",
			description = """Welcome to Simon Says!

Simon Says is a game for everyone on the server to play! The aim is to complete instructions starting with "Simon says". If you complete an instruction that doesn't start with "Simon says", you're out! You must react to the message during each round, otherwise you will be kicked from the game!

Give this message a thumbs up if you would like to play!

Game starting in:""" + Digits[2] + AllDigit,
			color = 0x7289da
		)
		Embed.set_footer(text = "Game ID: " + GameID)
		Msg = await client.send_message(
			message.channel,
			embed = Embed
		)
		await client.add_reaction(Msg, "👍")
		for i in range(2, -1, -1):
			Embed = discord.Embed(
				title = "Simon Says!",
				description = """Welcome to Simon Says!

Simon Says is a game for everyone on the server to play! The aim is to complete instructions starting with "Simon Says". If you complete an instruction that doesn't start with "Simon Says", you're out!

React to this message if you would like to play!

Game starting in:""" + Digits[i] + AllDigit,
				color = 0x7289da
			)
			await client.edit_message(Msg, embed = Embed)
			await asyncio.sleep(10)
		Players = GamesInPlay[GameID]["Players"]
		if len(Players) >= 2:
			GamesInPlay[GameID]["Started"] = True
			await Main()
		else:
			await client.edit_message(Msg, embed = discord.Embed(
				title = "Simon Says!",
				description = "Sorry, at least 2 players are needed to play.\n\nYou can start again by using `g:simonsays`!"
			))
			del GamesInPlay[GameID]

	else:
		User = message # passed as that arg
		if not GamesInPlay[ID]["Started"]:
			if Reaction.emoji == "👍":
				GamesInPlay[ID]["Players"] += [User]
		else:
			if GamesInPlay[ID]["Value"] == GetNumberFromEmoji(Reaction.emoji):
				if User not in GamesInPlay[ID]["Responses"].keys():
					0
					#GamesInPlay[ID]["Responses"][User] = 

async def Countdown(message, Channel, Word):
	async def GenerateWord(Word):
		return "```" + " ".join(Word) + (" " * (len(Word) >= 1)) + " ".join("-"*(9 - len(Word))) + "```"

	async def GenerateLeaderboard(CurrentGame):
		if CurrentGame["Submissions"] != {}:
			Ordered = sorted(CurrentGame["Submissions"], key = CurrentGame["Submissions"].get, reverse = True)
			Board = "\n".join([("**" + i + "**: " + str(CurrentGame["Submissions"][i]) + " letters") for i in Ordered])
			await client.send_message(message.channel, embed = discord.Embed(
				title = "Countdown Leaderboard",
				description = Board,
				color = 0x7289da
			))
		else:
			await client.send_message(message.channel, embed = discord.Embed(
				title = "Countdown Leaderboard",
				description = "No one submitted any valid words! 😔",
				color = 0x7289da
			))
		del CountdownChannels[message.channel]

	async def CheckWord(Given, Word):
		Letters = [i for i in Word]
		for i in Given:
			InList = IsInList(Letters, i)
			if InList != None:
				Letters.remove(i)
			else:
				return False
		return True

	async def Main():
		CountdownChannels[message.channel] = {
			"Word": "",
			"Checking": False,
			"Submissions": {}
		}
		CurrentGame = CountdownChannels[message.channel]
		Embed = discord.Embed(
			title = "Countdown",
			description = "Choose a 🇨onsonant or a 🇻owel!\n" + await GenerateWord(CurrentGame["Word"]),
			color = 0x7289da
		)
		GameEnv = await client.send_message(message.channel, embed = Embed)
		await client.add_reaction(GameEnv, "🇨")
		await client.add_reaction(GameEnv, "🇻")
		while len(CurrentGame["Word"]) < 9:
			Reaction = await client.wait_for_reaction(user = message.author, timeout = 60)
			if Reaction:
				if Reaction.reaction.emoji == "🇨":
					CurrentGame["Word"] += random.choice(Consonants)
				elif Reaction.reaction.emoji == "🇻":
					CurrentGame["Word"] += random.choice(Vowels)
				else:
					del CountdownChannels[message.channel]
					return
			else:
				del CountdownChannels[message.channel]
				return
			Embed = discord.Embed(
				title = "Countdown",
				description = "Choose a 🇨onsonant or a 🇻owel!\n" + await GenerateWord(CurrentGame["Word"]),
				color = 0x7289da
			)
			await client.edit_message(GameEnv, embed = Embed)

		for i in range(2, -1, -1):
			Embed = discord.Embed(
				title = "Countdown",
				description = "Time Left:" + Digits[i] + AllDigit + "\n" + await GenerateWord(CurrentGame["Word"]) + "\nStarting thinking of words that you can make from the letters! When time is up, you'll have 10 seconds to submit it!",
				color = 0x7289da
			)
			CurrentGame["Checking"] = True
			await client.edit_message(GameEnv, embed = Embed)
			await asyncio.sleep(10)

		Embed = discord.Embed(
			title = "Countdown",
			description = "Please submit your word with `!submit <word>`!\nTime Left:" + AllDigit + "\n" + await GenerateWord(CurrentGame["Word"]),
			color = 0x7289da
		)
		await client.edit_message(GameEnv, embed = Embed)
		await asyncio.sleep(10)
		await client.delete_message(GameEnv)

		await GenerateLeaderboard(CurrentGame)

	if Channel:
		if Word.split()[0] == "!submit":
			Actual = Word.split()[1]
			if Actual.lower() in AllWords:
				if await CheckWord(Actual.upper(), CountdownChannels[Channel]["Word"]):
					CountdownChannels[message.channel]["Submissions"][message.author.name] = len(Actual)
	elif message.channel not in CountdownChannels:
		Msg = await client.send_message(
			message.channel,
			embed = discord.Embed(
				title = "Countdown",
				description = """Welcome to Countdown!

In Countdown, you will be given nine letters that are vowels or consonants. You then have 30 seconds to try and come up with the longest word you can make with those letters.

Once the 30 seconds is up, you have 10 seconds to submit your word using `!submit <word>`! If your word is in the dictionary and is longer than your friends', you win the game!

Are you ready to play?""",
				color = 0x7289da
			)
		)
		await client.add_reaction(Msg, "👍")
		await client.add_reaction(Msg, "👎")
		Reaction = await client.wait_for_reaction(user = message.author, timeout = 60)
		if Reaction:
			if Reaction.reaction.emoji == "👍":
				await Main()
			else:
				await client.send_message(message.channel, "👌")
	else:
		await client.send_message(
			message.channel,
			embed = discord.Embed(
				title = "Countdown",
				description = "Sorry, there is currently a game in progress!",
				color = 0x7289da
			)
		)

async def Minesweeper(message, x, y):
	async def GetSurrounding(Board, x, y):
		Count = 0
		for X in range(-1, 2):
			for Y in range(-1, 2):
				try:
					if x+X >= 0 and y+Y >= 0:
						if Board[x + X][y + Y] == "💣":
							Count += 1
				except:
					0
		return Count

	async def GenerateBoard():
		Board = [["" for i in range(10)] for i in range(10)]
		for x in range(10):
			for y in range(10):
				if random.randint(1, 9) in [1, 2]:
					Board[x][y] = "💣"
		for x in range(10):
			for y in range(10):
				if Board[x][y] != "💣":
					Surroundings = await GetSurrounding(Board, x, y)
					Board[x][y] = EmojiNumbers[Surroundings] if Surroundings else "😄"
		NewBoard = ""
		for i in Board:
			NewBoard += "||" + "||||".join(i) + "||\n"
		print(NewBoard)
		return NewBoard

	async def Main():
		await client.send_message(
			message.channel,
			embed = discord.Embed(
				title = "Minesweeper",
				description = await GenerateBoard()
			)
		)

	Msg = await client.send_message(
		message.channel,
		embed = discord.Embed(
			title = "Minesweeper",
			description = """Welcome to Minesweeper!

Minesweeper is a 1-player game where you have to try and clear the board without hitting any mines. When you hit a block, you'll either see a number, a bomb or a smiley face.

- A number represents the amount of bombs surrounding that point on the board.
- A smiley face means there are no bombs surrounding that point on the board.
- A bomb represents you losing the game!

You will need spoilers enabled for this game to work properly.

Are you ready to play?""",
			color = 0x7289da
		)
	)
	await client.add_reaction(Msg, "👍")
	await client.add_reaction(Msg, "👎")
	Reaction = await client.wait_for_reaction(user = message.author, timeout = 60)
	if Reaction:
		if Reaction.reaction.emoji == "👍":
			await Main()
		else:
			await client.send_message(message.channel, "👌")

async def Hangman(message, Channel, Guess):
	async def GenerateText(Text, Guesses):
		Word = ["-" for i in range(len(Text))]
		Unused = []
		for i in Guesses:
			Used = False
			for x in range(len(Text)):
				if Text[x].upper() == i:
					Word[x] = Text[x].upper()
					Used = True
			if not Used:
				Unused += [i]
		return "\n```" + " ".join(Word) + "```\n```Used: " + " ".join(Guesses) + "```", Word.count("-") == 0

	async def NewMessage(Info, Guessed):
		Text, Won = await GenerateText(Info["Word"], Info["UsedLetters"])
		Won = Won or Guessed
		if Info["BadGuesses"] < len(HangmanStates) - 1:
			await client.send_message(Channel, embed = discord.Embed(
				title = "Hangman",
				description = HangmanStates[Info["BadGuesses"]] + Text + ["Type a letter to guess!\nThink you know it? Type `!guess <word>` to have a guess!", "**" + message.author.name + " wins!**\nThe word was: **" + Info["Word"] + "**."][Won],
				color = 0x7289da
			))
			if Won:
				del HangmanChannels[Channel]
		else:
			await client.send_message(Channel, embed = discord.Embed(
				title = "Hangman",
				description = HangmanStates[8] + Text + "**Game Over!**\nThe word was: **" + Info["Word"] + "**.",
				color = 0x7289da
			))
			del HangmanChannels[Channel]

	async def Update():
		Info = HangmanChannels[Channel]
		if len(Guess) == 1 and 65 <= ord(Guess.upper()) <= 90 and Guess not in Info["UsedLetters"]:
			Info["UsedLetters"] += [Guess.upper()]
			if Guess.lower() not in Info["Word"].lower():
				Info["BadGuesses"] += 1
			await NewMessage(Info, False)
		elif Guess.startswith("!guess"):
			Actual = Guess.split()[1]
			if Actual.lower() == Info["Word"].lower():
				await NewMessage(Info, True)
			else:
				Info["BadGuesses"] += 1
				await NewMessage(Info, False)

	async def Main():
		HangmanChannels[message.channel] = {
			"Word": random.choice(Words),
			"BadGuesses": 0,
			"UsedLetters": []
		}
		print(HangmanChannels[message.channel]["Word"])
		Embed = discord.Embed(
			title = "Hangman",
			description = HangmanStates[0] + "\n```" + " ".join(["-"] * len(HangmanChannels[message.channel]["Word"])) + "```Type a letter to guess!\nThink you know it? Type `!guess <word>` to have a guess!",
			color = 0x7289da
		)
		Original = await client.send_message(message.channel, embed = Embed)
		await asyncio.sleep(600)
		if message.channel in HangmanChannels:
			del HangmanChannels[message.channel]

	if Channel:
		await Update()
	else:
		Msg = await client.send_message(
			message.channel,
			embed = discord.Embed(
				title = "Hangman",
				description = """Welcome to Hangman!

In Hangman, you and your friends have to try and guess a randomly generated word by guessing letters. If you get a letter right, it will appear. If you get it wrong, Hangman will start to appear. Can you save Hangman?

Are you ready to play?""",
				color = 0x7289da
			)
		)
		await client.add_reaction(Msg, "👍")
		await client.add_reaction(Msg, "👎")
		Reaction = await client.wait_for_reaction(user = message.author, timeout = 60)
		if Reaction:
			if Reaction.reaction.emoji == "👍":
				await Main()
			else:
				await client.send_message(message.channel, "👌")

async def Game2048(message, x, y):
	async def RandomTile(Board):
		Value = 4 if random.randint(1, 10) == 1 else 2
		while True:
			X = random.randint(0, 3)
			Y = random.randint(0, 3)
			if Board[Y][X] == BG2048:
				Board[Y][X] = Game2048Tiles[Value]
				return Board

	async def Double(Value):
		for i in Game2048Tiles:
			if Game2048Tiles[i] == Value:
				return i*2, i*2 != 2048

	async def GenerateBoard(Board):
		return "\n".join(["".join(i) for i in Board])

	async def GetNextTile(Board, y, x, Type, IsXAxis):
		"""if IsXAxis:
			for i in range(x, x + 5 * Inc, Inc):
				print(y, x, y, i, y, x-1*Inc)
				try:
					if i >= 0:
						if Board[y][i] == Board[y][x-1*Inc]:
							print(y, x, y, i, y, x-1*Inc)
							return y, i
						elif Board[y][i] != BG2048:
							return False, False
				except:
					return False, False
		else:
			for i in range(y, y + 5 * Inc, Inc):
				print(y, x, i,x, y-1*Inc, x)
				try:
					if i >= 0:
						if Board[i][x] == Board[y-1*Inc][x]:
							print(y, x, i,x, y-1*Inc, x)
							return i, x
						elif Board[i][x] != BG2048:
							return False, False
				except:
					return False, False"""
		if IsXAxis:
			if Type == "L":
				for i in range(x - 1, -1, -1):
					if Board[y][i] == Board[y][x]:
						return y, i
					elif Board[y][i] != BG2048:
						return None, None
			elif Type == "R":
				for i in range(x + 1, 4):
					if Board[y][i] == Board[y][x]:
						return y, i
					elif Board[y][i] != BG2048:
						return None, None
			return None, None
		else:
			if Type == "U":
				for i in range(y - 1, -1, -1):
					if Board[i][x] == Board[y][x]:
						return i, x
					elif Board[i][x] != BG2048:
						return None, None
			elif Type == "D":
				for i in range(y + 1, 4):
					if Board[i][x] == Board[y][x]:
						return i, x
					elif Board[i][x] != BG2048:
						return None, None

	async def GameOver(Board):
		for x in Board:
			for y in x:
				if y == BG2048:
					return False
		return True

	async def Main():
		Playing = True
		Score = 0
		Board = [[BG2048] * 4 for i in range(4)]
		Embed = discord.Embed(
			title = "2048",
			description = "Preparing game <a:loading:401798527325569034>",
			color = 0x7289da
		)
		GameEnv = await client.send_message(message.channel, embed = Embed)
		for i in ["🔼", "🔽", "◀", "▶"]:
			await client.add_reaction(GameEnv, i)

		Board = await RandomTile(await RandomTile(Board))
		Embed.description = "**Score:** " + str(Score) + "\n\n" + await GenerateBoard(Board) + "\n\nSelect a reaction to move the tiles!"
		await client.edit_message(GameEnv, embed = Embed)

		while Playing:
			Reaction = await client.wait_for_reaction(user = message.author, timeout = 180)
			Changes = False
			if Reaction:
				if Reaction.reaction.emoji == "🔼":
					for x in range(4):
						for y in range(4):
							try:
								if Board[y][x] != BG2048:
									NextY, NextX = await GetNextTile(Board, y, x, "U", False)
									if NextY != None:
										NewValue, P = await Double(Board[y][x])
										Score += NewValue
										Board[NextY][NextX] = Game2048Tiles[NewValue]
										Board[y][x] = BG2048
										Changes = True
										Playing = P
							except:
								0
					for x in range(4):
						for y in range(4):
							for i in range(y - 1, -1, -1):
								if Board[i][x] == BG2048:
									Board[i][x] = Board[i+1][x]
									Board[i+1][x] = BG2048
								else:
									break
				elif Reaction.reaction.emoji == "🔽":
					for x in range(3, -1, -1):
						for y in range(3, -1, -1):
							try:
								if Board[y][x] != BG2048:
									NextY, NextX = await GetNextTile(Board, y, x, "D", False)
									if NextY != None:
										NewValue, P = await Double(Board[y][x])
										Score += NewValue
										Board[NextY][NextX] = Game2048Tiles[NewValue]
										Board[y][x] = BG2048
										Changes = True
										Playing = P
							except:
								0
					for x in range(3, -1, -1):
						for y in range(3, -1, -1):
							for i in range(y + 1, 4):
								if Board[i][x] == BG2048:
									Board[i][x] = Board[i-1][x]
									Board[i-1][x] = BG2048
								else:
									break
				elif Reaction.reaction.emoji == "◀":
					for x in range(4):
						for y in range(4):
							if Board[y][x] != BG2048:
								NextY, NextX = await GetNextTile(Board, y, x, "L", True)
								if NextY != None:
									NewValue, P = await Double(Board[y][x])
									Score += NewValue
									Board[NextY][NextX] = Game2048Tiles[NewValue]
									Board[y][x] = BG2048
									Changes = True
									Playing = P
					for x in range(4):
						for y in range(4):
							for i in range(x - 1, -1, -1):
								if Board[y][i] == BG2048:
									Board[y][i] = Board[y][i+1]
									Board[y][i+1] = BG2048
								else:
									break
					"""for x in range(4):
						for y in range(4):
							for i in range(x-1, -1, -1):
								try:
									NextY, NextX = await GetNextTile(Board, y, i, "L", True)
									Changes = True
									if NextY and Board[y][i] != BG2048:
										NewValue = await Double(Board[y][i])
										Score += NewValue
										Board[NextY][NextX] = Game2048Tiles[NewValue]
										Board[Y][i] = BG2048
									if Board[y][i] == BG2048 and i >= 0:
										Board[y][i] = Board[y][i+1]
										Board[y][i+1] = BG2048
									else:
										break
								except:
									0"""
				elif Reaction.reaction.emoji == "▶":
					for x in range(3, -1, -1):
						for y in range(3, -1, -1):
							if Board[y][x] != BG2048:
								NextY, NextX = await GetNextTile(Board, y, x, "R", True)
								if NextY != None:
									NewValue, P = await Double(Board[y][x])
									Score += NewValue
									Board[NextY][NextX] = Game2048Tiles[NewValue]
									Board[y][x] = BG2048
									Changes = True
									Playing = P
					for x in range(3, -1, -1):
						for y in range(3, -1, -1):
							for i in range(x + 1, 4):
								if Board[y][i] == BG2048:
									Board[y][i] = Board[y][i-1]
									Board[y][i-1] = BG2048
								else:
									break

				Board = await RandomTile(Board)
				if await GameOver(Board):
					Playing = False
					Embed.description = "**Score:** " + str(Score) + "\n\n" + await GenerateBoard(Board) + "\n\n**Game Over!**"
				elif not Playing:
					Embed.description = "**Score:** " + str(Score) + "\n\n" + await GenerateBoard(Board) + "\n\n**You win!**"
				else:
					Embed.description = "**Score:** " + str(Score) + "\n\n" + await GenerateBoard(Board) + "\n\nSelect a reaction to move the tiles!"
				await client.edit_message(GameEnv, embed = Embed)
			else:
				Playing = False

	Msg = await client.send_message(
		message.channel,
		embed = discord.Embed(
			title = "2048",
			description = """Welcome to 2048!

2048 is a 1-player game where you have to try to merge tiles containing equal numbers on a grid by pushing all tiles in a direction. When merged, the numbers on the tiles are doubled and turned into 1 tile with a larger value. Your task is to try and reach the 2048 tile before running out of spaces!

Are you ready to play?""",
			color = 0x7289da
		)
	)
	await client.add_reaction(Msg, "👍")
	await client.add_reaction(Msg, "👎")
	Reaction = await client.wait_for_reaction(user = message.author, timeout = 60)
	if Reaction:
		if Reaction.reaction.emoji == "👍":
			await Main()
		else:
			await client.send_message(message.channel, "👌")

async def GuessCode(message, x, y):
	Number = str(random.randint(1000, 9999))
	Playing = True
	Attempts = 0
	await client.send_message(
		message.channel,
		embed = discord.Embed(
			title = "Guess the Code",
			description = """Welcome to Guess the Code!

Guess the Code is a 1-player game where you have to guess the 4-digit code ranging from `1000 - 9999`. The task is to see how quickly you can guess the chosen number!

To guess, respond with a 4-digit number and I'll tell you how many of your numbers are correct!

To stop playing, you can use `cancel`.""",
			color = 0x7289da
		)
	)
	while Playing:
		Attempts += 1
		Response = await client.wait_for_message(author = message.author, timeout = 60)
		if Response:
			try:
				if Response.content.lower() == "cancel":
					await client.send_message(message.channel, "👌")
					Playing = False
				else:
					Num = int(Response.content)
					if 1000 <= Num <= 9999:
						Num = str(Num)
						Count = 0
						for i in range(4):
							if Num[i] == Number[i]:
								Count += 1
						if Count < 4:
							await client.send_message(message.channel, "You guessed **" + str(Count) + "** of 4 numbers correct.")
						else:
							await client.send_message(message.channel, "Congratulations, you got it right! It took you **" + str(Attempts) + "** attempts to guess " + Number + ".")
					else:
						await client.send_message(message.channel, "Sorry, that number doesn't range from 1000 to 9999!")
			except:
				await client.send_message(message.channel, "That's not a number!")
		else:
			Playing = False

async def Connect4(message, Number, ID):
	async def GenerateBoard(Board, Winner):
		if Winner and Winner != "END":
			for i in Winner:
				Board[i[0]][i[1]] = ["<a:flashingred:593409264895262741>","<a:flashingblue:593409264773758976>"][Board[i[0]][i[1]] == "🔵"]
		return "\n".join(["".join(i) for i in Board])

	async def Main(Opponent, Message):
		ID = str(uuid.uuid1())
		Embed = discord.Embed(
			title = "Connect 4",
			description = "Preparing game <a:loading:401798527325569034>",
			color = 0x7289da,
		)
		Embed.set_footer(text = "Game ID: " + ID)
		GamesInPlay[ID] = {
			"Message": await client.send_message(message.channel, embed = Embed),
			"Message2": await client.edit_message(Message, embed = Embed) if Message else False,
			"Player1": message.author,
			"Player2": Opponent or "CPU",
			"P1Name": message.author.name,
			"P2Name": Opponent.name if Opponent else "CPU",
			"Board": [["⚫"] * 7 for i in range(6)],
			"Embed": Embed,
			"Game": "connect4",
			"WhoseGo": "🔴",
			"ID": ID
		}
		for i in range(1, 8):
			await client.add_reaction(GamesInPlay[ID]["Message"], EmojiNumbers[i])
			if GamesInPlay[ID]["Message2"]:
				await client.add_reaction(GamesInPlay[ID]["Message2"], EmojiNumbers[i])

		Embed.description = "**" + message.author.name + " (🔴)** VS " + GamesInPlay[ID]["P2Name"] + " (🔵)\n\n" + await GenerateBoard(GamesInPlay[ID]["Board"], False) + "\n\nReact with a number to choose your position!"
		await client.edit_message(GamesInPlay[ID]["Message"], embed = Embed)
		if GamesInPlay[ID]["Message2"]:
			await client.edit_message(GamesInPlay[ID]["Message2"], embed = Embed)
		await asyncio.sleep(1200)
		if ID in GamesInPlay:
			await client.delete_message(GamesInPlay[ID]["Message"])
			if GamesInPlay[ID]["Message2"]:
				await client.edit_message(GamesInPlay[ID]["Message2"], embed = Embed)
			del GamesInPlay[ID]

	async def CheckWinner(CurrentGame):
		B = CurrentGame["Board"]
		Full = "END"
		for x in range(7):
			for y in range(6):
				if B[y][x] not in "🔴🔵":
					Full = False
				try:
					for i in "🔴🔵":
						if B[y][x]==B[y][x+1]==B[y][x+2]==B[y][x+3]==i:
							return [[y, x], [y, x+1], [y, x+2], [y, x+3]]
						elif B[y][x]==B[y+1][x]==B[y+2][x]==B[y+3][x]==i:
							return [[y, x], [y+1, x], [y+2, x], [y+3, x]]
						elif B[y][x]==B[y+1][x+1]==B[y+2][x+2]==B[y+3][x+3]==i:
							return [[y, x], [y+1, x+1], [y+2, x+2], [y+3, x+3]]
						elif B[y][x]==B[y+1][x-1]==B[y+2][x-2]==B[y+3][x-3]==i and (x-3) >= 0:
							return [[y, x], [y+1, x-1], [y+2, x-2], [y+3, x-3]]
				except:
					0
		return Full

	async def UpdateBoard(CurrentGame):
		CurrentGame["WhoseGo"] = "🔵🔴"[CurrentGame["WhoseGo"] == "🔵"]
		Names = [CurrentGame["P1Name"] + " (🔴) VS **" + CurrentGame["P2Name"] + " (🔵)**\n\n", "**" + CurrentGame["P1Name"] + " (🔴)** VS " + CurrentGame["P2Name"] + " (🔵)\n\n"][CurrentGame["WhoseGo"] == "🔴"]
		Winner = await CheckWinner(CurrentGame)
		if Winner == "END":
			CurrentGame["Embed"].description = "**It's a draw!**\n\n" + await GenerateBoard(CurrentGame["Board"], Winner) + "\n\nType `g:connect4` to play again!"
			await client.edit_message(CurrentGame["Message"], embed = CurrentGame["Embed"])
			if CurrentGame["Message2"]:
				await client.edit_message(CurrentGame["Message2"], embed = CurrentGame["Embed"])
			del GamesInPlay[CurrentGame["ID"]]
		elif Winner:
			WinnerName = [CurrentGame["P1Name"], CurrentGame["P2Name"]][CurrentGame["Board"][Winner[0][0]][Winner[0][1]] == "🔵"]
			CurrentGame["Embed"].description = "**" + WinnerName + " wins!**\n\n" + await GenerateBoard(CurrentGame["Board"], Winner) + "\n\nType `g:connect4` to play again!"
			await client.edit_message(CurrentGame["Message"], embed = CurrentGame["Embed"])
			if CurrentGame["Message2"]:
				await client.edit_message(CurrentGame["Message2"], embed = CurrentGame["Embed"])
			del GamesInPlay[CurrentGame["ID"]]
			return True
		else:
			CurrentGame["Embed"].description = Names + await GenerateBoard(CurrentGame["Board"], False) + "\n\nReact with a number to choose your position!"
			await client.edit_message(CurrentGame["Message"], embed = CurrentGame["Embed"])
			if CurrentGame["Message2"]:
				await client.edit_message(CurrentGame["Message2"], embed = CurrentGame["Embed"])

	async def CPU(message):
		await Main(False, False)

	async def Friend(message):
		await client.send_message(message.channel, "Please tag the friend you would like to play against!")
		Opponent = await client.wait_for_message(author = message.author, timeout = 300)
		if Opponent:
			if Opponent.mentions != []:
				Opp = Opponent.mentions[0]
				if Opp != message.author:
					Msg = await client.send_message(message.channel, "Hey, <@" + Opp.id + ">! You've been invited to a game of Connect 4! Would you like to play?")
					await client.add_reaction(Msg, "👍")
					await client.add_reaction(Msg, "👎")
					Reaction = await client.wait_for_reaction(user = Opp, timeout = 300)
					if Reaction:
						if Reaction.reaction.emoji == "👍":
							await Main(Opp, False)
						else:
							await client.send_message(message.channel, "👌")
				else:
					await client.send_message(message.channel, "You can't play against yourself! Type `g:connect4` to start again!")
			else:
				await client.send_message(message.channel, "Sorry, I couldn't find any users. Type `g:connect4` to start again!")

	async def Random(message):
		if "connect4" in Searching:
			Opponent = Searching["connect4"]
			if Opponent["User"] != message.author:
				del Searching["connect4"]
				await Main(Opponent["User"], Opponent["Message"])
			else:
				await client.send_message(message.channel, "You can't play against yourself! Type `g:connect4` to start again!")
		else:
			Embed = discord.Embed(
				title = "Connect 4",
				description = "Searching for opponent <a:loading:401798527325569034>",
				color = 0x7289da,
			)
			Searching["connect4"] = {
				"User": message.author,
				"Message": await client.send_message(
					message.channel,
					embed = Embed
				)
			}
	async def Position(Board, Number):
		Y = 6
		for i in Board[::-1]:
			Y -= 1
			if i[Number - 1] == "⚫":
				return Y
		return None

	async def CPUMove(CurrentGame, LastPos):
		Choices = []
		BestChoices = []
		for i in range(1, 8):
			ChoicePos = await Position(CurrentGame["Board"], i)
			if ChoicePos != None:
				Choices += [{
					"X": i,
					"Y": ChoicePos
				}]
				if abs(i - LastPos) <= 1:
					BestChoices += [{
						"X": i,
						"Y": ChoicePos
					}]
		if random.randint(1, 2) == 1:
			Chosen = random.choice(BestChoices)
			CurrentGame["Board"][Chosen["Y"]][Chosen["X"] - 1] = "🔵"
		else:
			Chosen = random.choice(Choices)
			CurrentGame["Board"][Chosen["Y"]][Chosen["X"] - 1] = "🔵"
		await UpdateBoard(CurrentGame)

	if Number:
		CurrentGame = GamesInPlay[ID]
		Board = CurrentGame["Board"]
		NextMove = await Position(Board, Number)
		if NextMove != None:
			Board[NextMove][Number - 1] = CurrentGame["WhoseGo"]
			if await UpdateBoard(CurrentGame):
				return
			if CurrentGame["Player2"] == "CPU":
				await asyncio.sleep(random.uniform(0, 1))
				await CPUMove(CurrentGame, Number)
	else:
		await client.send_message(
			message.channel,
			embed = discord.Embed(
				title = "Connect 4",
				description = """Welcome to Connect 4!

Connect 4 is a 2-player game on a 7x6 grid where you have to get four-in-a-row. You get to choose which column you drop your chip in and it falls to the bottom of that column.

Who would you like to play against?
- `cpu` The computer
- `friend` A player in this server
- `random` A random player
- `cancel` Cancel request""",
				color = 0x7289da
			)
		)

		Options = {
			"cpu": CPU,
			"friend": Friend,
			"random": Random
		}

		Response = await client.wait_for_message(author = message.author, timeout = 60)
		if Response:
			if Response.content.lower() in Options.keys():
				await Options[Response.content.lower()](message)
			elif Response.content == "cancel":
				await client.send_message(message.channel, "👌")
			else:
				await client.send_message(message.channel, "Sorry, that's not a valid response! Please use `g:connect4` to start again.")

async def Trivia(message, Channel, x):
	async def SetupQuestion(Question, QuestionNo):
		Embed = discord.Embed(
			title = "Trivia",
			description = "**Question " + str(QuestionNo) + ":**\n" + Question["Question"]["Title"],
			color = 0x7289da,
		)
		if Question["Type"] == "Image":
			Embed.set_image(url = requote_uri(Question["Question"]["Image"]))
		return Embed

	async def SetupLeaderboard(Leaderboard):
		Ordered = sorted(Leaderboard, key = Leaderboard.get, reverse = True)
		Board = "\n".join([("**" + i + "**: " + str(Leaderboard[i]) + " points") for i in Ordered])
		return discord.Embed(
			title = "Trivia Leaderboard",
			description = Board,
			color = 0x7289da,
		)

	async def NextQuestion(Q, Question):
		if Q["QuestionNo"] < 10:
			Q["QuestionNo"] += 1
			Num = Q["QuestionNo"]
			Question = Q["Questions"][Q["QuestionNo"] - 1]
			Embed = await SetupQuestion(Question, Q["QuestionNo"])
			await client.send_message(message.channel, embed = Embed)
			await asyncio.sleep(20)
			if Q:
				if Q["QuestionNo"] == Num and not Q["Finished"]:
					await client.send_message(message.channel, "Time's up! The correct answer was **" + Question["Question"]["Answers"][0].title() + "**.")
					await NextQuestion(Q, Question)
		else:
			Embed = await SetupLeaderboard(Q["Leaderboard"])
			await client.send_message(message.channel, embed = Embed)
			Q["Finished"] = True
			del ServerTriviaChannels[message.channel]

	async def Server(Category):
		if message.channel not in ServerTriviaChannels.keys():
			Questions = Data["Trivia"][Category]
			random.shuffle(Questions)
			QuestionNo = 1
			Question = Questions[QuestionNo - 1]
			Embed = await SetupQuestion(Question, QuestionNo)
			await client.send_message(message.channel, embed = Embed)
			ServerTriviaChannels[message.channel] = {
				"QuestionNo": 1,
				"Questions": Questions,
				"Leaderboard": {},
				"Finished": False
			}
			await asyncio.sleep(20)
			Q = ServerTriviaChannels[message.channel]
			if Q["QuestionNo"] == 1 and not Q["Finished"]:
				await client.send_message(message.channel, "Time's up! The correct answer was **" + Question["Question"]["Answers"][0].title() + "**.")
				await NextQuestion(Q, Question)
		else:
			await client.send_message(message.channel, "There is already a game in progress!")

	async def Solo(Category):
		Questions = Data["Trivia"][Category]
		random.shuffle(Questions)
		QuestionNo = 0
		while True:
			QuestionNo += 1
			Question = Questions[QuestionNo - 1]
			Embed = await SetupQuestion(Question, QuestionNo)
			await client.send_message(message.channel, embed = Embed)
			Answer = await client.wait_for_message(author = message.author, timeout = 60)
			if Answer:
				if Answer.content.lower() in Question["Question"]["Answers"]:
					await client.send_message(message.channel, "Correct! You're now at " + str(QuestionNo) + " points!")
				else:
					await client.send_message(message.channel, "Sorry, that's wrong! The correct answer was **" + Question["Question"]["Answers"][0].title() + "**. You scored " + str(QuestionNo - 1) + " points!")
					break
			else:
				await client.send_message(message.channel, "Time's up! You scored " + str(QuestionNo - 1) + " points!")
				break

	if Channel:
		Q = ServerTriviaChannels[Channel]
		Num = Q["QuestionNo"]
		Question = Q["Questions"][Q["QuestionNo"] - 1]["Question"]
		if message.content.lower() in Question["Answers"]:
			await client.send_message(Channel, "You got it, <@" + message.author.id + ">! **+1** point")
			if message.author.name in Q["Leaderboard"].keys():
				Q["Leaderboard"][message.author.name] += 1
			else:
				Q["Leaderboard"][message.author.name] = 1
			if Num == Q["QuestionNo"]:
				await NextQuestion(Q, Question)
			
	else:
		Categories = {
			"flags": "flags",
			"cities": "capital cities"
		}
		CatList = "\n".join([("- `" + i + "` " + Categories[i].title()) for i in Categories])
		Embed = discord.Embed(
			title = "Trivia",
			description = """Welcome to the Trivia game!

In this game, you will be given a set of questions based on a certain theme. Depending on the gamemode you choose, you can either see how many points you can get by yourself, or compete against your friends!

Please select a category:
""" + CatList,
			color = 0x7289da,
		)
		await client.send_message(message.channel, embed = Embed)
		Response = await client.wait_for_message(author = message.author, timeout = 60)
		if Response:
			Msg = Response.content.lower()
			if Msg in Categories.keys():
				Embed = discord.Embed(
					title = "Trivia",
					description = """Great choice!

Please choose a gamemode:
- `solo` Play until you get a question wrong for the highest score!
- `server` Compete against everyone in the server for the most points after 10 questions!""",
					color = 0x7289da,
				)
				await client.send_message(message.channel, embed = Embed)
				Gamemode = await client.wait_for_message(author = message.author)
				if Gamemode:
					Mode = Gamemode.content.lower()
					if Mode == "solo":
						await Solo(Msg)
					elif Mode == "server":
						await Server(Msg)
					else:
						await client.send_message(message.channel, "Sorry, that's not a valid option! Type `g:trivia` to start again!")
			else:
				await client.send_message(message.channel, "Sorry, that's not a valid option! Type `g:trivia` to start again!")

async def RockPaperScissors(message, Number, ID):
	GetMove = {"r":"Rock", "p":"Paper", "s":"Scissors"}

	async def CalcWinner(Move, BotsMove):
		def CheckWinner(Choice, Winner, Loser):
			if Choice == Winner: return "Congratulations, you win!"
			elif Choice == Loser: return "The CPU wins."
			else: return "It's a draw!"

		if Move == "r": return CheckWinner(BotsMove, "s", "p")
		elif Move == "p": return CheckWinner(BotsMove, "r", "s")
		elif Move == "s": return CheckWinner(BotsMove, "p", "r")

	Embed = discord.Embed(
		title = "Rock, Paper, Scissors!",
		description = """Welcome to Rock, Paper, Scissors!

Rock, Paper, Scissors is a simple 2-player game played against a CPU where you have to choose either rock, paper or scissors. If your object beats your opponent's object, you win!

Notes:
- Rocks destroy scissors
- Scissors cut paper
- Paper wraps around rock

Type `rock`, `paper` or `scissors`!""",
		color = 0x7289da,
	)
	await client.send_message(message.channel, embed = Embed)
	Response = await client.wait_for_message(author = message.author, timeout = 60)
	if Response:
		Move = Response.content.lower()[0]
		BotsMove = random.choice(["r", "p", "s"])
		if Move in "rps":
			Embed = discord.Embed(
				title = "Rock, Paper, Scissors!",
				description = "**You chose:** " + GetMove[Move] + "\n**CPU chose:** " + GetMove[BotsMove] + "\n\n" + await CalcWinner(Move, BotsMove),
				color = 0x7289da
			)
			await client.send_message(message.channel, embed = Embed)
		else:
			await client.send_message(message.channel, "Sorry, that's not a valid move! Type `g:rps` to start again!")

async def TicTacToe(message, Number, ID):
	async def Main(Opponent, Message):
		ID = str(uuid.uuid1())
		Embed = discord.Embed(
			title = "Tic-Tac-Toe",
			description = "Preparing game <a:loading:401798527325569034>",
			color = 0x7289da,
		)
		Embed.set_footer(text = "Game ID: " + ID)
		GamesInPlay[ID] = {
			"Message": await client.send_message(message.channel, embed = Embed),
			"Message2": await client.edit_message(Message, embed = Embed) if Message else False,
			"Player1": message.author,
			"Player2": Opponent or "CPU",
			"P1Name": message.author.name,
			"P2Name": Opponent.name if Opponent else "CPU",
			"Board": ["-", "-", "-", "-", "-", "-", "-", "-", "-"],
			"Embed": Embed,
			"Game": "tictactoe",
			"WhoseGo": "X",
			"ID": ID
		}
		for i in range(1, 10):
			await client.add_reaction(GamesInPlay[ID]["Message"], EmojiNumbers[i])
			if GamesInPlay[ID]["Message2"]:
				await client.add_reaction(GamesInPlay[ID]["Message2"], EmojiNumbers[i])

		Embed.description = "**" + message.author.name + " (X)** VS " + GamesInPlay[ID]["P2Name"] + " (O)\n\n" + """```
---
---
---```

React with a number to choose your position!"""
		await client.edit_message(GamesInPlay[ID]["Message"], embed = Embed)
		if GamesInPlay[ID]["Message2"]:
			await client.edit_message(GamesInPlay[ID]["Message2"], embed = Embed)
		await asyncio.sleep(300)
		if ID in GamesInPlay:
			await client.delete_message(GamesInPlay[ID]["Message"])
			if GamesInPlay[ID]["Message2"]:
				await client.edit_message(GamesInPlay[ID]["Message2"], embed = Embed)
			del GamesInPlay[ID]

	async def CheckWinner(CurrentGame):
		B = CurrentGame["Board"]
		for i in "XO":
			if B[0]==B[1]==B[2]==i or B[3]==B[4]==B[5]==i or B[6]==B[7]==B[8]==i or B[0]==B[4]==B[8]==i or B[2]==B[4]==B[6]==i or B[0]==B[3]==B[6]==i or B[1]==B[4]==B[7]==i or B[2]==B[5]==B[8]==i:
				return [CurrentGame["P1Name"], CurrentGame["P2Name"]][i == "O"] + " wins!"
		if B[0]!="-"and B[1]!="-"and B[2]!="-"and B[3]!="-"and B[4]!="-"and B[5]!="-"and B[6]!="-"and B[7]!="-"and B[8]!="-":
			return "It's a Draw!"

	async def UpdateBoard(CurrentGame):
		CurrentGame["WhoseGo"] = "OX"[CurrentGame["WhoseGo"] == "O"]
		Layout = "".join(Board[:3]) + "\n" + "".join(Board[3:6]) + "\n" + "".join(Board[6:]) + "\n"
		Names = [CurrentGame["P1Name"] + " (X) VS **" + CurrentGame["P2Name"] + " (O)**\n\n", "**" + CurrentGame["P1Name"] + " (X)** VS " + CurrentGame["P2Name"] + " (O)\n\n"][CurrentGame["WhoseGo"] == "X"]
		Winner = await CheckWinner(CurrentGame)
		if Winner:
			CurrentGame["Embed"].description = "**" + Winner + "**\n\n```\n" + Layout + "```\n\nType `g:tictactoe` to play again!"
			await client.edit_message(CurrentGame["Message"], embed = CurrentGame["Embed"])
			if CurrentGame["Message2"]:
				await client.edit_message(CurrentGame["Message2"], embed = CurrentGame["Embed"])
			del GamesInPlay[CurrentGame["ID"]]
			return True
		else:
			CurrentGame["Embed"].description = Names + "```\n" + Layout + "```\n\nReact with a number to choose your position!"
			await client.edit_message(CurrentGame["Message"], embed = CurrentGame["Embed"])
			if CurrentGame["Message2"]:
				await client.edit_message(CurrentGame["Message2"], embed = CurrentGame["Embed"])

	async def CPU(message):
		await Main(False, False)

	async def Friend(message):
		await client.send_message(message.channel, "Please tag the friend you would like to play against!")
		Opponent = await client.wait_for_message(author = message.author, timeout = 300)
		if Opponent:
			if Opponent.mentions != []:
				Opp = Opponent.mentions[0]
				if Opp != message.author:
					Msg = await client.send_message(message.channel, "Hey, <@" + Opp.id + ">! You've been invited to a game of Tic-Tac-Toe! Would you like to play?")
					await client.add_reaction(Msg, "👍")
					await client.add_reaction(Msg, "👎")
					Reaction = await client.wait_for_reaction(user = Opp, timeout = 300)
					if Reaction:
						if Reaction.reaction.emoji == "👍":
							await Main(Opp, False)
						else:
							await client.send_message(message.channel, "👌")
				else:
					await client.send_message(message.channel, "You can't play against yourself! Type `g:tictactoe` to start again!")
			else:
				await client.send_message(message.channel, "Sorry, I couldn't find any users. Type `g:tictactoe` to start again!")

	async def Random(message):
		if "tictactoe" in Searching:
			Opponent = Searching["tictactoe"]
			if Opponent["User"] != message.author:
				del Searching["tictactoe"]
				await Main(Opponent["User"], Opponent["Message"])
			else:
				await client.send_message(message.channel, "You can't play against yourself! Type `g:tictactoe` to start again!")
		else:
			Embed = discord.Embed(
				title = "Tic-Tac-Toe",
				description = "Searching for opponent <a:loading:401798527325569034>",
				color = 0x7289da,
			)
			Searching["tictactoe"] = {
				"User": message.author,
				"Message": await client.send_message(
					message.channel,
					embed = Embed
				)
			}

	async def CPUMove(CurrentGame):
		Choice = -1
		while Choice < 0 or CurrentGame["Board"][Choice] != "-":
			Choice = random.randint(0, 8)
		CurrentGame["Board"][Choice] = "O"
		await UpdateBoard(CurrentGame)

	if Number:
		CurrentGame = GamesInPlay[ID]
		Board = CurrentGame["Board"]
		if Board[Number - 1] == "-":
			Board[Number - 1] = CurrentGame["WhoseGo"]
			if await UpdateBoard(CurrentGame):
				return
			if CurrentGame["Player2"] == "CPU":
				await asyncio.sleep(random.uniform(0, 1))
				await CPUMove(CurrentGame)
	else:
		await client.send_message(
			message.channel,
			embed = discord.Embed(
				title = "Tic-Tac-Toe",
				description = """Welcome to Tic-Tac-Toe!

Tic-Tac-Toe is a 2-player game where each player is assigned a value, X or O. Each player takes turn to place their value on a 3x3 board. Get three-in-a-row to win!

The numbers you will be given to react with represent the following positions:
```
123
456
789
```
Who would you like to play against?
- `cpu` The computer
- `friend` A player in this server
- `random` A random player
- `cancel` Cancel request""",
				color = 0x7289da
			)
		)

		Options = {
			"cpu": CPU,
			"friend": Friend,
			"random": Random
		}

		Response = await client.wait_for_message(author = message.author, timeout = 60)
		if Response:
			if Response.content.lower() in Options.keys():
				await Options[Response.content.lower()](message)
			elif Response.content == "cancel":
				await client.send_message(message.channel, "👌")
			else:
				await client.send_message(message.channel, "Sorry, that's not a valid response! Please use `g:tictactoe` to start again.")


async def Help(message, x, y):
	await client.send_message(
		message.channel,
		embed = discord.Embed(
			title = "Help",
			description = """Hey there, my name is Gamer. I'm an open-source bot originally made for Discord Hack Week 2019!

I have an expanding library of games for you to try in chat! Want to take a look at all my games? Just type `g:games` :blush:

If you would like to view my source, you can do so [here](https://github.com/JoshSCF/gamer-bot).""",
			color = 0x7289da
		)
	)

async def Games(message, x, y):
	await client.send_message(
		message.channel,
		embed = discord.Embed(
			title = "Games",
			description = "\n".join([("**" + x + "**: `" + GameList[x] + "`") for x in GameList]),
			color = 0x7289da
		)
	)

Commands = {
	"help": Help,
	"games": Games,
	"tictactoe": TicTacToe,
	"rps": RockPaperScissors,
	"trivia": Trivia,
	"connect4": Connect4,
	"code": GuessCode,
	"2048": Game2048,
	"hangman": Hangman,
	"minesweeper": Minesweeper,
	"countdown": Countdown,
	#"simonsays": SimonSays
}

@client.event
async def on_reaction_add(reaction, user):
	if reaction.message.author.id == "592762698064986112":
		if user.id != "592762698064986112":
			Embed = reaction.message.embeds[0]
			if "footer" in Embed:
				ID = Embed["footer"]["text"].split(": ")[1]

				Number = GetNumberFromEmoji(reaction.emoji)
				if ID in GamesInPlay.keys():
					if Number:
						CurrentGame = GamesInPlay[ID]
						if CurrentGame["Game"] == "tictactoe":
							if (CurrentGame["WhoseGo"] == "X" and CurrentGame["Player1"] == user) or (CurrentGame["Player2"] == user and CurrentGame["WhoseGo"] == "O"):
								await Commands[CurrentGame["Game"]](False, Number, ID)
						elif CurrentGame["Game"] == "connect4":
							if (CurrentGame["WhoseGo"] == "🔴" and CurrentGame["Player1"] == user) or (CurrentGame["Player2"] == user and CurrentGame["WhoseGo"] == "🔵"):
								await Commands[CurrentGame["Game"]](False, Number, ID)
					elif GamesInPlay[ID]["Game"] == "simonsays":
						await SimonSays(user, reaction, ID)
			await client.remove_reaction(reaction.message, reaction.emoji, user)

@client.event
async def on_message(message):
	if message.content.startswith("g:"):
		Command = message.content[2:]
		if Command in Commands.keys():
			await Commands[Command](message, False, False)
		else:
			await client.send_message(message.channel, "Sorry, that is not a valid command!")
	elif message.channel in ServerTriviaChannels.keys():
		await Trivia(message, message.channel, False)
	elif message.channel in HangmanChannels.keys():
		await Hangman(message, message.channel, message.content)
	elif message.channel in CountdownChannels.keys():
		if CountdownChannels[message.channel]["Checking"]:
			await Countdown(message, message.channel, message.content)

@client.event
async def on_ready():
	print("READY!")
	await client.change_presence(game = discord.Game(name = "g:help"))

client.run(Token)
