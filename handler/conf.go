package handler

import (
	"io"
	"net"
)

type Conn interface {
	io.Reader
	io.Writer
	io.Closer
	RemoteAddr() net.Addr
}

type Listener interface {
	Accept() (Conn, error)
	Close() error
}
