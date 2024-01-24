package handler

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"easy-forward/handler"
	"easy-forward/log"
	"encoding/pem"
	"github.com/quic-go/quic-go"
	"math/big"
)

func ListenQUIC(port string) (handler.Listener, error) {
	ln, err := quic.ListenAddr(":"+port, generateTLSConfig(), &quic.Config{Allow0RTT: true})
	if err != nil {
		return nil, err
	}
	log.Logger.Warningf("quic listening on %s", port)
	return &QUICListener{ln: ln}, nil
}

// 生成TLS配置，QUIC需要TLS > 1.2
func generateTLSConfig() *tls.Config {
	// 尝试小一点的私钥位数
	key, err := rsa.GenerateKey(rand.Reader, 1024)
	if err != nil {
		panic(err)
	}
	template := x509.Certificate{SerialNumber: big.NewInt(1)}
	certDER, err := x509.CreateCertificate(rand.Reader, &template, &template, &key.PublicKey, key)
	if err != nil {
		panic(err)
	}
	keyPEM := pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)})
	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})

	tlsCert, err := tls.X509KeyPair(certPEM, keyPEM)
	if err != nil {
		panic(err)
	}

	// 设置TLS版本为TLS 1.3
	return &tls.Config{
		Certificates: []tls.Certificate{tlsCert},
		MinVersion:   tls.VersionTLS13, // 最小版本设为TLS 1.3
		MaxVersion:   tls.VersionTLS13, // 最大版本也设为TLS 1.3
	}
}
