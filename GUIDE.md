## Welcome to RoInvites!
RoInvites tracks your playtime on Roblox, sends out invites, and lets you create leaderboards based on your playtime data.<br>
Below you can find a guide on how to use this bot.<br>

### Adding yourself to the bot
Adding yourself to RoInvites is super easy!<br>
To add yourself to the bot, run `/user add YOUR_USERNAME`. You will need to verify your Roblox account.<br>
**Make sure to friend [@RobloxInvitesHolder](https://www.roblox.com/users/11263892678/profile) so you can be tracked properly.**<br>

Run `/server link` on any servers you want to link your Discord account with.<br>
You'll need to do this to participate in server leaderboards and for invite/leave messages to show in servers.<br>

### Removing yourself from the bot
Removing yourself from RoInvites is equally easy.<br>
To remove yourself from the bot, run `/user remove`. All of your data (besides server snapshots) will be deleted.<br>
If you only want to stop being tracked in a specific server, you can run `/server unlink` in that server.

### Leaderboards
Leaderboards are a fun way to rank yourself against other users in the same server as you.<br>
They can also be used to rank games based on their playtime.<br>

`all` refers to all-time leaderboards, while `snapshot` refers to since-last-snapshot leaderboards.
`/leaderboard breakdown_user [all | snapshot]` gives the leaderboard for all users in a server.<br>
`/leaderboard breakdown_game [all | snapshot]` gives the leaderboard for all games in a server.<br>
`/leaderboard user [all | snapshot] USERNAME` gives the leaderboard for any given user's games.<br>
`/leaderboard game [all | snapshot] PLACE_ID` gives the leaderboard for any given game.<br>

### Custom Titles
Custom Titles add your unique twist on any game you choose!<br>
You can customize the title and color of an invite message for any game.<br>

Add a Custom Title using `/custom_title add TITLE PLACE_ID HEX_COLOR`.<br>
Server admins can remove a Custom Title using `/custom_title remove PLACE_ID`.

### Blacklisting games
Some games may excessively spam the #roblox-invites channel.<br>
You can hide these games from being shown (however, server members will still accumulate playtime on these games).<br>

Server admins can blacklist a game using `/blacklist add PLACE_ID GAME_NAME`.<br>
Server admins can un-blacklist a game using `/blacklist remove PLACE_ID`.

### RoInvites, the app
To use commands anywhere on Discord, click RoInvites' bio and click *Add App*. Add the bot to *My Apps*.<br>
The below commands can be used anywhere on Discord.

To send invite messages to anyone, you can run `/send_invite`.<br>
To show other users your statistics, you can run `/user my_stats`.<br>