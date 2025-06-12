import os
import subprocess
import time
from discord_webhook import DiscordWebhook
from discord_webhook import DiscordEmbed

class PerforceLogger():
    def __init__(self, webhookURL):
        """Initialize the Perforce logger with Discord webhook integration.

        :param str webhookURL: The Discord webhook URL to post notifications to
        """
        self.webhookURL = webhookURL
        self.global_store = {
            'latest_change': ''
        }

    def checkP4(self):
        """Query Perforce server for the most recent change.

        :return str: The decoded output of the most recent Perforce change
        """
        p4Changes = subprocess.Popen('p4 changes -t -m 1 -l', stdout=subprocess.PIPE, shell=True)
        return p4Changes.stdout.read().decode('ISO-8859-1')

    def checkForChanges(self, output):
        """Check if the latest Perforce change is new and should be reported.

        :param str output: The output from the Perforce changes command
        :return str: The change information if it's new and not pending, empty string otherwise
        """
        if output != self.global_store['latest_change']:
            self.global_store['latest_change'] = output

            if '*pending*' in output: 
                return ''

            else:
                return output

        else: 
            return ''

    def postChanges(self):
        """Post new Perforce changes to Discord via webhook.

        Checks for new changes and posts them to the configured Discord channel
        if any are found. Changes are formatted with a custom color and author.
        """
        output = self.checkP4()
        payload = self.checkForChanges(output)

        if payload != '':
            message = DiscordWebhook(self.webhookURL)
            message.set_content(color=0xc8702a, description='`%s`' % (payload))
            message.set_author(name='Perforce')
            message.set_footer(text='RikshawStudios/perforce-commit-discord-bot', ts=True)
            message.send()

            # webhook = DiscordWebhook(self.webhookURL)
            # embedData = DiscordEmbed(title="Perforce Commit", description='`%s`' % (payload), color=0xc8702a)
            #
            # # set author
            # embedData.set_author(name="Perforce", url="author url", icon_url="author icon url")
            # # set image
            # embedData.set_image(url="your image url")
            # # set footer
            # embedData.set_footer(text='RikshawStudios/perforce-commit-discord-bot', icon_url="URL of icon")
            #
            # webhook.add_embed(embedData)
            #
            # webhook.execute()


        else:
            return

if __name__ == "__main__":
    """Main application entry point.

    Initializes the Perforce logger and runs an infinite loop that checks for
    changes every 30 seconds.
    """
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
    logger = PerforceLogger(DISCORD_WEBHOOK_URL)
    timer = time.time()

    while True:
        logger.postChanges()
        time.sleep(30.0 - ((time.time() - timer) % 30.0))