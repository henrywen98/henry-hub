# vpn-deploy

AI 一键部署自建 VPN：VLESS + XHTTP + TLS + Cloudflare CDN，在 VPS 上自动化搭建 3X-UI + Xray + Nginx + 伪装站。

## 用法

安装这个 plugin 后，对 Claude 说：

```
帮我部署一个 VPN
```

Claude 会逐步问你 9 个参数（服务器 IP、域名、Cloudflare 凭据等），SSH 进 VPS 跑完 15 步部署，最后输出可以直接导入 Shadowrocket / v2rayN / Clash 的 VLESS 链接。

也支持运维场景：

| 你说什么 | Claude 会做什么 |
|---|---|
| "VPN 连不上了" | 按 `troubleshooting.md` 诊断 + 修复 |
| "帮我加一个 VPN 用户" | 按 `maintenance.md` 添加客户端 |
| "证书要续期吗" | 检查证书状态，必要时强制续期 |

## 上游

skill 的 canonical source 在独立仓库：[henrywen98/claude-vpn-skill](https://github.com/henrywen98/claude-vpn-skill)

完整的安装教程、架构图、安全设计、FAQ 都在那里。
