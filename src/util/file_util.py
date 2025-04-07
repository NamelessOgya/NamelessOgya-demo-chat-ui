# python -m src.util.file_util

import yaml



def read_yaml(file_dir):
    with open(file_dir, 'r', encoding='utf-8') as f:
        data_dic = yaml.safe_load(f)

    return data_dic


if __name__ == "__main__":
    data = read_yaml('./src/agent/senario/senario.yaml')

    print(data)
