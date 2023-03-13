from mongoengine import connect, disconnect, disconnect_all, get_connection
from src.utils.Utils import Logger
from src.utils import config


logger = Logger(__name__).get_connector_logger()


class Connector:
    def __init__(
            self,
            name=None,
            port=None,
            host=None,
            alias=None
    ):
        # Define data base attributes.
        self.name = name or config.name
        self.port = port or config.port
        self.host = host or config.host
        self.alias = alias or config.alias

        # Flag attribute to determine whether there is connection with the database.
        self.online = False

        # Define logger.
        self.logger = logger
        self.logger.info("Connector is initiated!")

    def connect(self):
        if not self.online:
            connect(
                db=self.name,
                host=self.host,
                port=self.port,
                alias=self.alias
            )
            self.set_online(True)
            self.logger.info(
                f"Connected: "
                f"db={self.name}, "
                f"host={self.host},"
                f"port={self.port}, "
                f"alias={self.alias}"
            )
        return self

    def disconnect(self):
        if self.online:
            disconnect(self.alias)
            self.set_online(False)
            self.logger.info(
                f"Disconnected: "
                f"db={self.name}, "
                f"host={self.host},"
                f"port={self.port}, "
                f"alias={self.alias}"
            )
        return self

    def update_connection(self, **kwargs):
        change_flag = False
        for key, value in kwargs.items():
            try:
                temp_value = getattr(self, key)
            except KeyError:
                self.logger.error(
                    f"The variable key for updating database connection does not found: {key}"
                )
                continue
            if value == temp_value:
                continue
            else:
                setattr(self, key, value)
                self.logger.info(
                    f"Connection will be updated; {key}: {temp_value} ---> {value}"
                )
                change_flag = True

        if change_flag:
            self.connect()
        return self

    def disconnect_all(self):
        disconnect_all()
        self.set_online(False)
        self.logger.info(
            "All connections disconnected."
        )
        return self

    def set_online(self, online: bool = True):
        self.online = online
        return self


# Construct a Connector object to be able to use in further functions
# without defining same object multiple times.
main_conn = Connector()


if __name__ == "__main__":
    pass

