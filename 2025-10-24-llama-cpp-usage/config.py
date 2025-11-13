import os

ENV_LIST = ["MODEL_ENDPOINT"]

def set_environment_variables(**kwargs):
    # MODEL_ENDPOINT = https: // www.modelscope.cn /
    os.environ.update(kwargs)


def get_environment_variable(var_name, default_value=None):
    return os.environ.get(var_name, default_value)


def list_environment_variables():
    for key, value in os.environ.items():
        if key in ENV_LIST:
            print(f"{key} = {value}")


if __name__ == "__main__":
    # 设置环境变量
    set_environment_variables(MODEL_ENDPOINT="https://www.modelscope.cn/")
    # 获取特定环境变量
    MODEL_ENDPOINT = get_environment_variable('MODEL_ENDPOINT')
    print(f"MODEL_ENDPOINT: {MODEL_ENDPOINT}")
