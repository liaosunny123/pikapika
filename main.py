import time

from loguru import logger
import callback
import sys
from callback import lora
from callback import pic_gen
from callback import tagger
from codec import parser

fn_map = {
    "lora": callback.lora.callback,
    "pic-gen": callback.pic_gen.callback,
    "tagger": callback.tagger.callback,
}

if __name__ == "__main__":
    logger.info("Pikapika is starting...")
    logger.info("Pikapika version: v1.0.0-alpha")
    logger.info("Pikapika author: EpicMo")
    mq = parser.Parser()
    module_type = mq.get_module_type()
    if len(sys.argv) == 2:
        logger.info(f"Use manual module type: {sys.argv[1]}")
        module_type = sys.argv[1]
    logger.info("Pikapika is started, running now.")
    logger.info(f"Listening rabbitmq server:{mq.get_rabbitmq_conn_info()}")
    logger.info(f"Pikapika is now used as module: {module_type}")

    while True:
        try:
            conn = mq.get_rabbitmq_conn()
            channel = conn.channel()
            logger.info("Pikapika is now checked conn.")
            channel.queue_declare(queue=module_type, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                module_type, fn_map[module_type], True
            )
            logger.info("Pikapika is now running consuming task...")
            channel.start_consuming()
        except Exception as e:
            logger.warning(f"MQ Error as:{e}")
            logger.warning("Restart after 3s..")
            time.sleep(3)
