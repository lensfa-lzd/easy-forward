package webSocket

import (
	"io"
	"net"
	"time"
)

type Core struct {
}

func (c *Core) OpenStream() (Stream, error) {
	s := new(TCPStream)
	return s, nil
}

type Stream interface {
	io.Reader
	io.Writer
	io.Closer
	SetDeadline(t time.Time) error
}

// TCPStream 实现了Stream接口
type TCPStream struct {
	conn net.Conn
}

func (s *TCPStream) Read(p []byte) (n int, err error) {
	return s.conn.Read(p)
}

func (s *TCPStream) Write(p []byte) (n int, err error) {
	return s.conn.Write(p)
}

func (s *TCPStream) Close() error {
	return s.conn.Close()
}

func (s *TCPStream) SetDeadline(t time.Time) error {
	return s.conn.SetDeadline(t)
}
