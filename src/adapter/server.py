import selectors
import socket
import types


class WebServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 65432) -> None:
        self.selector = selectors.DefaultSelector()
        self.host = host
        self.port = port

    def run(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        s.setblocking(False)  # noqa: FBT003
        self.selector.register(s, selectors.EVENT_READ, data=None)
        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                else:
                    self.service_connection(key, mask)

    def accept_wrapper(self, sock: socket.socket) -> None:
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)  # noqa: FBT003
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)

    def service_connection(self, key, mask):
        s = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            if not (recv_data := s.recv(1024)):
                print(f"Closing connection to {data.addr}")
                self.selector.unregister(s)
                s.close()
            data.outb += recv_data
        if mask & selectors.EVENT_WRITE and data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = s.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
