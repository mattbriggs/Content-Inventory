import datetime

class Logger:
    def __init__(self, verbose=True):
        self.verbose = verbose

    def _log(self, level, message):
        if self.verbose:
            ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{ts}] [{level}] {message}")

    def info(self, msg): self._log("INFO", msg)
    def success(self, msg): self._log("SUCCESS", msg)
    def warn(self, msg): self._log("WARN", msg)
    def error(self, msg): self._log("ERROR", msg)
