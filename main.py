from loguru import logger

import callback
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

    logger.info("Pikapika is started, running now.")
    logger.info(f"Listening rabbitmq server:{mq.get_rabbitmq_conn_info()}")
    logger.info(f"Pikapika is now used as module: {mq.get_module_type()}")

    conn = mq.get_rabbitmq_conn()
    channel = conn.channel()
    logger.info("Pikapika is now checked conn.")
    channel.queue_declare(queue=mq.get_module_type(), durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(mq.get_module_type(), fn_map[mq.get_module_type()], True)
    logger.info("Pikapika is now running consuming task...")
    while True:
        try:
            channel.start_consuming()
        except Exception as e:
            logger.warning(f"MQ Error as:{e}")
