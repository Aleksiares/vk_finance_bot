import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint

import commander


class Server:
    """
    Класс Long Poll сервера, позволяющего слушать сообщения группы ВКонтакте
    """

    def __init__(self, api_token, group_id, server_name: str = 'empty'):
        self.server_name = server_name
        self.group_id = group_id

        self.vk = vk_api.VkApi(token=api_token)
        self.long_poll = VkBotLongPoll(self.vk, group_id, wait=30)
        self.vk_api = self.vk.get_api()

    def send_message(self, peer_id: int, message: str) -> None:
        return self.vk_api.messages.send(peer_id=peer_id,
                                         message=message,
                                         random_id=randint(0, 2048))

    def start(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.object.from_id
                peer_id = event.object.peer_id
                command: str = event.object.text.lower().strip()

                if command.startswith("/"):
                    if not commander.is_user_present(user_id):
                        answer_message = commander.add_user(user_id)
                        self.send_message(peer_id=peer_id,
                                          message=answer_message)

                    self.send_message(peer_id=peer_id,
                                      message=commander.processing_command(command=command,
                                                                           user_id=user_id))
