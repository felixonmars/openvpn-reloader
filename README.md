openvpn-reloader
================

Reload your openvpn process when packet loss suddenly arise.

# Usage
    usage: openvpn-reloader.py [-h] [-d DESTINATION] [-m MAX_LOSS_RATE]
                               [-t TIMEOUT] [-i INTERVAL] [-n N]
                               PID

    OpenVPN Auto Reloader

    positional arguments:
      PID                   OpenVPN PID to send SIGUSR1

    optional arguments:
      -h, --help            show this help message and exit
      -d DESTINATION, --destination DESTINATION
                            Target to ping. Default: 8.8.8.8
      -m MAX_LOSS_RATE, --max-loss-rate MAX_LOSS_RATE
                            Max bearable packet loss rate. Default: 50 (50
                            percent)
      -t TIMEOUT, --timeout TIMEOUT
                            Timeout for each ping packet. Default: 1 (second)
      -i INTERVAL, --interval INTERVAL
                            Interval between packets. Default: .2 (second)
      -n N                  Number of packets to determine packet loss. Default:
                            30
