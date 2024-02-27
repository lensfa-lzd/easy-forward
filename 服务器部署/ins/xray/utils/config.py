import copy
from typing import Dict


class XrayConfig:
    def __init__(self, domain: str, path: str, pem, key):
        self.domain = domain
        self.path = path  # compute.internal.ws  不带路径

        if pem is None:
            pem = get_pem()
        if key is None:
            key = get_key()

        self.vless_inbounds = {
            "port": 996,
            "protocol": "vless",
            "settings": {
                "clients": [
                    {
                        "id": "dc872e42-6fea-4036-defd-063cd777766b"
                    }
                ],
                "decryption": "none",
                "fallbacks": []
            },
            "streamSettings": {},
            "tag": "inbound",
            "sniffing": {"enabled": False}
        }

        # 需要补全域名 和 证书
        self.tls_settings = {
            "serverName": f"{self.domain}",
            "rejectUnknownSni": False,
            "minVersion": "1.1",
            "maxVersion": "1.3",
            "cipherSuites": "",
            "certificates": [
                {
                    "ocspStapling": 3600,
                    "certificate": pem,
                    "key": key
                }
            ],
            "alpn": [
                "h2",
                "http/1.1",
                "h3"
            ],
            "settings": [
                {
                    "allowInsecure": True,
                    "fingerprint": "",
                    "serverName": f"{self.domain}"
                }
            ]
        }

        self.quic_stream = {
            "network": "quic",
            "security": "tls",
            "tlsSettings": {},
            "quicSettings": {
                "security": "none",
                "key": f"{self.path}",
                "header": {
                    "type": "none"
                }
            }
        }
        self.h2_stream = {
            "network": "h2",
            "security": "tls",
            "tlsSettings": {},
            "httpSettings": {
                "host": [
                    f"{self.domain}"
                ],
                "path": f"/{self.path}",
                "method": "PUT",
                "headers": {
                    "Header": [
                        "value"
                    ]
                }
            }
        }
        self.grpc_stream = {
            "network": "grpc",
            "security": "tls",
            "tlsSettings": {},
            "grpcSettings": {
                "serviceName": f"/{self.path}"
            }
        }
        self.ws_stream = {
            "network": "ws",
            "security": "none",
            "wsSettings": {
                "path": f"/{self.path}",
                "headers": {}
            }
        }
        self.tcp_stream = {
            "network": "tcp",
            "security": "none",
            "tcpSettings": {
                "acceptProxyProtocol": False,
                "header": {
                    "type": "none"
                }
            }
        }

        self.sample_conf = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [],  # 添加inbounds即可
            "outbounds": [
                {
                    "protocol": "freedom",
                    "tag": "direct"
                },
                {
                    "protocol": "blackhole",
                    "tag": "blocked"
                }
            ]
        }

        self.portal_map = {
            'h2': self.h2_stream,
            'grpc': self.grpc_stream,
            'quic': self.quic_stream,
            'tcp': self.tcp_stream,
            'ws': self.ws_stream
        }

    def generate_config(self, conf):
        """
        c = {
            'h2': 8001,
            'grpc': 8002,
            'quic': 8003,
            'tcp': 8005
            'ws': 8080
        }
        """
        config = self.sample_conf
        inbounds = []
        for portal in conf.keys():
            port: int = conf[portal]
            inbound_conf = self.vless_inbounds
            inbound_conf['port'] = port
            inbound_conf['tag'] = f'inbound-{str(port)}'

            streamSetting = self.portal_map[portal]

            if portal in ['h2', 'grpc', 'quic']:
                streamSetting['tlsSettings'] = self.tls_settings

            inbound_conf['streamSettings'] = streamSetting

            inbounds.append(copy.deepcopy(inbound_conf))

        config['inbounds'] = inbounds
        return config


