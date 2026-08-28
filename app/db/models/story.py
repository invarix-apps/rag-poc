from app.db.base import Base
from app.db.models.mixins import DocumentMixin


class Story(Base, DocumentMixin):
    __tablename__ = "stories"
