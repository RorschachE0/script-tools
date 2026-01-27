import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# --- 配置区域 ---
# 检查系统是否存在 tshark
if not shutil.which("tshark"):
    print("错误: 未在系统路径中找到 'tshark'。请先安装 Wireshark 并将其添加到环境变量。")
    sys.exit(1)


def run_tshark_command(cmd_list, capture=True):
    """
    执行 Tshark 命令并返回完整结果对象。
    capture=True: 捕获输出用于分析 (如提取IP)
    capture=False: 直接将输出显示在屏幕上 (如转换过程)
    """
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=capture,
            text=True,
            check=True,
            encoding='utf-8',
            errors='ignore'  # 忽略非 UTF-8 字符导致的解码报错
        )
        return result
    except subprocess.CalledProcessError as e:
        # 只有在非零退出码时触发
        # 注意：Tshark 在输出警告(Warning)时通常仍返回 0，只有严重错误才返回非0
        print(f"\n[!] Tshark 执行异常: {' '.join(cmd_list)}")
        if e.stderr:
            print(f"[!] 错误详情: {e.stderr}")
        return None


def extract_ips_fast(pcap_file: Path):
    """
    使用 tshark 统计模式 (-z endpoints) 极速提取 IP，避免逐包遍历。
    """
    print(f"[*] 正在扫描文件统计 IP (快速模式)...")
    # -q: 禁止打印包列表, -z: 统计端点
    # -o gui.max_tree_items:10000000 防止在统计阶段因包结构太深而报错
    cmd = [
        "tshark", "-r", str(pcap_file),
        "-q", "-z", "endpoints,ip",
        "-o", "gui.max_tree_items:10000000"
    ]
    result = run_tshark_command(cmd, capture=True)

    ip_set = set()
    if result and result.stdout:
        lines = result.stdout.splitlines()
        start_parsing = False
        for line in lines:
            # 过滤无关行
            if line.startswith("==="): continue
            if "IPv4 Endpoints" in line:
                start_parsing = True
                continue
            if "IPv6 Endpoints" in line:
                continue

            # 解析表格内容
            if start_parsing and line.strip() and not line.startswith("Filter"):
                parts = line.split()
                if parts:
                    ip = parts[0]
                    # 简单格式校验
                    if ip.count('.') == 3 and ip.replace('.', '').isdigit():
                        ip_set.add(ip)

    # 智能排序
    return sorted(list(ip_set), key=lambda x: [int(p) for p in x.split('.') if p.isdigit()])


