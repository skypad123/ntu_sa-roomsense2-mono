
class InternalServerError(Exception):
    pass

class DatabaseInterfaceError(Exception):
    pass

class ItemNotFoundError(Exception):
    pass

class UpdateFailError(Exception):
    pass

class UploadFailError(Exception):
    pass