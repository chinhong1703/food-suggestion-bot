import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class DBHelperFood:
    def __init__(self):
        self.dbname = os.environ['DATABASE_URL']
        self.engine = create_engine(self.dbname)
        self.cursor = self.session()

    def session(self):
        return scoped_session(sessionmaker(bind=self.engine))

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner integer)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        try:
            self.cursor.execute(tblstmt)
            self.cursor.execute(itemidx)
            self.cursor.execute(ownidx)
            self.cursor.commit()
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()

    def add_item(self, item_text, owner):
        stmt = "INSERT INTO items (description, owner) VALUES (:description, :owner)"
        args = {"description": item_text, "owner": owner}
        try:
            self.cursor.execute(stmt, args)
            self.cursor.commit()
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM items WHERE description = :description AND owner = :owner"
        args = {"description": item_text, "owner": owner}
        try:
            self.cursor.execute(stmt, args)
            self.cursor.commit()
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()

    def get_items(self, owner):
        stmt = "SELECT description FROM items WHERE owner = :owner"
        args = {"owner": owner}
        try:
            results = self.cursor.execute(stmt, args)
            return [x for x in results]
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()



class DBHelperLog:
    def __init__(self):
        self.dbname = os.environ['DATABASE_URL']
        self.engine = create_engine(self.dbname)
        self.cursor = self.session()

    def session(self):
        return scoped_session(sessionmaker(bind=self.engine))

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS log (description text, owner integer, date timestamp)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON log (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON log (owner ASC)"
        try:
            self.cursor.execute(tblstmt)
            self.cursor.execute(itemidx)
            self.cursor.execute(ownidx)
            self.cursor.commit()
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()

    def add_item(self, item_text, owner, date):
        stmt = "INSERT INTO log (description, owner, date) VALUES (:description, :owner, :date)"
        args = {"description": item_text, "owner": owner, "date": date}
        try:
            self.cursor.execute(stmt, args)
            self.cursor.commit()
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM log WHERE description = :description AND owner = :owner"
        args = {"description": item_text, "owner": owner}
        try:
            self.cursor.execute(stmt, args)
            self.cursor.commit()
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()

    def get_items(self, owner):
        stmt = "SELECT * FROM log WHERE owner = :owner ORDER BY date DESC LIMIT 15"
        args = {"owner": owner}
        try:
            results = self.cursor.execute(stmt, args)
            return [x for x in results]
        except:
            self.cursor.rollback()
            raise
        finally:
            self.cursor.close()
