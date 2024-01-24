package startup

import (
	"context"
	"easy-forward/handler"
	quic "easy-forward/handler/quic"
	tcp "easy-forward/handler/tcp"
)

func startClient(ctx context.Context, config yamlConfig) {
	stopChan := make(chan struct{}, len(config.Rules))
	defer close(stopChan)

	for k, v := range config.Rules {
		listenPort := k
		serverAddress := v

		var conf = handler.Handler{
			Port:         listenPort,
			Address:      serverAddress,
			ListenerFunc: tcp.ListenTCP,
			ConnFunc:     quic.CreateQuicConn,
		}

		go conf.Run(ctx, stopChan)
	}
	for i := 0; i < len(config.Rules); i++ {
		// 等待结束
		<-stopChan
	}
}

func startServer(ctx context.Context, config yamlConfig) {
	stopChan := make(chan struct{}, len(config.Rules))
	defer close(stopChan)

	for k, v := range config.Rules {
		listenPort := k
		serverAddress := v

		var conf = handler.Handler{
			Port:         listenPort,
			Address:      serverAddress,
			ListenerFunc: quic.ListenQUIC,
			ConnFunc:     tcp.CreateTCPConn,
		}

		go conf.Run(ctx, stopChan)
	}

	for i := 0; i < len(config.Rules); i++ {
		// 等待结束
		<-stopChan
	}
}
