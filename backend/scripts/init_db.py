from app.db import Base, engine
from app import models 


def main() -> None:
    Base.metadata.create_all(engine)
    print("Tables created:", ", ".join(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()
