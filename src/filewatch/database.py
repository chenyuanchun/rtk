import datetime
from pathlib import Path

from sqlalchemy import create_engine, Column, Date, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class FilePathRegistry(Base):
    __tablename__ = 'file_path_registry'

    business_date = Column(Date, primary_key=True)
    file_path = Column(String, primary_key=True)
    status = Column(String)

def create_tables(engine):
    Base.metadata.create_all(engine)

def init_db(file_path: str):
    engine = create_engine(f'sqlite:///{file_path}')
    Session = sessionmaker(bind=engine)
    return Session()

def add_file_path(session, business_date: datetime.date, file_path: str, status: str = 'waiting'):
    new_record = FilePathRegistry(business_date=business_date, file_path=file_path, status=status)
    session.add(new_record)
    session.commit()

def get_all_file_paths(session):
    """
    Query the file_path_registry table and return all records.
    
    Args:
        session: SQLAlchemy session object
    
    Returns:
        List of FilePathRegistry objects
    """
    return session.query(FilePathRegistry).all()

def main():
    user_home = str(Path.home())
    session = init_db(f'{user_home}/workspace/rtk/files.db')
    all_files = get_all_file_paths(session)
    for file_record in all_files:
        print(f"Business Date: {file_record.business_date}, File Path: {file_record.file_path}, Status: {file_record.status}")
    
    # Example usage
    # today = datetime.date.today()
    # example_file_path = f"{user_home}/workspace/test2.txt"
    
    # add_file_path(session, today, example_file_path)
    
    # print("File path added successfully.")
    
    session.close()

if __name__ == "__main__":
    main()
