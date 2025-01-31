import pandas as pd
import akshare as ak
import matplotlib.pyplot as plt

class Backtest:
    def __init__(self, data):
        self.data = data
        self.data['Daily_MA'] = self.data['收盘'].rolling(window=20).mean()
        self.data['Weekly_MA'] = self.data['收盘'].rolling(window=100).mean()
        self.data['Monthly_MA'] = self.data['收盘'].rolling(window=200).mean()
        self.data.dropna(inplace=True)
        self.data['Signal'] = 0  # 初始化 Signal 列
        self.positions = []
        self.cash = 100000  # Initial cash
        self.shares = 0
        self.trades = []
        self.portfolio_value = self.cash  # Initialize portfolio value

    def generate_signals(self):
        self.data.loc[self.data['Daily_MA'] > self.data['Weekly_MA'], 'Signal'] = 1  # 买入信号
        self.data.loc[self.data['Daily_MA'] < self.data['Weekly_MA'], 'Signal'] = -1  # 卖出信号

    def backtest_strategy(self):
        self.generate_signals()
        with open('trades_log.txt', 'w') as f:
            f.write("Date, Price, Cash, Portfolio Value, Action, Shares\n")

            try:
                for i in range(1, len(self.data)):
                    # 交易逻辑
                    if self.data['Signal'].iloc[i] == 1 and self.data['Signal'].iloc[i-1] != 1:
                        # Buy signal
                        price = float(self.data['收盘'].iloc[i])
                        self.shares = self.cash // price  # 全仓买入
                        self.cash -= self.shares * price
                        self.portfolio_value = self.cash + self.shares * price
                        self.positions.append((self.data.index[i], 'Buy', price))
                        # 计算每次交易的收益率
                        if self.shares != 0:
                            profit = (self.cash + (self.shares * price)) / self.cash - 1
                        else:
                            profit = 0
                        self.trades.append((self.data.index[i], 'Buy', price, self.cash, self.shares, self.portfolio_value, profit))
                        print(f"Buy: Date: {self.data.index[i]}, Price: {price:.2f}, Cash: {self.cash:.2f}, Shares: {self.shares}, Portfolio Value: {self.portfolio_value:.2f}, Return: {profit:.2%}")
                        f.write(f"{self.data.index[i]}, {price:.2f}, {self.cash:.2f}, {self.portfolio_value:.2f}, Buy, {self.shares}\n")
                    elif self.data['Signal'].iloc[i] == -1 and self.data['Signal'].iloc[i-1] != -1:
                        # Sell signal
                        price = float(self.data['收盘'].iloc[i])
                        self.cash += self.shares * price  # 全仓卖出
                        self.portfolio_value = self.cash
                        self.positions.append((self.data.index[i], 'Sell', price))
                        # 计算每次交易的收益率
                        if self.shares != 0:
                            prev_price = float(self.data['收盘'].iloc[i-1])
                            profit = (self.cash - (self.shares * price)) / (self.shares * prev_price)
                        else:
                            profit = 0
                        self.trades.append((self.data.index[i], 'Sell', price, self.cash, 0, self.portfolio_value, profit))
                        print(f"Sell: Date: {self.data.index[i]}, Price: {price:.2f}, Cash: {self.cash:.2f}, Shares: 0, Portfolio Value: {self.portfolio_value:.2f}, Return: {profit:.2%}")
                        f.write(f"{self.data.index[i]}, {price:.2f}, {self.cash:.2f}, {self.portfolio_value:.2f}, Sell, 0\n")

                # Calculate final portfolio value
                final_price = float(self.data['收盘'].iloc[-1])
                final_portfolio_value = self.cash + self.shares * final_price
                print(f"Final Portfolio Value: {final_portfolio_value:.2f}")
                f.write(f"Final Date, Final Price, Final Cash, Final Portfolio Value, Action, Shares\n")
                f.write(f"{self.data.index[-1]}, {final_price:.2f}, {self.cash:.2f}, {final_portfolio_value:.2f}, Final, {self.shares}\n")
            except Exception as e:
                print(f"An error occurred: {e}")

    def plot_results(self):
        plt.figure(figsize=(14, 7))
        plt.plot(self.data['收盘'], label='Close Price')
        plt.plot(self.data['Daily_MA'], label='Daily MA')
        plt.plot(self.data['Weekly_MA'], label='Weekly MA')
        plt.plot(self.data['Monthly_MA'], label='Monthly MA')

        # Plot buy and sell signals
        for position in self.positions:
            if position[1] == 'Buy':
                plt.scatter(position[0], position[2], color='green', marker='^', label='Buy' if 'Buy' not in plt.gca().get_legend_handles_labels()[1] else "")
                plt.text(position[0], position[2], 'Buy', color='green', fontsize=10, verticalalignment='bottom')
            elif position[1] == 'Sell':
                plt.scatter(position[0], position[2], color='red', marker='v', label='Sell' if 'Sell' not in plt.gca().get_legend_handles_labels()[1] else "")
                plt.text(position[0], position[2], 'Sell', color='red', fontsize=10, verticalalignment='top')

        plt.legend()
        plt.show()

# 添加以下代码以运行回测和绘制结果
if __name__ == "__main__":
    # 示例数据加载
    stock_code = "002568"  # 例如：百润股份的股票代码
    data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date="20210101", end_date="20250101")
    data.set_index('日期', inplace=True)
    backtest = Backtest(data)
    backtest.backtest_strategy()
    backtest.plot_results()
