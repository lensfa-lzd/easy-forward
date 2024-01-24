package log

import (
	"fmt"
	"github.com/sirupsen/logrus"
	"os"
)

// MyFormatter 自定义格式器
type MyFormatter struct{}

// Format 实现 logrus.Formatter 接口的 Format 方法
func (f *MyFormatter) Format(entry *logrus.Entry) ([]byte, error) {
	// 自定义日志格式
	return []byte(fmt.Sprintf("[%s] %s: %s\n", entry.Level, entry.Time.Format("2006-01-02 15:04:05"), entry.Message)), nil
}

var Logger = logrus.New()

func SetLogger(level string, file string) {
	// 设置为自定义格式器
	Logger.SetFormatter(&MyFormatter{})
	if file != "" {
		logFile, err := os.OpenFile(file, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
		if err == nil {
			Logger.Out = logFile
		} else {
			Logger.Info("Failed to log to file, using default stderr")
		}
		defer func(file *os.File) {
			err = file.Close()
			if err != nil {
				fmt.Printf("Close log file err: %v", err)
			}
		}(logFile)
	}

	switch level {
	case "debug":
		Logger.SetLevel(logrus.DebugLevel)
	case "info":
		Logger.SetLevel(logrus.InfoLevel)
	case "warn":
		Logger.SetLevel(logrus.WarnLevel)
	case "error":
		Logger.SetLevel(logrus.ErrorLevel)
	}
}
