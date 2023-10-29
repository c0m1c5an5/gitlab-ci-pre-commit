class Error(Exception):
    pass


class CommandError(Error):
    def __init__(self, err: str) -> None:
        message = err
        super().__init__(message)


class YqVersionError(CommandError):
    def __init__(self) -> None:
        message = "Yq version is not compatible"
        super().__init__(message)


class MalformedError(Error):
    def __init__(self) -> None:
        message = "Source and destination are not equivalent"
        super().__init__(message)
