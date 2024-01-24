package handler

import (
	"context"
	"easy-forward/handler"
	"easy-forward/log"
	"fmt"
	"github.com/quic-go/quic-go"
	"net"
)

type QUICListener struct {
	ln *quic.Listener
}

func (q *QUICListener) Accept() (handler.Conn, error) {
	var ctx = context.Background()
	conn, err := q.ln.Accept(ctx)
	if err != nil {
		return nil, err
	}
	//log.Logger.Debugf("accept quic coonection")

	// 完全不使用多路复用 每个连接仅处理一个stream
	onlyStream, err := conn.AcceptStream(ctx)
	if err != nil {
		return nil, err
	}
	//log.Logger.Debugf("accept quic stream")

	return &QUICConn{quicConnect: conn, quicStream: onlyStream}, nil
}

func (q *QUICListener) Close() error {
	log.Logger.Warningf("closing quic listener")
	return q.ln.Close()
}

type QUICConn struct {
	quicConnect quic.Connection
	quicStream  quic.Stream
}

func (q *QUICConn) Close() error {
	streamErr := q.quicStream.Close()
	//log.Logger.Debugf("closing quic stream")
	ConnectErr := q.quicConnect.CloseWithError(0, "closing session")
	//log.Logger.Debugf("closing quic connection")
	if streamErr != nil || ConnectErr != nil {
		return fmt.Errorf("quic conn close error: streamErr %v, ConnectErr %v", streamErr, ConnectErr)
	}
	return nil
}

func (q *QUICConn) Read(p []byte) (n int, err error) {
	return q.quicStream.Read(p)
}

func (q *QUICConn) Write(p []byte) (n int, err error) {
	return q.quicStream.Write(p)
}

func (q *QUICConn) RemoteAddr() net.Addr {
	return q.quicConnect.RemoteAddr()
}
