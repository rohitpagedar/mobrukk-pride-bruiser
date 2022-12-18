import psycopg2


# Global variables
CREATE_TABLE_QUERIES = dict()
CREATE_TABLE_QUERIES[
    "users"
] = """CREATE TABLE users (
userid VARCHAR(255) PRIMARY KEY,
name VARCHAR(255),
email VARCHAR(255),
photos INT,
metadata VARCHAR(255)
)
"""
CREATE_TABLE_QUERIES[
    "images"
] = """CREATE TABLE images (
imageid VARCHAR(255) PRIMARY KEY,
userid VARCHAR(255),
metadata VARCHAR(255),
processed BOOLEAN DEFAULT FALSE
)
"""

LIST_TABLE_CONTENTS_QUERY = 'SELECT * FROM "{fname}"'
USER_TABLE_KEY_QUERY = "SELECT * FROM users WHERE userid='{fuser}'"
USER_TABLE_INSERT_QUERY = (
    "INSERT INTO users (userid, name, email, photos, metadata) VALUES (%s,%s,%s,%s,%s)"
)
USER_TABLE_DELETE_QUERY = "DELETE FROM users WHERE userid=%s"
USER_LOCK_ROW_QUERY = "SELECT * FROM users WHERE userid = '{fuser}' FOR UPDATE"
USER_UPDATE_PHOTOS_QUERY_KEY = (
    "UPDATE users SET photos = {fphotos} WHERE userid = '{fuser}'"
)

IMAGE_TABLE_KEY_QUERY = "SELECT * FROM images WHERE imageid='{fimage}'"
IMAGE_TABLE_INSERT_QUERY = (
    "INSERT INTO images (imageid, userid, metadata, processed) VALUES (%s,%s,%s,%s)"
)
IMAGE_TABLE_DELETE_QUERY = "DELETE FROM images WHERE imageid=%s"
IMAGE_LOCK_ROW_QUERY = "SELECT * FROM images WHERE imageid = '{fimage}' FOR UPDATE"
IMAGE_UPDATE_PROCESSED_QUERY_KEY = (
    "UPDATE images SET processed = {fvalue} WHERE imageid = '{fimage}'"
)


class UserDetails:
    def __init__(self, userid: str, name: str, email: str, photos: int, metadata: str):
        self.userid = userid
        self.name = name
        self.email = email
        self.photos = photos
        self.metadata = metadata

    def __json__(self):
        return {
            "userid": self.userid,
            "name": self.name,
            "email": self.email,
            "photos": self.photos,
            "metadata": self.metadata,
        }

    @classmethod
    def __from_json__(cls, json_data):
        return cls(
            json_data["userid"],
            json_data["name"],
            json_data["email"],
            json_data["photos"],
            json_data["metadata"],
        )

    def __str__(self):
        return f"userid = {self.userid}, name = {self.name}, email = {self.email}, photos = {self.photos}, metadata = {self.metadata}"


class ImageDetails:
    def __init__(self, imageid: str, userid: str, metadata: str, processed: bool):
        self.imageid = imageid
        self.userid = userid
        self.metadata = metadata
        self.processed = processed

    def __json__(self):
        return {
            "imageid": self.imageid,
            "userid": self.userid,
            "processed": self.processed,
            "metadata": self.metadata,
        }

    @classmethod
    def __from_json__(cls, json_data):
        return cls(
            json_data["imageid"],
            json_data["userid"],
            json_data["processed"],
            json_data["metadata"],
        )

    def __str__(self):
        return f"imageid = {self.imageid}, userid = {self.userid}, processed = {self.processed}, metadata = {self.metadata}"


# Returns a ImageDetails object when passed in a tuple
def get_image_object(result: tuple) -> ImageDetails:
    if result is None:
        return None
    image_object = ImageDetails(*result)
    return image_object


# Returns a UserDetails object when passed in a tuple
def get_user_object(result: tuple) -> UserDetails:
    if result is None:
        return None
    user_object = UserDetails(*result)
    return user_object


