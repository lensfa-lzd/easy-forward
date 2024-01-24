package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"
	"log"
	"net"
	"os"
	"os/signal"
	"strings"
)

var packetChan chan *Packet

type UDP struct {
	SrcIP   net.IP
	DstIP   net.IP
	SrcPort int
	DstPort int
	Content []byte
}

func (u *UDP) Send() error {
	laddr := &net.UDPAddr{IP: u.SrcIP, Port: u.SrcPort}
	raddr := &net.UDPAddr{IP: u.DstIP, Port: u.DstPort}

	if conn, err := net.DialUDP("udp", laddr, raddr); err != nil {
		return err
	} else {
		defer conn.Close()
		if _, err := conn.Write(u.Content); err != nil {
			return err
		} else {
			return nil
		}
	}
}

type Packet struct {
	Ethernet layers.Ethernet
	IP4      layers.IPv4
	TCP      layers.TCP
	UDP      layers.UDP
	Payload  gopacket.Payload

	Decoded []gopacket.LayerType
}

// NewPacket 解析报文
func NewPacket(packetData []byte) (*Packet, error) {
	var p Packet
	parser := gopacket.NewDecodingLayerParser(layers.LayerTypeEthernet, &p.Ethernet, &p.IP4, &p.TCP, &p.UDP, &p.Payload)
	if err := parser.DecodeLayers(packetData, &p.Decoded); err != nil {
		return nil, err
	} else {
		return &p, nil
	}
}

// String 显示报文信息
// 用于打印。
func (p *Packet) String() string {
	var info []string
	for _, layerType := range p.Decoded {
		switch layerType {
		case layers.LayerTypeEthernet:
			info = append(info,
				p.Ethernet.SrcMAC.String()+" > "+p.Ethernet.DstMAC.String(),
				"Ethernet Type: "+p.Ethernet.EthernetType.String(),
			)
		case layers.LayerTypeIPv4:
			info = append(info,
				p.IP4.SrcIP.String()+" > "+p.IP4.DstIP.String(),
				"Protocol: "+p.IP4.Protocol.String(),
			)
		case layers.LayerTypeTCP:
			info = append(info,
				p.TCP.SrcPort.String()+" > "+p.TCP.DstPort.String(),
			)
		case layers.LayerTypeUDP:
			info = append(info,
				p.UDP.SrcPort.String()+" > "+p.UDP.DstPort.String(),
			)
		case gopacket.LayerTypePayload:
			info = append(info,
				"Content: "+string(p.Payload.LayerContents()),
			)
		}
	}
	return strings.Join(info, " | ")
}

// findDevByIp 通过设备 IP 查找设备
// 在 Linux 中，设备名很容易获取，如 “eth0”； 但在 Windows 中则较难, 因而有此函数。
func findDevByIp(ip net.IP) (*pcap.Interface, error) {
	devices, err := pcap.FindAllDevs()
	if err != nil {
		return nil, err
	}
	for _, device := range devices {
		for _, address := range device.Addresses {
			if address.IP.Equal(ip) {
				return &device, nil
			}
		}
	}
	return nil, errors.New("find device failed by ip")
}

// capture 捕获报文，解析并放入 chan
func capture(dev *pcap.Interface, filter string) {
	if h, err := pcap.OpenLive(dev.Name, 4096, true, -1); err != nil {
		log.Panicln(err)
	} else if err := h.SetBPFFilter(filter); err != nil {
		log.Panicln(err)
	} else {
		defer h.Close()
		for {
			if packetData, _, err := h.ReadPacketData(); err != nil {
				log.Panicln(err)
			} else if p, err := NewPacket(packetData); err != nil {
				log.Panicln(err)
			} else {
				fmt.Println(p.String())
				packetChan <- p
			}
		}
	}
}

// redirect 转发报文
// 指定源 IP 和目的 IP，端口不变。
func redirect(ctx context.Context, srcIP, dstIP net.IP) {
	for {
		select {
		case <-ctx.Done():
			return
		case p := <-packetChan:
			u := UDP{
				SrcIP:   srcIP,
				DstIP:   dstIP,
				SrcPort: int(p.UDP.SrcPort),
				DstPort: int(p.UDP.DstPort),
				Content: p.Payload.LayerContents(),
			}
			if err := u.Send(); err != nil {
				log.Printf("send p failed: %+v", u)
			}
		}
	}
}

func Run(ctx context.Context, devIp, filter, srcIp, dstIp string) {
	dev, err := findDevByIp(net.ParseIP(devIp))
	if err != nil {
		log.Panicf("find device by ip failed: ip=%s, err=%s", devIp, err)
	}

	packetChan = make(chan *Packet, 64)
	go capture(dev, filter) // filter -> 端口
	redirect(ctx, net.ParseIP(srcIp), net.ParseIP(dstIp))
}

func main_() {
	var (
		devIP  = flag.String("d", "192.168.0.204", "Device IP.")
		filter = flag.String("f", "port 14001", "BPF filter expression.")
		srcIP  = flag.String("src-ip", "10.0.1.3", "Redirect src IP.")
		dstIP  = flag.String("dst-ip", "10.0.1.2", "Redirect dst IP.")
	)
	flag.Parse()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	Run(ctx, *devIP, *filter, *srcIP, *dstIP)
}
