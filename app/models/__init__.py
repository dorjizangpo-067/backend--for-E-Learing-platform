from .users import User
from .courses import Course
from .categories import Category

User.model_rebuild()
Course.model_rebuild()
Category.model_rebuild()