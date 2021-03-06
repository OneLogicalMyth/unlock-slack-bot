import time, re
from slackclient import SlackClient
from unlocked import unlocked

# instantiate Slack client
slack_client = SlackClient('<<API_TOKEN>>')
RTM_READ_DELAY = 2 # 2 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:

            # if direct message you don't need @BotName
            if event["channel"].startswith('D') and not event["user"] == starterbot_id:
               return event["text"], event["channel"], event["user"]

            # look for @BotName in channel
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"], event["user"]

    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """    # Default response is help text for the user
    default_response = "Sorry don't understand that. Commands are as follows:\n`unlocked` - record the machine as unlocked\n`stats` - current unlock count per user"
    response = None

    user_info = slack_client.api_call(
       "users.info",
       user=user
    )

    user_display_name = user_info["user"]["profile"]["display_name"]

    # debug
    print "The bot was mentioned in the channel '{}' by the user '{}' with the command of '{}'".format(channel,user,command)

    # process commands
    if command == 'unlocked':
        response = unlocked().unlocked(user,user_display_name)

    if command == 'stats':
        response = unlocked().stats()

    # send response to slack
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        as_user=True,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False,auto_reconnect=True):
        print("Unlock Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            try:
                command, channel, user = parse_bot_commands(slack_client.rtm_read())
                if command:
                    command = command.lower()
                    handle_command(command, channel, user)
            except Exception as e:
                print "ERROR: The command '" + str(command) + "' was sent by '" + str(user) + "' but failed, exception is '" + str(e) + "'"
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
