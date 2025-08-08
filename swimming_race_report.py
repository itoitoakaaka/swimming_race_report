# swimming_race_report.py

import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import re
import os

# =======================
# STEP 1: Webスクレイパー
# =======================
def extract_results(url, swimmer_name):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    rows = soup.select('table tr')
    for row in rows:
        if swimmer_name in row.text:
            tds = row.find_all('td')
            break
    else:
        print(f"{swimmer_name} のデータが見つかりませんでした")
        return None

    race_time = tds[2].text.strip()
    splits = re.findall(r'\d{1,2}:\d{2}\.\d{2}', row.text)

    def time_to_sec(t):
        m, s = t.split(':')
        return round(int(m)*60 + float(s), 2)

    data = []
    for i, t in enumerate(splits):
        dist = (i+1)*50
        seconds = time_to_sec(t)
        data.append((dist, t, seconds))

    df = pd.DataFrame(data, columns=['Distance(m)', 'Time', 'Time(s)'])
    df['Split(s)'] = df['Time(s)'].diff().fillna(df['Time(s)'])
    df['Velocity(m/s)'] = df['Distance(m)'] / df['Time(s)']

    df.to_csv('race_result.csv', index=False)
    print("✅ リザルト保存完了: race_result.csv")
    return df

# ===========================
# STEP 2: 映像クリック分析GUI
# ===========================
def click_event(event, x, y, flags, param):
    global timestamps
    if event == cv2.EVENT_LBUTTONDOWN:
        frame_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        time_sec = frame_idx / fps
        timestamps.append(time_sec)
        print(f"クリック: {round(time_sec, 2)}秒")

def analyze_video(video_path, px_per_meter, distance_m, race_time_s):
    global cap, fps, timestamps
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    timestamps = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("動画をクリック", frame)
        cv2.setMouseCallback("動画をクリック", click_event)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(timestamps) < 2:
        print("❌ ストロークが検出されていません")
        return None

    stroke_count = len(timestamps)
    stroke_intervals = np.diff(timestamps)
    avg_cycle_time = np.mean(stroke_intervals)
    stroke_rate = 60 / avg_cycle_time
    stroke_length = distance_m / (stroke_count / 2)
    velocity = distance_m / race_time_s

    metrics = {
        "Distance(m)": distance_m,
        "StrokeCount": stroke_count,
        "AvgCycleTime(s)": round(avg_cycle_time, 2),
        "StrokeRate(c/min)": round(stroke_rate, 2),
        "StrokeLength(m)": round(stroke_length, 2),
        "Velocity(m/s)": round(velocity, 2)
    }

    pd.DataFrame([metrics]).to_csv("stroke_metrics.csv", index=False)
    print("✅ 指標保存完了: stroke_metrics.csv")
    return metrics

# =========================
# STEP 3: レポート生成
# =========================
def generate_report():
    result = pd.read_csv("race_result.csv")
    stroke = pd.read_csv("stroke_metrics.csv")

    df = pd.merge_asof(result.sort_values("Distance(m)"),
                       stroke.sort_values("Distance(m)"),
                       on="Distance(m)", direction="nearest")

    plt.figure(figsize=(10, 7))

    plt.subplot(3, 1, 1)
    plt.plot(df['Distance(m)'], df['Velocity(m/s)'], marker='o', label='Velocity')
    plt.title('Velocity')
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(df['Distance(m)'], df['StrokeRate(c/min)'], marker='o', label='Stroke Rate', color='orange')
    plt.title('Stroke Rate')
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(df['Distance(m)'], df['StrokeLength(m)'], marker='o', label='Stroke Length', color='green')
    plt.title('Stroke Length')
    plt.xlabel('Distance (m)')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("race_report.png")
    print("✅ レポート出力完了: race_report.png")

# =========================
# 実行例（コメント外して使う）
# =========================
# extract_results("https://result.swim.or.jp/2024s/07/0727r/index.html", "山田 太郎")
# analyze_video("sample.mp4", px_per_meter=50, distance_m=50, race_time_s=28.35)
# generate_report()