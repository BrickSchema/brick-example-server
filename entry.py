#!/usr/bin/env python

import pdb
import argparse

from brick_server import create_app


def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--configfile',
                           help='Location of the config file',
                           type=str,
                           default='configs/configs.json',
                           )
    argparser.add_argument('--port',
                           type=int,
                           default=7889,
                           )
    argparser.add_argument('--host',
                           type=str,
                           default='0.0.0.0',
                           )
    return argparser.parse_args()

def main():
    args = get_args()
    app = create_app(configfile=args.configfile)
    app.run(args.host, port=args.port)

if __name__ == '__main__':
    main()
