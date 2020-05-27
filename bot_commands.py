"""Bot commands.."""

from chat_functions import send_text_to_room
from nio import (
    RoomInviteError,
    RoomKickError,
)
import logging
logger = logging.getLogger(__name__)


class Command(object):
    """Bot commands."""

    def __init__(self, client, store, config, command, room, event):
        """A command made by a user.

        Args:
            client (nio.AsyncClient): The client to communicate to matrix with

            store (Storage): Bot storage

            config (Config): Bot configuration parameters

            command (str): The command and arguments

            room (nio.rooms.MatrixRoom): The room the command was sent in

            event (nio.events.room_events.RoomMessageText): The event describing the command
        """
        self.client = client
        self.store = store
        self.config = config
        self.command = command
        self.room = room
        self.event = event
        self.args = self.command.split()[1:]

    async def process(self):
        """Process the command."""
        if self.command.startswith("echo"):
            await self._echo()
        elif self.command.startswith("agent"):
            await self._invite_agent()
        elif self.command.startswith("kick"):
            await self._kick_agent()
        elif self.command.startswith("leave"):
            await self._bot_leave()
        elif self.command.startswith("help"):
            await self._show_help()
        else:
            await self._unknown_command()

    async def _echo(self):
        """Echo back the command's arguments."""
        logger.debug(f"Estoy en echo command")
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _invite_agent(self):
        """Invite an agent."""
        logger.debug(f"Estoy en invite command")
        agent_id = "@agent1:localhost"
        invite_response = await self.client.room_invite(self.room.room_id, agent_id)
        if type(invite_response) == RoomInviteError:
            logger.error(f"Failed to invite: {agent_id} : {invite_response.message}")

    async def _kick_agent(self):
        """Kick an agent."""
        logger.debug(f"Estoy en kick command")
        agent_id = "@agent1:localhost"
        kick_response = await self.client.room_kick(self.room.room_id, agent_id, "Porque quise")
        if type(kick_response) == RoomKickError:
            logger.error(f"Failed to kick: {agent_id} : {kick_response.message}")

    async def _bot_leave(self):
        """Kick an agent."""
        logger.debug(f"Estoy en leave command")
        text = "Adiós a todos"
        await send_text_to_room(self.client, self.room.room_id, text)
        await self.client.room_leave(self.room.room_id)

    async def _show_help(self):
        """Show the help text."""
        if not self.args:
            text = ("Hello, I am a bot made with matrix-nio! Use `help commands` to view "
                    "available commands.")

            help = """
    !bot help [commands|rules]     - Help on commands
    !bot help                      - This menu
                   """

            text = f"`Help menu`:\n{help}"
            html = f"`<b>Help menu:</b><br /><pre><code>{help}</code></pre>`"

            await send_text_to_room(self.client, self.room.room_id, text)
            return

        topic = self.args[0]
        if topic == "rules":
            text = "There are no rules here!"
        elif topic == "commands":
            help = """
    !bot echo some_string     - Prints the string you entered
    !bot agent                - Invites an agent
    !bot leave                - bot leaves the room
                   """

            text = f"`We have a great comamnds for you`:\n{help}"
            # text = f"`Help menu`:\n{help}"
        else:
            text = f"We don't have help for **{topic}**!"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )
