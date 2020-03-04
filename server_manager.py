from server import Server
import config


"""
Точка входа программы
"""

server = Server(config.VK_API_TOKEN, config.VK_GROUP_ID, "server-finance")
server.start()
