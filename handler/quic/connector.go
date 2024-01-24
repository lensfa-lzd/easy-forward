package handler

import (
	"context"
	"crypto/tls"
	"easy-forward/handler"
	"fmt"
	"time"

	"github.com/quic-go/quic-go"
)

func CreateQuicConn(address string) (handler.Conn, error) {
	// "localhost:4242"
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	session, err := quic.DialAddrEarly(ctx, address, &tls.Config{InsecureSkipVerify: true}, nil)
	if err != nil {
		return nil, fmt.Errorf("connect to quic server error: %v", err)
	}

	stream, err := session.OpenStreamSync(context.Background())
	if err != nil {
		return nil, fmt.Errorf("create stream in quic connect error: %v", err)
	}

	return &QUICConn{quicConnect: session, quicStream: stream}, nil
}