def get_pem():
    pem = [
        "-----BEGIN CERTIFICATE-----",
        "MIIF+TCCBOGgAwIBAgIQCoXcx23fbb5da5BWWVKbsTANBgkqhkiG9w0BAQsFADBu",
        "MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3",
        "d3cuZGlnaWNlcnQuY29tMS0wKwYDVQQDEyRFbmNyeXB0aW9uIEV2ZXJ5d2hlcmUg",
        "RFYgVExTIENBIC0gRzIwHhcNMjMxMTIwMDAwMDAwWhcNMjQxMTE5MjM1OTU5WjAc",
        "MRowGAYDVQQDExFhd3MtaGsubGVuc2ZhLmNvbTCCASIwDQYJKoZIhvcNAQEBBQAD",
        "ggEPADCCAQoCggEBAIuszg4+NJj09BaKc18YqZdiEM0sy8LlwpMjBuku7Xw3u6rR",
        "fQefLPvKHH8oyDKaO17WmjPrxf6WdBdftZZrR+tzdsK2X4AkheFaFaUHH7Gux0BL",
        "+G1raTdtLIphzotiIhm0i0w/+9Z3NfjTCbfRzTci2ejfnJv19eMjZ03kcwz3WqJi",
        "6tF9Vc/tGstEMw5zKHPIGF2yXO8ZSAMMaAHg2nL0aDjgOtq/+qwELsG0f9O2QZ2Q",
        "fjbychc4hcvw8UTwNFlnwKqxpavqDrDvTSwM1rztUfuRPMH6NNTKCDlbjB4BlD3h",
        "XTO4QCTT+kyFjzJIFnkAVPNW/zgdlQDBTvg60Y0CAwEAAaOCAuMwggLfMB8GA1Ud",
        "IwQYMBaAFHjfkZBf7t6s9sV169VMVVPvJEq2MB0GA1UdDgQWBBRLtFmjfMU7n61j",
        "FBp9FYfaRDN2NzAcBgNVHREEFTATghFhd3MtaGsubGVuc2ZhLmNvbTA+BgNVHSAE",
        "NzA1MDMGBmeBDAECATApMCcGCCsGAQUFBwIBFhtodHRwOi8vd3d3LmRpZ2ljZXJ0",
        "LmNvbS9DUFMwDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggr",
        "BgEFBQcDAjCBgAYIKwYBBQUHAQEEdDByMCQGCCsGAQUFBzABhhhodHRwOi8vb2Nz",
        "cC5kaWdpY2VydC5jb20wSgYIKwYBBQUHMAKGPmh0dHA6Ly9jYWNlcnRzLmRpZ2lj",
        "ZXJ0LmNvbS9FbmNyeXB0aW9uRXZlcnl3aGVyZURWVExTQ0EtRzIuY3J0MAwGA1Ud",
        "EwEB/wQCMAAwggF9BgorBgEEAdZ5AgQCBIIBbQSCAWkBZwB3AHb/iD8KtvuVUcJh",
        "zPWHujS0pM27KdxoQgqf5mdMWjp0AAABi+29NxUAAAQDAEgwRgIhAPwDDSov/cnx",
        "qRIBZxVyiGcoZpu+eJHexe3mblTElxQtAiEA6yV6OA5UyEmjUCbwlP5+ss8XgdJb",
        "NqYuS4h0hXI9taMAdQBIsONr2qZHNA/lagL6nTDrHFIBy1bdLIHZu7+rOdiEcwAA",
        "AYvtvTa1AAAEAwBGMEQCIEoBjjU5EP2RWKDYpKMPjALlLRdub/dEBHPfPgsc3H4n",
        "AiAbwE3wp9eXmsnkagVK3q8a9fxZ7ZUaFk4tYZvKF7TXBwB1ANq2v2s/tbYin5vC",
        "u1xr6HCRcWy7UYSFNL2kPTBI1/urAAABi+29Np4AAAQDAEYwRAIgWQQfv06Esdpf",
        "DaujwRPFt5yhrMdKU6UxtOUQOfTXeHoCIG+Mb5hNWsl2gfsTRLIwiBakBP9/k6jN",
        "3PZ/vm85OLbpMA0GCSqGSIb3DQEBCwUAA4IBAQBXmAA6wlHQIoBKv1mg4O4oGXsL",
        "g29979GZhSkdbuFjbPpq0RBneIuZGWcJmw0QTAJDyGAUJDrDcT+zklQYmya3CxNv",
        "rZ+7YoQV81tHUkWdCFmGXBqIoZ3LgmW0CpVal3guYzC1yRBSbiv5v9swl+Ix8N+M",
        "owf5cdlU555DhfIvFuV74NAelknjVPq+kfN5RZlLX6fhmLMvaeUZVpTu6K5i288I",
        "qdJSx4C2SGj4Q7aWphJ+P93fZLkzK9J7Mj4Q8WIvJ7HJoF8Dcv8COyzIgL1NGcy8",
        "mM+N9BEat3eVjWNstB1yMLrBReyWIQZ0ObbSR9w2pr9uWWQbSfpv/K/RaNYo",
        "-----END CERTIFICATE-----",
        "-----BEGIN CERTIFICATE-----",
        "MIIEqjCCA5KgAwIBAgIQDeD/te5iy2EQn2CMnO1e0zANBgkqhkiG9w0BAQsFADBh",
        "MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3",
        "d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH",
        "MjAeFw0xNzExMjcxMjQ2NDBaFw0yNzExMjcxMjQ2NDBaMG4xCzAJBgNVBAYTAlVT",
        "MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j",
        "b20xLTArBgNVBAMTJEVuY3J5cHRpb24gRXZlcnl3aGVyZSBEViBUTFMgQ0EgLSBH",
        "MjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAO8Uf46i/nr7pkgTDqnE",
        "eSIfCFqvPnUq3aF1tMJ5hh9MnO6Lmt5UdHfBGwC9Si+XjK12cjZgxObsL6Rg1njv",
        "NhAMJ4JunN0JGGRJGSevbJsA3sc68nbPQzuKp5Jc8vpryp2mts38pSCXorPR+sch",
        "QisKA7OSQ1MjcFN0d7tbrceWFNbzgL2csJVQeogOBGSe/KZEIZw6gXLKeFe7mupn",
        "NYJROi2iC11+HuF79iAttMc32Cv6UOxixY/3ZV+LzpLnklFq98XORgwkIJL1HuvP",
        "ha8yvb+W6JislZJL+HLFtidoxmI7Qm3ZyIV66W533DsGFimFJkz3y0GeHWuSVMbI",
        "lfsCAwEAAaOCAU8wggFLMB0GA1UdDgQWBBR435GQX+7erPbFdevVTFVT7yRKtjAf",
        "BgNVHSMEGDAWgBROIlQgGJXm427mD/r6uRLtBhePOTAOBgNVHQ8BAf8EBAMCAYYw",
        "HQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMBIGA1UdEwEB/wQIMAYBAf8C",
        "AQAwNAYIKwYBBQUHAQEEKDAmMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdp",
        "Y2VydC5jb20wQgYDVR0fBDswOTA3oDWgM4YxaHR0cDovL2NybDMuZGlnaWNlcnQu",
        "Y29tL0RpZ2lDZXJ0R2xvYmFsUm9vdEcyLmNybDBMBgNVHSAERTBDMDcGCWCGSAGG",
        "/WwBAjAqMCgGCCsGAQUFBwIBFhxodHRwczovL3d3dy5kaWdpY2VydC5jb20vQ1BT",
        "MAgGBmeBDAECATANBgkqhkiG9w0BAQsFAAOCAQEAoBs1eCLKakLtVRPFRjBIJ9LJ",
        "L0s8ZWum8U8/1TMVkQMBn+CPb5xnCD0GSA6L/V0ZFrMNqBirrr5B241OesECvxIi",
        "98bZ90h9+q/X5eMyOD35f8YTaEMpdnQCnawIwiHx06/0BfiTj+b/XQih+mqt3ZXe",
        "xNCJqKexdiB2IWGSKcgahPacWkk/BAQFisKIFYEqHzV974S3FAz/8LIfD58xnsEN",
        "GfzyIDkH3JrwYZ8caPTf6ZX9M1GrISN8HnWTtdNCH2xEajRa/h9ZBXjUyFKQrGk2",
        "n2hcLrfZSbynEC/pSw/ET7H5nWwckjmAJ1l9fcnbqkU/pf6uMQmnfl0JQjJNSg==",
        "-----END CERTIFICATE-----",
        ""
    ]
    return pem


