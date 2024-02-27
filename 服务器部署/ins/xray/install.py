import os
from utils.scripts import generate_xray_daemon, download_xray, generate_xray_config


# 使用系统的xray是为了让xray的udp代理可以正常运行


def main():
    print()
    daemon_name = 'xray'
    file_name = daemon_name + '.service'

    print('下载xray')
    download_xray()

    print('生成配置文件')
    generate_xray_config('aws-hk.lensfa.com', 'compute.internal.ws')

    print('添加守护进程/应用服务')
    generate_xray_daemon()

    print()
    print('重载守护进程 -> systemctl daemon-reload')
    os.system('sudo systemctl daemon-reload')

    print()
    print('设置为自启动')
    print(f'  开启 -> sudo systemctl start {file_name}')
    print(f'  自启动 -> sudo systemctl enable {file_name}')
    os.system(f'sudo systemctl start {file_name}')
    os.system(f'sudo systemctl enable {file_name}')

    print()
    print('运行结束')


if __name__ == '__main__':
    main()
