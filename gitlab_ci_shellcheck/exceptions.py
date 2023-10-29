class Error(Exception):
    pass


class CommandError(Error):
    def __init__(self, err: str) -> None:
        message = err
        super().__init__(message)


class ShellcheckNotFoundError(CommandError):
    pass
