class Error(Exception):
    pass


class FormatError(Error):
    pass


class YqNotFoundError(Error):
    pass


class YqVersionError(Error):
    pass
