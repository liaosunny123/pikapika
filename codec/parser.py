import pika
import yaml


class Parser(object):
    def __init__(self):
        with open("server.yaml", "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get_rabbitmq_conn_info(self) -> str:
        return self.config["rabbitmq"]["host"] + ":" + self.config["rabbitmq"]["port"]

    def get_rabbitmq_conn(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config["rabbitmq"]["host"],
                port=int(self.config["rabbitmq"]["port"]),
                credentials=pika.PlainCredentials(
                    self.config["rabbitmq"]["username"],
                    self.config["rabbitmq"]["password"],
                ),
            )
        )

    def get_module_type(self) -> str:
        return self.config["module"]["type"]

    def get_oss_access_key_id(self) -> str:
        return self.config["oss"]["access_key_id"]

    def get_oss_access_key_secret(self) -> str:
        return self.config["oss"]["access_key_secret"]

    def get_upload_prefix(self) -> str:
        return self.config["oss"]["upload_prefix"]
