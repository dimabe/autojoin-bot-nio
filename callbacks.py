"""Events callbacks."""

from chat_functions import (
    send_text_to_room,
)
from bot_commands import Command
from nio import (
    JoinError,
)
from message_responses import Message

import logging
import time

logger = logging.getLogger(__name__)


class Callbacks(object):
    """Event callbacks."""

    def __init__(self, client, store, config):
        """
        Class constructor.

        Args:
            client (nio.AsyncClient): nio client used to interact with matrix

            store (Storage): Bot storage

            config (Config): Bot configuration parameters
        """
        self.client = client
        self.store = store
        self.config = config
        self.command_prefix = config.command_prefix

    async def message(self, room, event):
        """Callback for when a message event is received.

        Args:
            room (nio.rooms.MatrixRoom): The room the event came from

            event (nio.events.room_events.RoomMessageText): The event defining the message

        """
        # Extract the message text
        msg = event.body

        # Ignore messages from ourselves
        if event.sender == self.client.user:
            return
        # if event.origin_server_ts < time.time() - 1000:
        #     return

        logger.debug(
            f"Bot message received for room {room.display_name} | "
            f"{room.user_name(event.sender)}: {msg}"
        )

        # Process as message if in a public room without command prefix
        has_command_prefix = msg.startswith(self.command_prefix)
        print(f"ROOM IS GROUP??? {room.is_group}")
        if not has_command_prefix and not room.is_group:
            # General message listener
            message = Message(self.client, self.store, self.config, msg, room, event)
            await message.process()
            return

        # Otherwise if this is in a 1-1 with the bot or features a command prefix,
        # treat it as a command
        if has_command_prefix:
            # Remove the command prefix
            msg = msg[len(self.command_prefix):]

        command = Command(self.client, self.store, self.config, msg, room, event)
        await command.process()

    async def invite(self, room, event):
        """Callback for when an invite is received. Join the room specified in the invite."""
        logger.debug(f"Got invite to {room.room_id} from {event.sender}.")

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.client.join(room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt, result.message,
                )
            else:
                logger.info(f"Joined {room.room_id}")
                break

    async def joined(self, room, event):
        """Callback for when the agent accepts the invite."""
        logger.debug(f"Got room.member.event {event.membership} from {event.sender}.")
        if event.membership == "join" and event.sender != "@dianabot:localhost":
            text = f"Welcome {event.sender}"
            await send_text_to_room(self.client, room.room_id, text)
        elif event.membership == "leave" and event.sender == "@agent1:localhost":
            text = f"Agent {event.sender} rejected the invitation"
            await send_text_to_room(self.client, room.room_id, text)
