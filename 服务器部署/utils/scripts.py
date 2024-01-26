import json
import os
import subprocess


def generate_daemon():
    print()
    daemon_name = 'ef'
    file_name = daemon_name + '.service'
    run_cmd = f'/usr/bin/ef -c /etc/ef/config.yaml'

    service_path = '/etc/systemd/system/'
    daemon_text = "[Unit]\n" \
                  f"Description={daemon_name}\n" \
                  "After=network.target\n" \
                  "Wants=network.target\n\n" \
                  "[Service]\n" \
                  "User=root\n" \
                  "Group=root\n" \
                  "Type=simple\n" \
                  "PIDFile=/var/run/ef.pid\n" \
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


def download(version: str = 'v0.0.1', arch: str = 'arm64'):
    # https://github.com/lensfa-lzd/easy-forward/releases/download/v0.0.1/ef-arm64
    file_name = f'ef-{arch}'
    url = f'https://github.com/lensfa-lzd/easy-forward/releases/download/{version}/ef-{arch}'

    os.system(f'wget {url}')
    os.system(f'mv {file_name} ef')
    os.system(f'chmod +x ef')
    os.system(f'mv ef /usr/bin')


def generate_config():
    os.system(f'mkdir /etc/ef')
    os.system(f'mv config.yaml /etc/ef')


if __name__ == '__main__':
    print()
