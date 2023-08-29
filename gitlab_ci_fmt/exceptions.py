class Error(Exception):
    pass


class CommandError(Error):
    def __init__(self, rc: int, err: str) -> None:
        message = f"Subprocess failed [{rc}]: {err!r}"
        super().__init__(message)


class MalformedError(Error):
    def __init__(self) -> None:
        message = "Formatting produced malformed result"
        super().__init__(message)


class YqVersionError(Error):
    def __init__(self) -> None:
        message = "Yq version is not compatible"
        super().__init__(message)
