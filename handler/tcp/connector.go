package handler

import (
	"easy-forward/handler"
	"fmt"
	"net"
)

func CreateTCPConn(address string) (handler.Conn, error) {
	// 使用net.Dial发起TCP连接
	conn, err := net.Dial("tcp", address)
	if err != nil {
		return nil, fmt.Errorf("connect to tcp server error: %v", err)
	}
	return conn, nil
}
