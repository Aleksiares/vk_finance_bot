import config
from server import Server


server = Server(config.VK_API_TOKEN, config.VK_GROUP_ID, "finance-server")
server.start()
