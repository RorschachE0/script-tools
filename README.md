# T-Filter: High-Performance Packet Forensics Tool

> **T-Filter** (`tfilter_v2.py`) 是一个基于 Python 封装 Tshark 的高性能网络数据包清洗与取证工具。它专为运维与安全人员设计，旨在解决传统脚本处理大体积 PCAP 文件时**速度慢、交互繁琐、复杂协议解析崩溃**的三大痛点。

---

## 🌟 核心亮点 (Key Features)

### 1. 🚀 极速 IP 提取 (Flash Extraction)
- **底层加速**: 摒弃了低效的 Python 循环遍历，T-Filter 调用 Tshark 的底层统计引擎 (`-z endpoints,ip`)，直接从 C 语言层面聚合会话。
- **性能飞跃**: 实测提取 1GB PCAP 文件中的唯一 IP 列表仅需几秒钟，速度提升 **10-50 倍**。

### 2. 🛡️ 协议防崩溃机制 (Crash Protection)
- **MongoDB/嵌套协议修复**: 针对深度嵌套的数据包（如复杂的 MongoDB 查询或 RPC），自动注入内核级参数 `-o "gui.max_tree_items:10000000"`。
- **解决痛点**: 彻底解决了 Wireshark 解析器因 *"Dissector bug / infinite loop"* 导致的处理中断或数据截断问题，确保取证数据的完整性。

### 3. ⚡ 智能直通模式 (Smart Bypass)
- **零延迟导出**: 当检测到用户未输入任何过滤条件时，自动降级为系统级文件复制 (IO Copy)。
- **无需解码**: 跳过耗时的解码/重编码过程，实现文件的瞬间导出。

### 4. 🎯 精准多维过滤
交互式引导用户构建复杂的 Wireshark 显示过滤器（Display Filter）：
- **IP 定位**: 支持“列表编号选择”或“手动输入”。
- **精准时间**: 智能解析 `MMDDHHMMSS` 格式（自动补全当前年份）。
- **协议栈**: 支持 TCP/UDP/ICMP 及特定端口过滤。

---

## 🛠️ 环境依赖 (Prerequisites)

- **操作系统**: Windows / Linux / macOS
- **Python**: 3.6+ (仅使用标准库，无需 `pip install`)
- **核心组件**: [Wireshark](https://www.wireshark.org/)
  > ⚠️ **注意**: 必须确保 `tshark` 命令已添加到系统的环境变量 (PATH) 中。

---

## 🚀 快速开始 (Quick Start)

### 1. 部署
将 `tfilter_v2.py` 放入包含数据包文件的目录中：

```text
Project/
├── tfilter_v2.py       # T-Filter 主程序
├── target.pcap         # 待分析的数据包
└── filtered_results/   # (自动生成) 结果输出目录
