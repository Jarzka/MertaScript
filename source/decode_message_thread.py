from threading import Thread

class DecodeMessageThread(Thread):
    # @param method string "host" or "join"
    def init(self, data, sender, network_manager):
        self._data = data
        self._sender = sender
        self._network_manager = network_manager
    def run(self):
        self._network_manager.decode_message(self._data, self._sender)