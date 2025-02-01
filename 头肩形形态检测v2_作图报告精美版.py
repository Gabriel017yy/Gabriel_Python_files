import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

def detect_head_and_shoulders(prices, volumes, order=5):
    """
    检测头肩顶形态
    :param prices: 价格序列（Pandas Series）
    :param volumes: 交易量序列（Pandas Series）
    :param order: 局部极值点检测窗口大小
    :return: 关键点索引（左肩、头、右肩、颈线等）
    """
    if not isinstance(prices, pd.Series) or not isinstance(volumes, pd.Series):
        raise ValueError("prices 和 volumes 必须是 Pandas Series 类型")
    
    prices = prices.reset_index(drop=True)
    volumes = volumes.reset_index(drop=True)
    
    # 找到局部最大和最小值
    local_max_idx = argrelextrema(prices.values, np.greater, order=order)[0]
    local_min_idx = argrelextrema(prices.values, np.less, order=order)[0]
    
    if len(local_max_idx) < 3 or len(local_min_idx) < 2:
        return None  # 不能构成头肩顶
    
    # 确保索引足够长
    if len(local_max_idx) < 3 or len(local_min_idx) < 2:
        return None
    
    # 选择潜在的左肩、头、右肩
    A, C, E = local_max_idx[:3]  # 左肩、头、右肩
    B, D = local_min_idx[:2]  # 低点B和D，可能构成颈线
    
    # 条件判断
    if not (prices.iloc[C] > prices.iloc[A] and prices.iloc[C] > prices.iloc[E] and prices.iloc[E] < prices.iloc[C]):
        return None  # 头部必须最高
    if not (prices.iloc[D] <= prices.iloc[B] * 1.05 and prices.iloc[D] >= prices.iloc[B] * 0.95):
        return None  # D 点应接近 B
    if not (volumes.iloc[A] > volumes.iloc[C] and volumes.iloc[E] < volumes.iloc[C]):
        return None  # 交易量减少
    
    neckline = (prices.iloc[B] + prices.iloc[D]) / 2
    
    return {'left_shoulder': A, 'head': C, 'right_shoulder': E, 'neckline': neckline}

def check_for_downward_trend(prices, start_idx, end_idx, threshold=0.05):
    """
    检查在指定时间段内是否存在明显的下跌行情
    :param prices: 价格序列（Pandas Series）
    :param start_idx: 开始索引
    :param end_idx: 结束索引
    :param threshold: 下跌阈值
    :return: 是否存在明显的下跌行情
    """
    peak_price = prices.iloc[start_idx]
    future_prices = prices.iloc[start_idx:end_idx]
    if future_prices.empty:
        return False
    lowest_price = future_prices.min()
    return (peak_price - lowest_price) / peak_price > threshold

def plot_head_and_shoulders_with_trend(data, symbol):
    """
    绘制头肩顶形态及其后的下跌行情
    :param data: 包含价格和交易量的数据（Pandas DataFrame）
    :param symbol: 股票代码
    """
    prices = data['Close'].squeeze()
    volumes = data['Volume'].squeeze()
    plt.figure(figsize=(15, 6))  # 调整 plot 大小
    plt.plot(prices, label='Price', linewidth=2)
    
    trend_info = []
    with open(f"{symbol}_trend_report.txt", "w") as file:
        file.write("Report of Head and Shoulders Pattern Detection:\n")

    for i in range(len(prices) - 3):
        prices_slice = prices[i:].reset_index(drop=True)
        volumes_slice = volumes[i:].reset_index(drop=True)
        
        # 确保 prices_slice 和 volumes_slice 是 Pandas Series 类型
        if not isinstance(prices_slice, pd.Series):
            prices_slice = prices_slice.squeeze()
        if not isinstance(volumes_slice, pd.Series):
            volumes_slice = volumes_slice.squeeze()
        
        result = detect_head_and_shoulders(prices_slice, volumes_slice)
        if result:
            left_shoulder = i + result['left_shoulder']
            head = i + result['head']
            right_shoulder = i + result['right_shoulder']
            neckline = result['neckline']
            
            # 在图上标记出 Left Shoulder, Head, Right Shoulder
            plt.scatter(prices.index[left_shoulder], prices.iloc[left_shoulder], color='red', label='Left Shoulder' if i == 0 else "")
            plt.scatter(prices.index[head], prices.iloc[head], color='blue', label='Head' if i == 0 else "")
            plt.scatter(prices.index[right_shoulder], prices.iloc[right_shoulder], color='green', label='Right Shoulder' if i == 0 else "")

            # 检查是否出现下跌行情
            one_month_later = min(right_shoulder + 20, len(prices) - 1)  # 一个月后的时间点
            downtrend = check_for_downward_trend(prices, right_shoulder, one_month_later)
            trend_info.append((prices.index[right_shoulder], prices.index[one_month_later], downtrend))

            # 将每次检测结果写入 txt 文件
            try:
                with open(f"{symbol}_trend_report.txt", "a") as file:
                    downtrend_str = 'Yes' if downtrend else 'No'
                    file.write(f"Head and Shoulders形态出现时间: {prices.index[right_shoulder].strftime('%Y-%m-%d %H:%M:%S')}, 之后是否出现下跌情况: {downtrend_str}\n")
                print(f"Trend detection result appended to {symbol}_trend_report.txt")
            except Exception as e:
                print(f"Failed to write trend detection result to file: {e}")

    # 添加图例说明
    plt.legend(['Price', 'Left Shoulder', 'Head', 'Right Shoulder'], fontsize=12, loc='upper left', fancybox=True, framealpha=0.5, borderpad=1)

    plt.title(f"{symbol} Head and Shoulders Pattern Detection", fontsize=16, pad=20)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{symbol}_head_and_shoulders_plot.png")  # 保存图表
    
    # 删除重复行
    try:
        with open(f"{symbol}_trend_report.txt", "r") as file:
            lines = file.readlines()
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)
        with open(f"{symbol}_trend_report.txt", "w") as file:
            file.writelines(unique_lines)
        print(f"Duplicate lines removed from {symbol}_trend_report.txt")
    except Exception as e:
        print(f"Failed to remove duplicate lines from file: {e}")
    
    # 统计 yes 和 no 数量
    try:
        yes_count = 0
        no_count = 0
        for line in unique_lines:
            if '之后是否出现下跌情况: Yes' in line:
                yes_count += 1
            elif '之后是否出现下跌情况: No' in line:
                no_count += 1
        with open(f"{symbol}_trend_report.txt", "a") as file:
            file.write(f"\n统计结果: 总共检测到头肩形态 {yes_count + no_count} 次, 其中如期下跌的有 {yes_count} 次, 不符合预期的有 {no_count} 次\n")
        print(f"Trend statistics appended to {symbol}_trend_report.txt")
    except Exception as e:
        print(f"Failed to append trend statistics to file: {e}")
    
    plt.show()

# 导入股票数据
symbol = 'GOLD'  # stock或者futures的代码在这里键入
data = yf.download(symbol, start='2005-01-01', end='2025-01-01')

# 确保 prices 和 volumes 是 Pandas Series 类型
prices = data['Close'].squeeze()
volumes = data['Volume'].squeeze()

# 运行检测算法并绘制结果
try:
    plot_head_and_shoulders_with_trend(data, symbol)
except Exception as e:
    print(f"发生错误: {e}")
