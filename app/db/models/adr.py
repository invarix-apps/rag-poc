from app.db.base import Base
from app.db.models.mixins import DocumentMixin


class Adr(Base, DocumentMixin):
    __tablename__ = "adrs"
