package startup

import (
	"context"
	"easy-forward/log"
	"fmt"
	"gopkg.in/yaml.v3"
	"os"
	"os/signal"
)

type yamlConfig struct {
	// 属性必须大写开头
	LogLevel string            `yaml:"logLevel"`
	LogFile  string            `yaml:"logFile"`
	Rules    map[string]string `yaml:"rules"`
	Mode     string            `yaml:"mode"`
}

func SetConfig(configFile string) {
	fmt.Print("Setting config...\n")

	// 读取YAML文件内容
	data, err := os.ReadFile(configFile)
	if err != nil {
		panic(fmt.Errorf("read config error: %v", err))
	}

	// 解析YAML文件内容到结构体
	var config yamlConfig
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		panic(fmt.Errorf("unmarshal config error: %v", err))
	}

	log.SetLogger(config.LogLevel, config.LogFile)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	if config.Mode == "client" {
		startClient(ctx, config)
	} else {
		startServer(ctx, config)
	}
}