def parse_user_time(time_str):
    """
    解析用户输入的 MMDDHHMMSS 格式，自动补全当年年份。
    """
    if not time_str: return None
    try:
        current_year = datetime.now().year
        dt = datetime.strptime(f"{current_year}{time_str}", "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"    [!] 时间格式错误: {time_str}，已忽略时间过滤。")
        return None


def main():
    current_dir = Path.cwd()
    # 查找 pcap 文件
    extensions = {'.cap', '.pcap', '.pcapng'}
    files = [f for f in current_dir.iterdir() if f.suffix in extensions and f.is_file()]

    if not files:
        print(f"[-] 当前目录 {current_dir} 下未找到数据包文件。")
        return

    print(f"\n[+] 发现 {len(files)} 个数据包文件:")
    for idx, f in enumerate(files):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {idx + 1}: {f.name} ({size_mb:.2f} MB)")

    # 1. 选择文件
    while True:
        try:
            choice = input(f"\n> 请选择文件编号 (1-{len(files)}): ").strip()
            if not choice: continue
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                selected_file = files[idx]
                break
            print("编号超出范围。")
        except ValueError:
            print("请输入有效数字。")

    # 2. 提取并选择 IP
    unique_ips = extract_ips_fast(selected_file)
    target_ip = None

    if unique_ips:
        print(f"\n[+] 发现 {len(unique_ips)} 个 IPv4 地址:")
        # 如果IP太多，只显示前20个
        display_ips = unique_ips[:20]
        for idx, ip in enumerate(display_ips):
            print(f"  {idx + 1}: {ip}")
        if len(unique_ips) > 20:
            print(f"  ... (剩余 {len(unique_ips) - 20} 个未显示)")

        mode = input("\n> 选择模式 [1:列表编号 / 2:手动输入 / Enter:跳过]: ").strip()

        if mode == '1':
            while True:
                try:
                    c_str = input(f"> 输入 IP 编号 (1-{len(display_ips)}): ").strip()
                    if not c_str: break  # 允许在子菜单放弃
                    c = int(c_str)
                    if 1 <= c <= len(display_ips):
                        target_ip = display_ips[c - 1]
                        break
                    print("编号无效。")
                except ValueError:
                    pass
        elif mode == '2':
            inp = input("> 输入目标 IP: ").strip()
            if inp:
                target_ip = inp
            else:
                print("    未输入内容，跳过 IP 过滤。")
    else:
        print("[-] 未发现 IPv4 地址，跳过 IP 过滤。")

    # 3. 协议与端口
    protocol = input("\n> 输入协议 (tcp/udp/icmp... 或 Enter跳过): ").strip()
    port = ""
    if protocol in ['tcp', 'udp']:
        port = input(f"> 输入 {protocol} 端口号 (或 Enter跳过): ").strip()

    # 4. 时间过滤
    print("\n[!] 时间格式: MMDDHHMMSS (默认为当年)")
    t_start = input("> 开始时间 (Enter跳过): ").strip()
    t_end = input("> 结束时间 (Enter跳过): ").strip()

    fmt_start = parse_user_time(t_start)
    fmt_end = parse_user_time(t_end)

    # 5. 构建过滤器
    filters = []
    if target_ip:
        filters.append(f"ip.addr == {target_ip}")
    if protocol:
        filters.append(protocol)
    if port:
        filters.append(f"{protocol}.port == {port}")
    if fmt_start:
        filters.append(f'frame.time >= "{fmt_start}"')
    if fmt_end:
        filters.append(f'frame.time <= "{fmt_end}"')

    filter_str = " && ".join(filters)

    # 6. 准备输出路径
    output_dir = current_dir / "filtered_results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"filtered_{selected_file.name}"

    print("-" * 50)
    print(f"源文件: {selected_file.name}")
    print(f"过滤器: {filter_str if filter_str else '无 (完整导出)'}")
    print(f"保存至: {output_file}")
    print("-" * 50)

    # 7. 执行处理逻辑 (关键修复区域)
    if not filter_str:
        # 【安全修复 1】如果没有过滤器，直接使用 Python 复制
        # 这避免了 Tshark 重新解析 Mongo 包导致的崩溃，且速度极快
        print("[*] 检测到无过滤条件，正在执行直接复制 (安全模式)...")
        try:
            shutil.copy2(selected_file, output_file)
            print(f"\n[√] 复制成功！")
            print(f"    文件大小: {output_file.stat().st_size / (1024 * 1024):.2f} MB")
        except Exception as e:
            print(f"\n[x] 复制失败: {e}")
        return

    # 如果有过滤器，必须使用 Tshark
    # 【安全修复 2】增加 gui.max_tree_items 参数，防止 Mongo 解析导致的无限循环报错
    tshark_args = [
        "tshark",
        "-r", str(selected_file),
        "-w", str(output_file),
        "-o", "gui.max_tree_items:10000000"  # 扩大协议树限制到 1000 万
    ]
    if filter_str:
        tshark_args.extend(["-Y", filter_str])

    print("[*] 正在处理数据包 ...")

    # capture=False 让 tshark 的原生输出显示在屏幕上
    result_obj = run_tshark_command(tshark_args, capture=False)

    # 8. 结果验证
    if result_obj is not None and result_obj.returncode == 0:
        if output_file.exists():
            final_size = output_file.stat().st_size
            if final_size > 0:
                print(f"\n[√] 处理成功！")
                print(f"    文件路径: {output_file}")
                print(f"    文件大小: {final_size / (1024 * 1024):.2f} MB")
            else:
                print(f"\n[!] 警告: 生成的文件为空 (0 KB)。")
                print("    可能原因: 过滤条件过于严格，或数据包损坏。")
        else:
            print("\n[x] 错误: 命令显示成功，但未找到输出文件。")
    else:
        print("\n[x] 处理失败。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户强制中断。")
    except Exception as e:
        print(f"\n[!] 发生未知错误: {e}")

    input("\n按 Enter 键退出...")