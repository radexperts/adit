import asyncio
import signal
import subprocess
import sys
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from threading import Event
from types import FrameType

from django.conf import settings
from django.core.management.base import BaseCommand
from watchfiles import PythonFilter, watch

from ...utils.debounce import debounce


class ServerCommand(BaseCommand, ABC):
    """See Django's runserver.py command.

    https://github.com/django/django/blob/master/django/core/management/commands/runserver.py
    """

    help = "Starts a custom server"
    server_name = "custom server"

    _popen: subprocess.Popen | None = None
    _stop = Event()

    def add_arguments(self, parser):
        parser.add_argument(
            "--autoreload",
            action="store_true",
            help="Autoreload server on code change.",
        )

    def handle(self, *args, **options):
        # SIGINT is sent by CTRL-C
        def on_interrupt(signum: int, frame: FrameType | None) -> None:
            self.on_shutdown()
            self.shutdown()
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.raise_signal(signal.SIGINT)

        signal.signal(signal.SIGINT, on_interrupt)

        # SIGTERM is sent when stopping a Docker container
        def on_terminate(signum: int, frame: FrameType | None) -> None:
            self.on_shutdown()
            self.shutdown()
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.raise_signal(signal.SIGTERM)

        signal.signal(signal.SIGTERM, on_terminate)

        self.run(**options)

    def run(self, **options):
        if options["autoreload"]:
            self.stdout.write(f"Autoreload enabled for {self.server_name}.")

            # We debounce to give the Django webserver time to restart first
            @debounce(wait_time=2)
            def inner_run():
                if self._popen is not None:
                    self._popen.terminate()
                    self._popen.wait()

                args = sys.argv.copy()
                args.remove("--autoreload")
                self._popen = subprocess.Popen(args, close_fds=False)

            inner_run()

            try:
                for changes in watch(
                    settings.BASE_DIR / "adit", watch_filter=PythonFilter(), stop_event=self._stop
                ):
                    self.stdout.write("Changes detected. Restarting server...")
                    inner_run()
            except KeyboardInterrupt:
                # watch itself tries to catch signals and may raise a KeyboardInterrupt, but we
                # handle all signals ourselves
                pass

            if self._popen:
                self._popen.wait()
        else:
            self.stdout.write("Performing system checks...")
            self.check(display_num_errors=True)

            self.stdout.write(datetime.now().strftime("%B %d, %Y - %X"))
            self.stdout.write(f"Starting {self.server_name}")
            self.stdout.write("Quit with CONTROL-C.")

            # We run run_server in a different thread to avoid blocking the main thread
            # especially when handling SIGINT and SIGTERM signals.
            t = threading.Thread(target=self.run_server, kwargs=options)
            t.start()
            t.join()

    def shutdown(self):
        if self._popen:
            self._popen.terminate()

        self._stop.set()

    @abstractmethod
    def run_server(self, **options) -> None:
        """
        The abstract method that should be implemented by subclasses to do the work.

        Args:
            **options: Additional keyword arguments parsed from the command line.
        """
        raise NotImplementedError

    @abstractmethod
    def on_shutdown(self) -> None:
        """
        A callback method that is called when the server should shutdown.

        Called when CTRL-C is pressed, the Docker container is stopped or when
        an autoreload is triggered. It should be used to clean up any resources
        and force the server to shut down.
        """
        raise NotImplementedError


class AsyncServerCommand(ServerCommand, ABC):
    def run_server(self, **options):
        loop = asyncio.get_event_loop()

        # Shutdown in asyncio loop must be handled by a different signal handler
        loop.add_signal_handler(signal.SIGINT, lambda: self.on_shutdown())
        loop.add_signal_handler(signal.SIGTERM, lambda: self.on_shutdown())

        loop.run_until_complete(self.run_server_async())

    @abstractmethod
    async def run_server_async(self, **options):
        raise NotImplementedError
