def get_model_name(style: int) -> str:
    enum = {
        1: "chilloutmix",  # 写实风格
    }
    return enum[style]
