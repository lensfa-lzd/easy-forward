package handler

import (
	"easy-forward/handler"
	"easy-forward/log"
	"net"
)

func ListenTCP(port string) (handler.Listener, error) {
	ln, err := net.Listen("tcp", ":"+port)
	if err != nil {
		return nil, err
	}
	log.Logger.Warningf("tcp listening on %s", port)
	return &TCPListener{ln: ln}, nil
}
