from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def bulk_save_to_db(model, data_list):
    """
    使用 SQLAlchemy 批量插入数据
    :param model: 数据模型类（例如 ProductData）
    :param data_list: 数据字典列表
    """
    db = SessionLocal()
    try:
        db.bulk_insert_mappings(model, data_list)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


