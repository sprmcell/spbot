import discord
class Reference:
    class NoneReference(Exception):
        def __init__(self, description: str = None) -> None:
            super().__init__(description or "Please reply to a message for this command to work")
    def __init__(self, client) -> None:
        self.client = client
    async def __call__(self, message: discord.Message) -> discord.Message:
        self.message = message
        self.referance = message.reference
        if self.reference is None:
            raise self.NoneReferance()
        return await self.get_reference()

    async def get_reference(self) -> discord.Message:
        self.channel = self.client.get_channel(self.reference.channel_id)
        message: discord.Message = await self.channel.fetch_message(self.reference.message_id)
        return message

    async def __aenter__(self) -> discord.Message:
        self.channel = self.client.get_channel(self.reference.channel_id)
        return await self.channel.fetch_message(self.reference.message_id)

    async def __aexit__(self, *args) -> None:
        return False
