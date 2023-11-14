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

    def get_lora_scripts_ws_addr(self) -> str:
        return self.config["child_service"]["lora"]

    def get_lora_train_num(self) -> str:
        return self.config["lora"]["train_num"]

    def get_loss_decided_num(self) -> float:
        return float(self.config["lora"]["loss_decide"])

    def get_sd_service_addr(self) -> str:
        return str(self.config["child_service"]["sd"])

    def get_sd_preview_default_prompt(self) -> str:
        return str(self.config["sd"]["preview_prompt"])

    def get_sd_generate_steps(self) -> str:
        return str(self.config["sd"]["preview_steps"])

    def get_seg_pics_access_key_id(self) -> str:
        return str(self.config["seg"]["access_key_id"])

    def get_seg_pics_access_key_secret(self) -> str:
        return str(self.config["seg"]["access_key_secret"])

    def get_seg_pics_endpoint(self) -> str:
        return str(self.config["seg"]["endpoint"])

    def get_seg_pics_region_id(self) -> str:
        return str(self.config["seg"]["region_id"])
