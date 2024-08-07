from sqlalchemy.orm import DeclarativeBase

class BMPTable(DeclarativeBase):
    def to_dict(self):
        dict = {}
        for col in self.__table__.columns:
            if hasattr(self, col.name):
                dict[col.name] = getattr(self,col.name)

        return dict   