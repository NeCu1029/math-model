import numpy as np
import pandas as pd
import simul_data as data
import matplotlib.pyplot as plt


def noise(x):
    return 2 * x * np.random.random() - x


def T(t):  # 기온 (t는 날짜)
    return (
        -12.13237713 * np.sin(np.pi * 2 / 365.25 * t + 1.24857351)
        + 14.62580424
        + noise(3)
    )


def P(t):  # 증기압 (t는 날짜)
    val = (
        -25.53476336 * np.sqrt(np.sin(np.pi / 365.25 * t - 4.95989598) ** 2)
        + 28.23420628
        + noise(3)
    )
    return max(val, 0)


def P0_base(t, a, b, c, d, e):
    return np.exp(a - b / (t + c)) / np.pow(t + d, e)


def P0(t):  # 포화 증기압 (t는 기온)
    if t > 0:
        return P0_base(t, 34.494, 4924.99, 237.1, 105, 1.57) / 100
    else:
        return P0_base(t, 43.494, 6545.8, 278, 868, 2) / 100


def RP(h):  # 강수 확률 (h는 상대 습도)
    return 1 / (1 + np.exp(-0.12023 * h + 8.83966484))


def R(t):  # 강수량 (t는 날짜, 랜덤 포함)
    if np.random.random() > RP(P(t) / P0(T(t)) * 100):
        return 0.0
    return (
        np.random.choice(
            data.rain_db[data.rain_db["month"] == data.month[t % 365]]["rain"]
        )
        / 1000
    )


def U(t):  # 사용량 (t는 날짜)
    return data.usage[data.month[t % 365]] + noise(5000)


def EV(t):  # 증발량 (t는 날짜)
    return C2 * max(P0(T(t)) - P(t), 0) / 1000


def O(t):  # 방류량 (t는 날짜)
    if 180 <= t % 365 <= 330:
        if W[t] <= 80:
            return 4.5e4
        elif W[t] <= 90:
            return 1.3e5
        else:
            return 3e5
    else:
        if W[t] <= 30:
            return 0
        elif W[t] >= 90:
            return 2e5
        else:
            return 3e3


rain_data = pd.read_csv("./climate.csv")
rain_data = rain_data[["일시", "일강수량(mm)"]]
rain_data.columns = ["date", "rain"]
rain_data = rain_data[rain_data["date"] >= "2023-01-01"]
rain_data = rain_data[rain_data["date"] <= "2023-12-31"]
rain_data.fillna(0, inplace=True)

DURATION = 365
C1 = 0.28  # 강수의 실제 유입 비율
C2 = 0.43432727  # 증발량 관련 비례상수
I = 1.8e4  # 무강수 시 유입량
G = 1e4  # 외부 급수량
J = 0.5  # 절수 비율
A_COL = 1.09e8  # 유역면적
A = 6.5e5  # 저수지 면적
V = 2e7  # 저수지 부피
rains = 0
W = [75.0]
difs = []
rsum = []
ins = []
outs = []

for t in range(DURATION):
    Rt = 0.3 * rain_data["rain"].iloc[t] / 1000
    in_cur = C1 * A_COL * Rt + I + G
    out_cur = A * EV(t) + (1 - J) * (U(t) + O(t))
    diff = (in_cur - out_cur) * 100 / V
    rains += Rt
    W.append(max(W[-1] + diff, 0))
    rsum.append(rains * 1000)
    ins.append(in_cur)
    outs.append(out_cur)
print("강수량 (mm):", round(rains * 1000, 2))

plt.subplot(221)
plt.plot(range(DURATION + 1), W, c="blue")
plt.plot(range(DURATION + 1), [0] * (DURATION + 1), c="black")
# plt.ylim(0, 1)
plt.title("Water Storage (%)")
plt.subplot(222)
plt.plot(range(1, DURATION + 1), rsum, c="orange")
plt.title("Accumulated Rainfall (mm / day)")
plt.subplot(223)
plt.plot(range(1, DURATION + 1), ins, c="green")
plt.title("Influx (m^3 / day)")
plt.subplot(224)
plt.plot(range(1, DURATION + 1), outs, c="red")
plt.title("Efflux (m^3 / day)")

plt.tight_layout()
plt.show()
