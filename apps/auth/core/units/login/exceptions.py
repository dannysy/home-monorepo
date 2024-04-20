from house.basic.exceptions import BadRequestException


class OldLoginError(BadRequestException):
    """This App_Id already exist."""
    pass


class WrongLoginRequest(BadRequestException):
    """This App_Id already exist."""
    pass

class LoginSpentError(BadRequestException):
    """Логин уже отработан"""
    pass