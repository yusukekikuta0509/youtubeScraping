import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

# Seleniumセットアップ
def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# 適切な待機時間を設定する関数
def wait_with_message(seconds, message):
    print(f"{message} (待機 {seconds}秒)")
    time.sleep(seconds)

# テキストからメールアドレスを抽出する関数
def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

# YouTubeから情報を取得する関数
def scrape_youtube():
    driver = setup_browser()
    try:
        # 結果をCSVに書き込む準備
        with open("youtube_channels.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Channel Name", "Email", "Description"])  # ヘッダー行を作成

            # YouTubeにアクセス
            driver.get("https://www.youtube.com/")
            wait_with_message(5, "YouTubeのホームページにアクセス中")

            # ショート動画セクションに移動
            shorts_button = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/tp-yt-app-drawer/div[2]/div/div[2]/div[2]/ytd-guide-renderer/div[1]/ytd-guide-section-renderer[1]/div/ytd-guide-entry-renderer[2]/a/tp-yt-paper-item")
            shorts_button.click()
            wait_with_message(5, "ショート動画セクションに移動中")

            # 複数のショート動画を処理
            for i in range(1, 6):  # 最初の5つのショート動画を対象とする
                try:
                    # 動画のチャンネルページに移動
                    short_video = driver.find_element(By.XPATH, f"(/html/body/ytd-app/div[1]/ytd-page-manager/ytd-shorts/div[3]/div[2]/ytd-reel-video-renderer[1]/div[4]/ytd-reel-player-overlay-renderer/div[1]/div[1]/div/yt-reel-metapanel-view-model/div[1]/yt-reel-channel-bar-view-model/span/a)[{i}]")
                    short_video.click()
                    wait_with_message(5, f"ショート動画 {i} を再生中")

                    # チャンネル情報を取得
                    channel_link = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse[2]/div[3]/ytd-tabbed-page-header/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/div/div[2]/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/div/yt-attribution-view-model/span[2]/span/a")
                    channel_name = channel_link.text
                    channel_link.click()
                    wait_with_message(5, "チャンネルページに移動中")

                    # チャンネル概要にアクセス
                    about_tab = driver.find_element(By.XPATH, "//a[contains(@href, '/about')]")
                    about_tab.click()
                    wait_with_message(5, "チャンネル概要にアクセス中")

                    # チャンネル概要のテキストを取得
                    description = driver.find_element(By.XPATH, "/html/body/ytd-app/ytd-popup-container/tp-yt-paper-dialog/ytd-engagement-panel-section-list-renderer/div[2]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-about-channel-renderer/div").text

                    # メールアドレスを取得（存在する場合）
                    try:
                        email_text = driver.find_element(By.TAG_NAME, "body").text
                        email = extract_email(email_text)
                    except Exception as e:
                        print(f"メールアドレス取得中にエラー: {e}")
                        email = "Not found"

                    # 結果をCSVに保存
                    writer.writerow([channel_name, email, description])
                    print(f"チャンネル名: {channel_name}, メール: {email}")

                    # 戻る
                    driver.back()  # チャンネルページ -> ショート動画
                    wait_with_message(3, "ショート動画セクションに戻る")
                    driver.back()  # ショート動画セクション -> ショート動画一覧
                except Exception as e:
                    print(f"動画 {i} の処理中にエラー: {e}")
                    driver.back()

        print("情報を取得しました！結果はyoutube_channels.csvに保存されました。")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_youtube()
