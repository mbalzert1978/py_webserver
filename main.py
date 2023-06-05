from src.adapter.server import WebServer


def main() -> None:
    s = WebServer()
    s.run()


if __name__ == "__main__":
    main()
