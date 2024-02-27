import json
import os
import subprocess

try:
    from utils.config import XrayConfig
except Exception as e:
    print(e)
    from config import XrayConfig


def generate_xray_daemon():
    print()
    daemon_name = 'xray'
    file_name = daemon_name + '.service'
    run_cmd = f'/usr/bin/xray -c /etc/xray/config.json'

    service_path = '/etc/systemd/system/'
    daemon_text = "[Unit]\n" \
                  f"Description={daemon_name}\n" \
                  "After=network.target\n" \
                  "Wants=network.target\n\n" \
                  "[Service]\n" \
                  "User=root\n" \
                  "Group=root\n" \
                  "Type=simple\n" \
                  "PIDFile=/var/run/xray.pid\n" \
                  f"ExecStart={run_cmd}\n" \
                  "Restart=on-failure\n\n" \
                  "[Install]\n" \
                  "WantedBy=multi-user.target"
    print(f'-> {service_path + file_name}')

    # 需要root权限
    # 使用'w'模式打开文件，如果文件已存在，'w'模式将会覆盖掉旧的内容
    # with open(service_path + output_file, 'w', encoding='utf-8') as f:
    #     # 使用write方法将字符串写入文件
    #     f.write(daemon_text)

    # 使用echo和tee命令将文本写入文件 运行过程中需要手动输入密码
    # 多次执行会覆盖原来的文件
    subprocess.run(f'echo "{daemon_text}" | sudo tee {service_path + file_name}'
                   , shell=True, encoding='utf-8')

    print('*******************************************')


def download_xray(arch: str = 'arm64-v8a'):
    # arch : 64 arm64-v8a
    # https://github.com/XTLS/Xray-core/releases/download/v1.8.7/Xray-linux-arm64-v8a.zip
    file_name = f'Xray-linux-{arch}.zip'
    url = f'https://github.com/XTLS/Xray-core/releases/download/v1.8.7/{file_name}'

    os.system(f'wget {url}')
    os.system(f'unzip {file_name}')
    os.system(f'chmod +x xray')
    os.system(f'mv xray /usr/bin')


def generate_xray_config(domain: str, path: str, pem=None, key=None):
    c = XrayConfig(domain, path, pem, key)

    conf = {
            # 'h2': 8001,
            # 'grpc': 8002,
            # 'quic': 8003  quic 目前无法在多网卡下使用
            'tcp': 8005,
            'ws': 8080
        }
    config = c.generate_config(conf)

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

    os.system(f'mkdir /etc/xray')
    os.system(f'mv config.json /etc/xray')


if __name__ == '__main__':
    generate_xray_config('aws-hk.lensfa.com', 'compute.internal.ws')
