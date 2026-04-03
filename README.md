# CDISC Library MCP Server

MCP Server for CDISC Library API - 提供对临床数据标准的完整访问。

## 安装

```bash
pip install cdisc-library-mcp
```

## 配置

```json
{
  "mcpServers": {
    "cdisc-library": {
      "command": "python",
      "args": ["-m", "cdisc_mcp"],
      "env": {
        "CDISC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 许可证

MIT License