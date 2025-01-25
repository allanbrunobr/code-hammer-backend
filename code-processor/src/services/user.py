from typing import Optional
from sqlalchemy.orm import Session

from ..adapters.dtos import UserPreferDTO
from ..domain import User


class UserService:

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def verify_user_is_active(db: Session, email: str) -> bool:
        return True

    @staticmethod
    def get_user_prefer(user: User) -> UserPreferDTO:
        prompt = '''
                  You are a expert code analyst, you shou analyze this code and comment and refactor the parts of code with bugs, vulnerabilities and code smells.
                  You should comment if the code follows the fundamentals of OWASP and SOLID.|
                
                  {code}
                   
                  You should format in markdown translated to {language}
                  '''
        user_prefer = UserPreferDTO(
            language='Portuguese/BR',
            prompt=prompt
        )

        user.prompt = user.prompt.format(code=process_request.code)
        user.prompt = user.prompt.format(language=user.language)
        return user_prefer

    @staticmethod
    def verify_user_is_active() -> bool:
        return True