class Gandalf:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        # Set the connection details for the PostgreSQL database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.db_conn = None
        self.tables = None

    def connect(self) -> None:
        try:
            self.db_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.populate_table_dict()
        except psycopg2.Error as error:
            print(f"Caught error while connecting to DB : {error}")

    # is db connected, if not, make a best effort attempt to re-establish connection
    def ensure_db_is_connected(self) -> None:
        if self.db_conn.status != psycopg2.extensions.STATUS_READY:
            self.connect()

    def populate_table_dict(self) -> None:
        if self.tables is None or len(self.tables) == 0:
            # empty list
            self.tables = list()

        # populate table list
        with self.db_conn.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            # Fetch the results of the query
            results = cursor.fetchall()
            for result in results:
                if result[0] not in self.tables:
                    print(f"Warming up the tables cache with table : {result[0]}")
                    self.tables.append(result[0])
            self.db_conn.commit()

    def create_table(self, table_name: str) -> None:
        self.ensure_db_is_connected()
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(CREATE_TABLE_QUERIES[table_name])
                self.db_conn.commit()
            self.tables.append(table_name)
            return
        except Exception as e:
            print(f"Caught exception while listing table contents {e}")
            raise e

    def list_table_contents(self, table_name: str) -> None:
        if table_name not in self.tables:
            return None
        self.ensure_db_is_connected()
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(LIST_TABLE_CONTENTS_QUERY.format(fname=table_name))
                table_contents = list()
                results = cursor.fetchall()
                for result in results:
                    if table_name == "users":
                        table_contents.append(get_user_object(result))
                    else:
                        table_contents.append(get_image_object(result))
                print(f"Contents of table {table_name} are :")
                print(
                    f"********************************************************************************************"
                )
                for row in table_contents:
                    print(f"{row}")
                print(
                    f"********************************************************************************************"
                )
                self.db_conn.commit()
        except Exception as e:
            print(f"Exception while listing table contents {e}")
            return None

    def get_user_details(self, userid: str) -> UserDetails:
        self.ensure_db_is_connected()
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(USER_TABLE_KEY_QUERY.format(fuser=userid))
                result = cursor.fetchone()
                user_object = get_user_object(result)
                self.db_conn.commit()
                return user_object
        except Exception as e:
            print(f"Caught exception while getting user details : {e}")
            return None

    def get_image_details(self, imageid: str) -> ImageDetails:
        self.ensure_db_is_connected()
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute(IMAGE_TABLE_KEY_QUERY.format(fimage=imageid))
                result = cursor.fetchone()
                image_object = get_image_object(result)
                self.db_conn.commit()
                return image_object
        except Exception as e:
            print(f"Caught exception while getting user details : {e}")
            return None

    def add_user(
        self,
        userid: str,
        name: str,
        email: str,
        photos: int = None,
        metadata: str = None,
    ) -> int:
        self.ensure_db_is_connected()
        try:
            if self.tables is not None and ("users" not in self.tables):
                self.create_table("users")
            with self.db_conn.cursor() as cursor:
                result = self.get_user_details(userid)
                if result is None:
                    cursor.execute(
                        USER_TABLE_INSERT_QUERY, (userid, name, email, photos, metadata)
                    )
                    print(
                        f"Added user in the system with the following details :::: id - {userid}, name - {name}, email - {email}"
                    )
                self.db_conn.commit()
            return 1
        except Exception as e:
            print(f"Caught exception while adding user : {e}")
            return -1

    def delete_user(self, user: str) -> int:
        self.ensure_db_is_connected()
        try:
            if self.tables is not None and ("users" not in self.tables):
                self.create_table("users")
            with self.db_conn.cursor() as cursor:
                result = self.get_user_details(user)
                if result is not None:
                    cursor.execute(USER_TABLE_DELETE_QUERY, (user,))
                self.db_conn.commit()
            return 1
        except Exception as e:
            print(f"Caught exception while deleting user : {e}")
            return -1

    def add_image(
        self, imageid: str, userid: str, metadata: str = None, processed: bool = False
    ) -> int:
        self.ensure_db_is_connected()
        try:
            if self.tables is not None and ("images" not in self.tables):
                self.create_table("images")
            with self.db_conn.cursor() as cursor:
                result = self.get_image_details(imageid)
                if result is None:
                    cursor.execute(
                        IMAGE_TABLE_INSERT_QUERY, (imageid, userid, metadata, processed)
                    )
                    print(
                        f"Added image in the system with : imageid - {imageid} for user - {userid}"
                    )
                self.db_conn.commit()
            return 1
        except Exception as e:
            print(f"Caught exception while adding image : {e}")
            return -1

    def delete_image(self, imageid: str) -> int:
        self.ensure_db_is_connected()
        try:
            if self.tables is not None and ("images" not in self.tables):
                self.create_table("images")
            with self.db_conn.cursor() as cursor:
                result = self.get_image_details(imageid)
                if result is not None:
                    cursor.execute(IMAGE_TABLE_DELETE_QUERY, (imageid,))
                self.db_conn.commit()
            return 1
        except Exception as e:
            print(f"Caught exception while deleting image : {e}")
            return -1

    def update_user_photos(self, userid: str, increment: bool) -> int:
        self.ensure_db_is_connected()
        try:
            with self.db_conn.cursor() as cursor:
                # Lock row first
                cursor.execute(USER_LOCK_ROW_QUERY.format(fuser=userid), (1,))
                result = cursor.fetchone()
                user_details = get_user_object(result)
                photos = user_details.photos
                if increment:
                    photos = photos + 1
                else:
                    photos = photos - 1
                cursor.execute(
                    USER_UPDATE_PHOTOS_QUERY_KEY.format(fuser=userid, fphotos=photos),
                    (100, 1),
                )
                self.db_conn.commit()
            return 1
        except Exception as e:
            print(f"Caught exception while updating user photos : {e}")
            return -1

    def update_image_processed(self, imageid: str, is_processed: bool = True) -> int:
        self.ensure_db_is_connected()
        try:
            with self.db_conn.cursor() as cursor:
                # Lock row first
                cursor.execute(IMAGE_LOCK_ROW_QUERY.format(fimage=imageid), (1,))
                result = cursor.fetchone()
                image_details = get_image_object(result)
                print(
                    f"Toggling image process value for imageid {image_details.imageid} from {image_details.processed} to {is_processed}"
                )
                cursor.execute(
                    IMAGE_UPDATE_PROCESSED_QUERY_KEY.format(
                        fimage=imageid, fvalue=is_processed
                    ),
                    (100, 1),
                )
                self.db_conn.commit()
            return 1
        except Exception as e:
            print(f"Caught exception while updating image processed flag : {e}")
            return -1

    def close(self) -> None:
        self.db_conn.close()
