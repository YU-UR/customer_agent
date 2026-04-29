from app.utils.log_utils import logger_util


logger = logger_util.get_logger(__name__)

def commit_db_server(session):
    try:
        session.commit()
        logger.info("commit db success")
    except Exception as e:
        session.rollback()
        logger.error(f"commit db error: {e}")
    finally:
        session.close()