def get_key():
    key = [
        "-----BEGIN RSA PRIVATE KEY-----",
        "MIIEowIBAAKCAQEAi6zODj40mPT0FopzXxipl2IQzSzLwuXCkyMG6S7tfDe7qtF9",
        "B58s+8ocfyjIMpo7XtaaM+vF/pZ0F1+1lmtH63N2wrZfgCSF4VoVpQcfsa7HQEv4",
        "bWtpN20simHOi2IiGbSLTD/71nc1+NMJt9HNNyLZ6N+cm/X14yNnTeRzDPdaomLq",
        "0X1Vz+0ay0QzDnMoc8gYXbJc7xlIAwxoAeDacvRoOOA62r/6rAQuwbR/07ZBnZB+",
        "NvJyFziFy/DxRPA0WWfAqrGlq+oOsO9NLAzWvO1R+5E8wfo01MoIOVuMHgGUPeFd",
        "M7hAJNP6TIWPMkgWeQBU81b/OB2VAMFO+DrRjQIDAQABAoIBACJGBYwOLJbp6KlN",
        "UPEhWqAYgrnuB5PsEDpNqoj2qHTGMklAvXbs0rt4RVTYm4N7QB1N+KnL7ZpCrfr8",
        "U9E0wwGeJCK0YKvPioCZO91yaY8OrbrzyWKELF3a7saIKIggTPDU0iekPbZLK1XC",
        "50wRcdNZPHJ9yG6mxK73RYaiC68++EfmyoW3c0hi/DHQHuDpDU5V3qDCd2PcZ4Zp",
        "v5N8JEbTeoqTlJVBAwqu+8KiJPKzTi6GSbK6D87MUpg1hjVUXjisTM67k392o0yX",
        "BF2HCG/BGRGGhHR732GKDrG1ExUuFZ43muGBysGgQivRXLPC7fLIW+5XouXMRRMc",
        "fWPkGEsCgYEAwyw8/BcWY2pXcuJgrYwLPrx0Ak3ANgMWiv5FHo9WYO6l+G2Q3j/b",
        "cJv7+7hzG1ZPZbsNZaM5o5JCyquzgYiZpYFx+PibgddLk9J+RJfgHlCmAQp02n28",
        "3mwMFi/lT3h9ptdFkNEddYdbH94POaWWLDgQnuEg3gnAxG1/XINrJS8CgYEAtzS0",
        "UgnELQ16I4X2r1Hm7znSKiBC4/AY4Bta5zVGBOlKus2f0DoMa2A1DUI7Ekl8dnfX",
        "BmGpJmDKQApXdQ4Qia9qDVciuF6J0iwtMBS0ovvLhIJaiiCjwxCp4kfubZPFY54p",
        "e6ysL8f3po754TpmapCO0T3UBH0B3TNop2aIPgMCgYEAq4n5O9QK8Gvp2maPdFlP",
        "FN/L0q6FjrNeH+Hl3Ds9P0rhgxzBpCVZ+HqQmah/Ovq8I/yohLlWkqadn8YTqnjm",
        "GipQgvP2scMJgS4TnrQh3mMh1G5dUCANXSx33xRPpm6PeZFhaivxiXfjJnokxZT9",
        "DXZlXU8fdSf7Tmmy9Bvpky8CgYA8LYS5mdmljtK6zmssRXPcyppdGgG+y4PwQSwH",
        "3DjmrhbM63P+OsMPlid29nVe2WKXq1+nCfc80vg8NulpWrhV8ZedUCzocK1Gqxog",
        "u/xluN2t5f+FdZk1Hskeuc/4kFx7D13C8QISI9YWEMrFj6BKirdOxcdZvhIZraRH",
        "sGc6LwKBgFGrHhPvsYbRaJ3R9MwOeFXVtKQQQJ8sC8D1YvKfvLZrVw+LLOoWKrjo",
        "GjPY+57SDEKjtkJn90MuueXhVglUW/f/2BokfUO1Qdb4IPkV+BywzRSwdcRD3GV1",
        "b6E2u5t6x0sOOEQLpPepQ8OeU1LjcXoIqzrlbuRJJN9rlS9XBGj6",
        "-----END RSA PRIVATE KEY-----",
        ""
    ]
    return key
