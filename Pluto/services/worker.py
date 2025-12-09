"""
Example worker service for Pluto Supervisor.
It prints a heartbeat every few seconds.
"""
import time
import argparse


def main(name='worker'):
    try:
        while True:
            print(f"[{name}] heartbeat")
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"[{name}] stopping")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--name', default='worker')
    args = p.parse_args()
    main(args.name)
