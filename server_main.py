#!/usr/bin/python3

import asyncio
import logging
import signal
import argparse

import mlat.clientio
import mlat.coordinator


def stop_event_loop(msg, loop):
    logging.info(msg)
    loop.stop()


def main(tcp_port, udp_port, motd, bind_address):
    loop = asyncio.get_event_loop()

    coordinator = mlat.coordinator.Coordinator()
    server = loop.run_until_complete(mlat.clientio.start_client_listener(tcp_port=tcp_port,
                                                                         udp_port=udp_port,
                                                                         coordinator=coordinator,
                                                                         motd=motd,
                                                                         bind_address=bind_address))

    loop.add_signal_handler(signal.SIGINT, stop_event_loop, "Halting on SIGINT", loop)
    loop.add_signal_handler(signal.SIGTERM, stop_event_loop, "Halting on SIGTERM", loop)

    try:
        loop.run_forever()  # Well, until stop() is called anyway!

    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        style='{',
                        format='{asctime}.{msecs:03.0f}  {levelname:8s} {name:20s} {message}',
                        datefmt='%Y%m%d %H:%M:%S')

    parser = argparse.ArgumentParser(description="Multilateration server.")
    parser.add_argument('--motd',
                        type=str,
                        help="Server MOTD",
                        default="In-development v2 server. Expect odd behaviour.")
    parser.add_argument('--bind-address',
                        help="Host to bind to when accepting connections.",
                        default="0.0.0.0")
    parser.add_argument('--tcp-port',
                        help="Port to accept TCP control connections on.",
                        type=int,
                        required=True)
    parser.add_argument('--udp-port',
                        help="Port to accept UDP datagram traffic on.",
                        type=int)

    args = parser.parse_args()

    main(tcp_port=args.tcp_port,
         udp_port=args.udp_port,
         bind_address=args.bind_address,
         motd=args.motd)
