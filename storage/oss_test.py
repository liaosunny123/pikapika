from storage import oss


def oss_download_test():
    img_list = oss.download_target_files(
        "LTAI5tPqsGHt74fEsNfpZfoR",
        "h3kABq8RbWfC189bi4EJHolttFFkqF",
        "https://oss-rg-china-mainland.aliyuncs.com",
        "dzy-test-model-bucket",
        ['pic/16972863391068804e1d63cfe6ee2c8a98f90bdc0865f.jpg'],
    )
    print(img_list)
