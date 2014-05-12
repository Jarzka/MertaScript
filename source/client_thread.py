from threading import Thread
import decode_message_thread


class ClientThread(Thread):
    def init(self, client, network_manager):
        self._client = client
        self._network_manager = network_manager

    def run(self):
        # In python 3, bytes strings and unicode strings are now two different types. Since sockets are not
        # aware of string encodings, they are using raw bytes strings, that have a slightly different interface from
        # unicode strings. So, now, whenever you have a unicode string that you need to use as a byte string,
        # you need to encode() it. And when you have a byte string, you need to decode it to use it as a regular
        # (python 2.x) string. Unicode strings are quotes enclosed strings. Bytes strings are b"" enclosed strings
        self._client.get_socket().sendall("<CON_MSG|Welcome to the server.>".encode())

        while True:
            try:
                data = self._client.get_socket().recv(self._network_manager.get_buffer_size())
                # print("Got message from client id {}: {}".format(self._client.get_id(), data))
                decode_message = decode_message_thread.DecodeMessageThread()
                decode_message.init(data, self._client, self._network_manager)
                decode_message.run()
            except:
                print("Client {} disconnected".format(self._client.get_id()))
                break

        self._client.disconnect() # Set client status disconnected