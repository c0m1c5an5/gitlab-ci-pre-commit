class Error(Exception):
    pass


class ShellcheckNotFoundError(Error):
    def __init__(self, rc: int, err: str) -> None:
        message = f"Shellcheck not found [{rc}]: {err!r}"
        super().__init__(message)
