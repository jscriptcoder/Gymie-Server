import argparse
from gymie.server import start

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--host', default='0.0.0.0')
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()

    start(args.host, args.port)
