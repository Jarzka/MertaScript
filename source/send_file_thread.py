from threading import Thread

class SendFileThread(Thread):
    # @param method string "host" or "join"
    def init(self, path_file, client):
        self._path_file = path_file
        self._client = client
    def run(self):
        file = open (self._path_file, "rb")
        read_bytes = file.read(1024)
        while (read_bytes):
            read_bytes = file.read(1024)
        self._client.get_socket().sendall("<FILE|".encode() + read_bytes + ">".encode())