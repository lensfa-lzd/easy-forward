package main

import (
	"easy-forward/startup"
	"flag"
)

func main() {
	var configFile = flag.String("c", "client.yaml", "config file")
	flag.Parse()

	startup.SetConfig(*configFile)
}
