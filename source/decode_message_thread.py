from threading import Thread

class DecodeMessageThread(Thread):
    def init(self, data, sender, network_manager):
        self._data = data
        self._sender = sender
        self._network_manager = network_manager
    def run(self):
        self._network_manager.decode_message(self._data, self._sender)