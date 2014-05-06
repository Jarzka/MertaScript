from threading import Thread

class NetworkManagerThread(Thread):
    # @param method string "host" or "join"
    def init(self, program, method):
        self._program = program
        self._method = method
    def run(self):
        if self._method == "host":
            self._program.get_network_manager().start_host(self._program.HOST_PORT)
        elif self._method == "join":
            self._program.get_network_manager().start_join(self._program.JOIN_IP, self._program.HOST_PORT)