def get_model_name(style: int) -> str:
    map = {
        1: "chilloutmix",  # 写实风格
    }
    return map[style]
