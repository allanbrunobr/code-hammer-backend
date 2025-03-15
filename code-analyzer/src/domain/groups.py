from enum import Enum

class UserGroup(str, Enum):
    owner = "Owner"
    admin = "Admin"
    editor = "Editor"
    user = "User"
