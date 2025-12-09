# Pluto — 用户态“操作系统”演示

Pluto 是一个演示性项目，旨在以“冥王星”的主题呈现隐私保护与协作协调的设计理念。它不是一个真实的内核级操作系统，而是在用户态实现的一套服务与工具集合，展示隐私、服务管理、虚拟文件系统和协作协议等原型。

**主要特性**
- **隐私锁仓（PrivacyVault）**：使用 `cryptography.Fernet` 加密本地存储，演示重要数据的加密存放与检索。
- **虚拟文件系统（VFS）**：在用户态提供加密 blob 存储、列举/读写/删除接口。
- **服务管理器（Supervisor）**：注册、启动、监控与重启服务，捕获服务输出并提供日志尾部查看。
- **协作模块（Collab）**：基于 TCP 的点对点消息广播，支持可选 TLS 加密与 token 认证（演示级）。
- **交互式 Shell & TUI**：一个轻量 shell（`Pluto.os`）用于控制服务与 VFS，以及基于 `curses` 的 TUI（`Pluto.tui`）用于实时查看状态。
- **自动化演示**：`Pluto/full_demo.py` 会按步骤演示 Vault、VFS、Supervisor 与 Collab 的功能。

**项目结构（重要文件）**
- `Pluto/privacy.py` — Vault 实现。
- `Pluto/vfs.py` — 虚拟文件系统（基于 Vault 存储）。
- `Pluto/supervisor.py` — 服务管理器（捕获 stdout/stderr）。
- `Pluto/collab.py` — 协作服务器/客户端（支持 TLS + token 演示）。
- `Pluto/shell.py` / `Pluto/os.py` — 交互式 shell 和 OS 入口。
- `Pluto/tui.py` — 简单 curses TUI（实时状态查看）。
- `Pluto/full_demo.py` — 全功能自动演示脚本。
- `Pluto/services/worker.py` — 示例 worker 服务。
- `Pluto/requirements.txt` — 依赖（`cryptography` 等）。
- `vault/` — 运行时密钥与生成的自签名证书（演示用途）。

**快速开始**
1. 创建并激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Pluto/requirements.txt
```

2. 运行自动演示（推荐）：

```bash
python -m Pluto.full_demo
```

3. 交互式探索：
- 启动用户态 OS（启动 supervisor、注册示例服务并进入 shell）：

```bash
python -m Pluto.os
```

- 在 shell 中你可以运行：
  - `services`：列出注册的服务
  - `start <name>` / `stop <name>`：控制服务
  - `status`：查看服务状态与日志尾部
  - `ls` / `cat <path>` / `write <path> <content>` / `rm <path>`：操作 VFS
  - `exit`：退出

4. 启动并查看 TUI（需要终端支持 curses）：

```bash
python -m Pluto.tui
```

5. 手动测试协作（演示 TLS + token）：
- 服务器（演示模式下会自动生成自签名证书到 `vault/ssl`）：

```bash
python -c "from Pluto.collab import CollabServer; CollabServer(use_ssl=True, auth_token='secrettoken').start(); import time; time.sleep(600)"
```

- 客户端：

```bash
python -c "from Pluto.collab import CollabClient; c=CollabClient(use_ssl=True, token='secrettoken'); c.connect(); c.send('hello')"
```

**安全说明与限制**
- 此项目为演示用途：Vault、TLS 证书生成与协作认证均为示意实现。不要在生产环境中直接使用本项目作为安全组件。
- 如果用于更严格的场景，建议将 Vault 密钥迁移到受信任的 KMS/密钥库，并使用受信任 CA 签发的证书。

**开发与测试**
- 代码已包含基本示例与自动演示脚本。你可以基于 `Pluto/supervisor.py` 与 `Pluto/services/` 扩展更多服务。
- 推荐添加单元测试与 CI（例如 GitHub Actions）在合并或发布前验证行为。

**下一步建议**
- 为 Collab 添加严格的证书验证（使用 `cafile`），并改进认证流程。
- 为 Supervisor 提供 HTTP/Unix socket 管理 API，以便远程监控与日志查询。
- 为 VFS 添加访问控制与多用户隔离策略。

