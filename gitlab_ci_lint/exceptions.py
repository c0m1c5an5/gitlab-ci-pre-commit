class Error(Exception):
    pass


class CommandError(Error):
    def __init__(self, err: str) -> None:
        message = err
        super().__init__(message)


class PassNotFoundError(CommandError):
    pass


class InvalidGitUrlError(Error):
    def __init__(self, remote: str) -> None:
        message = f"'{remote}' is not a valid git url"
        super().__init__(message)
