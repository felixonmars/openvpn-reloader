#!/usr/bin/env python
from __future__ import print_function
from collections import deque
import struct
import sys
import socket
from os import kill, sysconf
import signal
from time import sleep
from argparse import ArgumentParser

shrt_max, shrt_min = sysconf('SC_SHRT_MAX'), sysconf('SC_SHRT_MIN')


class PacketLossException(Exception):
    pass


def monitor(destination, max_loss_rate=0.5, timeout=.5, interval=.2, n=30):
    loss = deque(maxlen=n)
    seq = shrt_min

    while True:
        header = struct.pack(b'bbHHh', 8, 0, 0, 0, seq)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
        s.settimeout(timeout)
        s.sendto(header, (destination, 0))

        try:
            packet, peer = s.recvfrom(1024)
        except socket.timeout:
            sys.stdout.write("?")
            loss.append(1)
        else:
            sys.stdout.write(".")
            loss.append(0)

        sys.stdout.flush()

        if sum(loss) > max_loss_rate * n:
            raise PacketLossException

        sleep(interval)
        seq += 1

        if seq > shrt_max:
            seq = shrt_min


def main():
    arg_parser = ArgumentParser(description="OpenVPN Auto Reloader")

    arg_parser.add_argument(
        'PID',
        type=int,
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
            kill(options.PID, signal.SIGUSR1)
            sleep(5)

if __name__ == "__main__":
    main()
