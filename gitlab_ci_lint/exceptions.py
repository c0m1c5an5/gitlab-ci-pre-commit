class Error(Exception):
    pass


class RemoteParseError(Error):
    def __init__(self, remote: str) -> None:
        message = f"Failed to parse remote '{remote}' as git url"
        super().__init__(message)
