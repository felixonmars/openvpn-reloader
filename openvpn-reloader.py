#!/usr/bin/env python
from __future__ import unicode_literals, print_function
import struct
import sys
import socket
from sh import kill
from time import sleep
from argparse import ArgumentParser


class PacketLossException(Exception):
    pass


def monitor(destination, max_loss_rate=0.5, timeout=.5, interval=.2, n=30):
    loss = [0] * n
    seq = 1

    while True:
        header = struct.pack(b'bbHHh', 8, 0, 0, 0, seq)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
        s.settimeout(timeout)
        s.sendto(header, (destination, 0))

        try:
            packet, peer = s.recvfrom(1024)
        except socket.timeout:
            sys.stdout.write("?")
            loss[0] = 1
        else:
            sys.stdout.write(".")

        sys.stdout.flush()

        if sum(loss) > max_loss_rate * n:
            raise PacketLossException

        sleep(interval)

        loss = [0] + loss[:-1]
        seq += 1

        if seq > 65535:
            seq = 0


def main():
    arg_parser = ArgumentParser(description="OpenVPN Auto Reloader")

    arg_parser.add_argument(
        'PID',
        help="OpenVPN PID to send SIGUSR1")

    arg_parser.add_argument(
        '-d', '--destination',
        default="8.8.8.8",
        help="Target to ping. Default: 8.8.8.8")

    arg_parser.add_argument(
        '-m', '--max-loss-rate',
        type=int,
        default=50,
        help="Max bearable packet loss rate. Default: 50 (50 percent)")

    arg_parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=.5,
        help="Timeout for each ping packet. Default: 1 (second)")

    arg_parser.add_argument(
        '-i', '--interval',
        type=float,
        default=.2,
        help="Interval between packets. Default: .2 (second)")

    arg_parser.add_argument(
        '-n',
        type=int,
        default=30,
        help="Number of packets to determine packet loss. Default: 30")

    options = arg_parser.parse_args()

    while True:
        try:
            monitor(options.destination, options.max_loss_rate / 100.0, options.timeout, options.interval, options.n)
        except PacketLossException:
            print("Reloading", options.PID)
            kill("-USR1", options.PID)
            sleep(5)

if __name__ == "__main__":
    main()
