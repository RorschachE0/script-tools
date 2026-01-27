# capFilter - 高性能交互式数据包清洗工具

**PcapFilter** 是一个基于 Python 和 `Tshark` (Wireshark CLI) 构建的高效网络流量取证与清洗工具。它旨在解决处理大体积 PCAP 文件时手动过滤繁琐、解析速度慢以及复杂协议（如 MongoDB）可能导致解析器崩溃的问题。

该工具通过交互式命令行界面 (CLI)，实现了对 `.pcap/.cap/.pcapng` 文件的秒级 IP 提取、精准过滤和安全导出。

## 🚀 核心特性

### 1. ⚡ 极速 IP 提取 (Performance Optimized)
- 摒弃了传统的逐包遍历模式，采用 Tshark 的 **统计模式 (`-z endpoints`)**。
- **性能提升**: 在处理 GB 级文件时，IP 提取速度比普通 Python 循环快 **10-50 倍**。

### 2. 🛡️ 复杂协议防崩溃机制 (Crash Proof)
- **MongoDB/嵌套协议修复**: 针对深度嵌套的数据包（如复杂的 MongoDB 查询），自动注入 `-o "gui.max_tree_items:10000000"` 参数。
- 解决了 Wireshark 解析器因 "Dissector bug / infinite loop" 导致的崩溃或数据截断问题，确保数据完整性。

### 3. 🧠 智能直通模式 (Smart Bypass)
- 当用户未设置过滤条件时，自动切换为 **系统级文件复制**。
- 避免了不必要的解码/重编码过程，实现零延迟导出。

### 4. 🎯 精准多维过滤
支持组合过滤条件：
- **IP 地址**: 支持列表选择或手动输入。
- **协议与端口**: TCP/UDP/ICMP 及指定端口。
- **时间范围**: 智能解析 `MMDDHHMMSS` 格式（自动补全当年年份）。

### 5. 🛠️ 现代化工程实现
- **Pathlib**: 全面使用面向对象的路径处理，完美兼容 Windows/Linux/macOS。
- **Robust IO**: 健壮的子进程管理与异常捕获，防止 Tshark 僵尸进程。

---

## 📋 环境要求

- **操作系统**: Windows, Linux, 或 macOS
- **Python**: 3.6+
- **依赖软件**: [Wireshark](https://www.wireshark.org/) (必须安装并确保 `tshark` 在系统环境变量 Path 中)

## 📦 安装与使用

1. **克隆项目**
   ```bash
   git clone [https://github.com/your-repo/pcap-filter.git](https://github.com/your-repo/pcap-filter.git)
   cd pcap-filter
