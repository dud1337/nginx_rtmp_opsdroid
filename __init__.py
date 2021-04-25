######################################################################
#   
#   nginx RTMP watcher
#       Announces status of an RTMP stream on nginx
#   
#   1. Avoid spamming
#   2. Stream grabbing
#
######################################################################
from aiohttp.web import Request
from opsdroid.skill import Skill
from opsdroid.matchers import match_regex, match_crontab, match_event, match_webhook, match_always
from opsdroid.events import Message, Reaction, Image, Video, RoomDescription

import datetime
import requests

class nginxRTMPMonitor(Skill):
    def __init__(self, *args, **kwargs):
        super(nginxRTMPMonitor, self).__init__(*args, **kwargs)
        self.bot_was_last_message = False

        self.bot_thinks_stream_is_up = self.check_stream_status()

        if self.bot_thinks_stream_is_up:
            self.stream_since_when = datetime.datetime.today() - datetime.timedelta(hours=1)
        else:
            self.stream_since_when = False


    ##################################################################
    #
    #   1. Avoid spamming
    #       The bot notifies if a stream is ongoing every hour
    #       if no one posts within that hour, it is superfluous;
    #       this functionality prevents that.
    #
    ##################################################################
    async def avoid_spam_send(self, msg):
        if not self.bot_was_last_message:
            await self.opsdroid.send(
                Message(
                    text=msg,
                    target=self.config.get('room_test')
                )
            )
            self.bot_was_last_message = True
        else:
            pass

    @match_always
    async def who_last_said(self, event):
        self.bot_was_last_message = False


    ##################################################################
    #
    #   1. Stream monitoring
    #       Monitors stream
    #
    ##################################################################
    def check_stream_status(self):
        return bool(int(requests.get(self.config.get('stream_status_url')).text[0]))

    def take_stream_screenshot(self):
        pass

    @match_webhook('stream')
    async def streamwebhookskill(self, event: Request):
        # Capture the post data
        data = await event.json()

        if data['stream_state_change'] == 'start':
            await self.opsdroid.send(
                Message(
                    text='<h1>⚡️ STARTED <a href="' + self.config.get('stream_url') + '">STREAMIN\'</a> ⚡️</h1>',
                    target=self.config.get('room_notify')
                )
            )
            self.bot_thinks_stream_is_up = True
            self.stream_since_when = datetime.datetime.today()
        elif data['stream_state_change'] == 'stop':
            await self.opsdroid.send(
                Message(
                    text='<h1>⚰️ STREAM OVER ⚰️</h1>',
                    target=self.config.get('room_notify')
                )
            )
            self.bot_thinks_stream_is_up = False
            self.stream_since_when = False

    @match_crontab('* * * * *', timezone="Europe/Zurich")
    async def stream_ongoing(self, event):
        if self.bot_thinks_stream_is_up:
            stream_up = self.check_stream_status()
            if stream_up:
                if (datetime.datetime.today() - self.stream_since_when) > datetime.timedelta(hours=1):
                    await self.avoid_spam_send(
                        '<h1>⚡️ <a href="' + self.config.get('stream_url') + '">STREAMIN\'</a> ⚡️</h1>'
                    )
                self.stream_since_when = datetime.datetime.today()
