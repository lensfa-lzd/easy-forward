package handler

import (
	"context"
	"easy-forward/log"
	"io"
)

type Handler struct {
	Port         string
	Address      string
	ListenerFunc func(port string) (Listener, error)
	ConnFunc     func(address string) (Conn, error)
}

func (h *Handler) Run(ctx context.Context, stop chan struct{}) {
	//ln, err := net.Listen("tcp", "0.0.0.0:"+port)
	ln, err := h.ListenerFunc(h.Port)
	if err != nil {
		log.Logger.Fatal(err)
	}
	defer func(listener Listener) {
		err = listener.Close()
		if err != nil {
			log.Logger.Errorf("close listener failed: %v", err)
		}
	}(ln)

	connChan := make(chan Conn, 64)
	defer close(connChan)

	go func(listener Listener) {
		for {
			conn, err := listener.Accept()
			if err != nil {
				log.Logger.Error("listen client failed")
				continue
			}
			log.Logger.Infof("New connection from %s", conn.RemoteAddr().String())
			connChan <- conn
		}
	}(ln)

	for {
		select {
		case <-ctx.Done():
			stop <- struct{}{}
			return
		case conn := <-connChan:
			go h.forward(conn)
		}
	}
}

func (h *Handler) forward(conn Conn) {
	serverConn, err := h.ConnFunc(h.Address) // 连接服务器
	if err != nil {
		log.Logger.Errorf(err.Error())
		return
	}

	closeChain := make(chan struct{}, 1)
	defer func() {
		<-closeChain
		close(closeChain)
	}()

	_closeConn := func(Conn Conn) {
		err = Conn.Close()
		if err != nil {
			log.Logger.Errorf("close connection failed: %v", err)
		}
	}
	defer _closeConn(serverConn)
	defer _closeConn(conn)

	// Start proxying
	go h.proxy(serverConn, conn, closeChain)
	go h.proxy(conn, serverConn, closeChain)

	// 只要有一个交换关闭 就关闭另一个
	<-closeChain
}

func (h *Handler) proxy(dst Conn, src Conn, close chan struct{}) {
	// defer log.Logger.Debugf("proxy done")

	_, _ = io.Copy(dst, src)
	//if err != nil {
	//	log.Logger.Errorf(err.Error())
	//}
	close <- struct{}{}
}
