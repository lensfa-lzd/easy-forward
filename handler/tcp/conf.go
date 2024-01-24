package handler

import (
	"easy-forward/handler"
	"easy-forward/log"
	"net"
)

type TCPListener struct {
	ln net.Listener
}

func (t *TCPListener) Accept() (handler.Conn, error) {
	conn, err := t.ln.Accept()
	if err != nil {
		return nil, err
	}
	//log.Logger.Debugf("accept tcp conection")
	return conn, nil
}

func (t *TCPListener) Close() error {
	log.Logger.Warningf("closing tcp listener")
	return t.ln.Close()
}
