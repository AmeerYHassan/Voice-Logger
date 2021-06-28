
# Voice Logger Bot

![transparent_mic](https://user-images.githubusercontent.com/57303145/123701145-743ab880-d82f-11eb-8808-9af6f5d166c2.png)

This is a discord bot that monitors the voice channels in a server. The bot records when a user enters or leaves a voice channel, records the total time a user is in the voice channel, and posts a log of all of the activities that happens during a conversation in the voice channel. All of the logs are persisted, so each person in the server can view the history of voice conversations.

The total time each user is in a voice chat is persisted as well, allowing the users of the server to see who has spent the most time in voice channels.

## Tech used
* The [discord.py](https://pypi.org/project/discord.py/) python module is used to interact with the official Discord API. 
* Information is logged and persisted using [MongoDB](http://mongodb.com/). 
* The bot itself is hosted on an [AWS EC2 instance](https://aws.amazon.com/).

## Features

### Voice Log Messages
![voice_logger_description](https://user-images.githubusercontent.com/57303145/123700908-1e661080-d82f-11eb-9e1a-837b8be6eb8d.png)

### Verbosity Mode
![verbosity_ss](https://user-images.githubusercontent.com/57303145/123700900-1c03b680-d82f-11eb-82a1-34edb5e90e98.png)

### Viewing Voice Chat History 
![history_pagination](https://user-images.githubusercontent.com/57303145/123700881-127a4e80-d82f-11eb-85da-ca96b2bbae55.png)

## Commands Used
`/set_channel` - Used to set the text channel that the bot will send messages to.
`/vc_history` - Used to view the history of the voice chats in a server.
`/set_verbosity` - Allows the user to toggle whether they want each voice chat activity to have it's own embed message.

## Planned Features
* Allowing each server owner to set their own timezone and having the time automatically converted.
* Implementing the command to allow server members to view the most active voice members.
	* The data of each user is already logged, just need to work on the front-end for it.
* If [discord.py](https://pypi.org/project/discord.py/) implements recieving the voice channel audio, I'd like to work on recording voice chats.
	* Record each user on their own channel.
	* Send the audio to Google Audio Transcription for automatic transcription of audio for each person.
