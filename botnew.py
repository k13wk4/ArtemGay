import requests
import cloudscraper
import json
import os
from datetime import datetime
import time
import pytz
from colorama import Fore, Style

wib = pytz.timezone('Europe/Kyiv')
# Настройки порогов и множителей для каждого типа игры
game_thresholds = {
    'slotMachine': [
        (5000000, 100000),  # Если энергия больше 5,000,000, использовать множитель 100000
        (100000, 10000),    # Если энергия больше 10000, использовать множитель 10000
        (1000, 1000),     # Если энергия больше 1000 использовать множитель 1000
        (500, 500)            # Если энергия больше 0 использовать множитель 500
    ],
    'wheelOfFortune': [
        (100000, 25),
        (30000, 10),
        (10000, 5),  # Если энергия больше 10,000, использовать множитель 5
        (1000, 3),   # Если энергия больше 1,000 использовать множитель 3
        (0, 1)       # Если энергия меньше 1,000 использовать множитель 1
    ]
}
dc4_balance_max = 2000
dc4_balance_min = 1500

# Крутить слот машину или нет
USE_GAE = True

class Boinkers:
    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper()
        self.last_gae_resource = None
        self.do_last_gae_resource = None
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
            'Cache-Control': 'no-cache',
            'Host': 'boink.boinkers.co',
            'Origin': 'https://boink.boinkers.co',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'


        }

    @staticmethod
    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def log(message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    @staticmethod
    def welcome():
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Boinkers - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<K13WK4>
            """
        )

    @staticmethod
    def format_seconds(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @staticmethod
    def print_retry_message(attempt, retries):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ ERROR ]{Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{attempt + 1}/{retries}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

    def load_op_id(self, retries=5):
        url = 'https://boink.boinkers.co/public/data/config?p=android'
        headers = {
            **self.headers,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=headers, timeout=10)
                if response.status_code == 403:
                    return None
                response.raise_for_status()
                live_ops = response.json()['liveOps']

                # Ищем первый элемент, который соответствует условиям
                element = next((op['_id'] for op in live_ops if
                                'mainButtonOverrides' in op and
                                'wheelOfFortune' in op['mainButtonOverrides']), None)

                return element
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(5)
                else:
                    return None

    def users_login(self, query: str, retries=3):
        url = 'https://boink.boinkers.co/public/users/loginByTelegram?tgWebAppStartParam=boink241967995&p=android'
        data = json.dumps({"initDataString":query, "sessionParams":{}})
        headers = {
            **self.headers,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, data=data, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def users_me(self, token: str, retries=3):
        url = 'https://boink.boinkers.co/api/users/me?p=android'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None
        
    def claim_booster(self, token: str, retries=3):
        url = 'https://boink.boinkers.co/api/boinkers/addShitBooster?p=android'
        data = json.dumps({'multiplier':2, 'optionNumber':1})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, data=data, timeout=10)
                if response.status_code == 403:
                    return None

                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None
    

    def claim_inbox(self, token: str, message_id: str, retries=3):
        url = 'https://boink.boinkers.co/api/inboxMessages/claimInboxMessagePrize?p=android'
        data = json.dumps({'inboxMessageId':message_id})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, data=data, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def spin_wheel(self, token: str, game_type: str, live_op_id: str, multiplier: str, retries: int = 3):
        url = f'https://boink.boinkers.co/api/play/spin{game_type}/{multiplier}'

        if game_type == 'WheelOfFortune':
            data = json.dumps({'liveOpId': live_op_id} if live_op_id else {})
        elif game_type == 'SlotMachine':
            data = json.dumps({})  # Исправлено: создаем JSON даже для пустого словаря
        else:
            raise ValueError(f"Unexpected game type: {game_type}")
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, data=data, timeout=10)
                if response.status_code == 403:
                    print(f"{Fore.YELLOW + Style.BRIGHT}[ WARNING ] {Style.RESET_ALL} Forbidden access detected.")
                    return None
                response.raise_for_status()
                return response.json()
            except (cloudscraper.exceptions.CloudflareException, requests.RequestException, ValueError) as e:
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    print(
                        f"{Fore.RED + Style.BRIGHT}[ ОШИБКА ] {Style.RESET_ALL}"
                        f"Не удалось после {retries} попыток: {str(e)}"
                    )
                    return None

    def open_elevator(self, token: str, live_op_id: str, retries=3):
        url = 'https://boink.boinkers.co/api/play/openElevator?p=android'
        data = json.dumps({'liveOpId':live_op_id})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, data=data, timeout=10)
                if response.status_code == 403:
                    return None

                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None
        
    def quit_elevator(self, token: str, retries=3):
        url = 'https://boink.boinkers.co/api/play/quitAndCollect?p=android'
        data = {}
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 403:
                    return None

                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def upgrade_boinker(self, token: str, upgrade_type: str, retries=3):
        url = f'https://boink.boinkers.co/api/boinkers/{upgrade_type}?p=android'
        data = {}
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, json=data, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def gae_data(self, token: str, retries=3):
        url = 'https://boink.boinkers.co/api/gae/getGaeDataForUser?p=android'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None
    
    def raffle_data(self, token: str, retries=3):
        url = 'https://boink.boinkers.co/api/raffle/getRafflesData?p=android'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None
        
    def claim_raffle(self, token: str, retries=3):
        url = 'https://boink.boinkers.co/api/raffle/claimTicketForUser?p=android'
        data = {}
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 403:
                    return None

                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None



    def event_id(self, retries=3):
        url = 'https://boink.boinkers.co/public/data/config?p=android'
        headers = {
            **self.headers,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def check_progress_id(self, token: str, operation_id: str, retries=3):
        url = f'https://boink.boinkers.co/api/liveOps/dynamic/{operation_id}/progress?p=android'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def event_get_new_prize(self, token: str, operation_id: str, idx: int, retries=3):
        url = f'https://boink.boinkers.co/api/liveOps/dynamic/{operation_id}/{idx}'
        data = {}
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        for attempt in range(retries):
            try:
                response = self.scraper.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 402:
                    self.log(f"{Fore.RED + Style.BRIGHT}Ошибка недостаточно средств для idx: {idx}{Style.RESET_ALL}")
                    return None
                if response.status_code == 403:
                    return None

                response.raise_for_status()
                return response.json()
            except (requests.RequestException, requests.Timeout, ValueError):
                if attempt < retries - 1:
                    self.print_retry_message(attempt, retries)
                    time.sleep(2)
                else:
                    return None

    def process_query(self, query: str, live_op_id: str):

        login_info = self.users_login(query)
        token = login_info['token']

        if not token:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Аккаунт{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Запрос неверен {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return

        if token:

            user = self.users_me(token)

            if user:
                gold = user.get('currencySoft', 0)
                shit = user.get('currencyCrypto', 0)


                dynamic_currencies = user.get('dynamicCurrencies', {})
                dc4_balance = dynamic_currencies.get('dc4', {}).get('balance', 0)

                games_energy = user.get('gamesEnergy', {})
                if dc4_balance < dc4_balance_min:
                    if games_energy:
                        self.log(
                            f"{Fore.YELLOW + Style.BRIGHT}[ВНИМАНИЕ]{Style.RESET_ALL} Ресурс пользователя GAE "
                            f"({Fore.WHITE + Style.BRIGHT}{dc4_balance}{Style.RESET_ALL}) меньше необходимого "
                            f"({Fore.WHITE + Style.BRIGHT}{dc4_balance_max}{Style.RESET_ALL}). Проверяем наличие энергии..."
                        )

                        for game_type, details in games_energy.items():
                            if game_type == 'wheelOfFortune' and game_type in game_thresholds:
                                energy = details['energy']
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} Энергии "
                                    f"({Fore.WHITE + Style.BRIGHT}{energy}{Style.RESET_ALL}) достаточно для игры {Fore.WHITE + Style.BRIGHT}{game_type}{Style.RESET_ALL}."
                                )
                                thresholds = game_thresholds[game_type]
                                while energy > 0:
                                    multiplier = next((mult for threshold, mult in thresholds if energy > threshold),
                                                      thresholds[-1][1])
                                    spin_result = self.spin_wheel(token, 'WheelOfFortune', live_op_id, multiplier)
                                    if spin_result is None:
                                        print(
                                            f"Получен None при попытке вызова spin_wheel с параметрами: live_op_id={live_op_id}, multiplier={multiplier}")
                                    if spin_result:
                                        energy = spin_result['userGameEnergy']['energy']
                                        reward = spin_result['prize']['prizeValue']
                                        reward_type = spin_result.get('prize', {}).get('prizeTypeName', 'Gae')
                                        new_dynamic_currencies = spin_result.get('newDynamicCurrencies', {})
                                        user_dc4_balance = new_dynamic_currencies.get('dc4', {}).get('balance', 0)

                                        self.log(
                                            f"{Fore.GREEN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} Вращение успешно: "
                                            f"Тип: {Fore.WHITE + Style.BRIGHT}{game_type}{Style.RESET_ALL}, Награда: "
                                            f"{Fore.WHITE + Style.BRIGHT}{reward}{Style.RESET_ALL} ({Fore.WHITE + Style.BRIGHT}{reward_type}{Style.RESET_ALL}), "
                                            f"Осталось энергии: {Fore.WHITE + Style.BRIGHT}{energy}{Style.RESET_ALL}, "
                                            f"Множитель: {Fore.WHITE + Style.BRIGHT}{multiplier}{Style.RESET_ALL}, "
                                            f"DC4 баланс: {Fore.WHITE + Style.BRIGHT}{user_dc4_balance}{Style.RESET_ALL}"
                                        )

                                        if user_dc4_balance >= dc4_balance_max:
                                            self.log(
                                                f"{Fore.GREEN + Style.BRIGHT}[УСПЕХ]{Style.RESET_ALL} DC4 Ресурс "
                                                f"({Fore.WHITE + Style.BRIGHT}{user_dc4_balance}{Style.RESET_ALL}) превысил необходимый "
                                                f"({Fore.WHITE + Style.BRIGHT}{dc4_balance_max}{Style.RESET_ALL}). Останавливаем вращения."
                                            )
                                            break
                                    else:
                                        self.log(
                                            f"{Fore.RED + Style.BRIGHT}[ОШИБКА]{Style.RESET_ALL} . Переходим к следующему этапу."
                                        )
                                        break  # Выходим из цикла при ошибке, переходим к следующему этапу

                                    time.sleep(1)  # Задержка для избежания ограничения API

                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} Ресурс DC4 "
                        f"({Fore.WHITE + Style.BRIGHT}{dc4_balance}{Style.RESET_ALL}) достаточен "
                        f"({Fore.WHITE + Style.BRIGHT}{dc4_balance_min}{Style.RESET_ALL}). Переходим к следующей задаче."
                    )
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Аккаунт{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {user['userName']} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL} [ Баланс{Style.RESET_ALL} "
                    f"{Fore.WHITE + Style.BRIGHT}{gold} Gold🪙 {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{dc4_balance} DC4 {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{shit:.4f} Shit💩 {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                time.sleep(1)

                claim_booster = self.claim_booster(token)
                if claim_booster:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boost Mining{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boost Mining{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Is Already Claimed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                inbox = user['inboxMessages']
                if inbox:
                    completed = False
                    for message in inbox:
                        message_id = message['_id']
                        status = message['state']

                        if message and status != "claimed":
                            claim_inbox = self.claim_inbox(token, message_id)
                            if claim_inbox:
                                reward = claim_inbox['gottenPrize']['prizeValue']
                                reward_type = claim_inbox.get('gottenPrize', {}).get('prizeName', 'Gold')
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Inbox{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {message['title']} {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {reward} {reward_type} {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Inbox{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {message['title']} {Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                        else:
                            completed = True

                    if completed:
                        self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Inbox{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Clear {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Inbox{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} No Available Message {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                for _ in range(4):  # Выполняем 4 попытки
                    open_elevator = self.open_elevator(token, live_op_id)
                    if open_elevator:
                        reward = open_elevator['prize']['prizeValue']
                        reward_type = open_elevator['prize']['prizeTypeName']

                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Elevator{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} Is Opened {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Result{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} You Win {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {reward} {reward_type} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Elevator{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} No Available Attempt {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        break  # Выходим из цикла, если попытка не удалась

                    time.sleep(2)

                # После завершения цикла (4 попытки или неудачная попытка) вызываем quit_elevator
                self.quit_elevator(token)
                time.sleep(1)  # Задержка после завершения всех действий с лифтом

                boinkers = user['boinkers']
                if boinkers:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boinker{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {boinkers['currentBoinkerProgression']['id']} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Level {boinkers['currentBoinkerProgression']['level']} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
                    time.sleep(1)

                    upgrade_type = ['megaUpgradeBoinkers', 'upgradeBoinker']
                    while True:
                        for upgrade in upgrade_type:
                            upgrade_boinker = self.upgrade_boinker(token, upgrade_type=upgrade)
                            time.sleep(7)

                            if upgrade_boinker:
                                boink_id = upgrade_boinker['userBoinkers']['currentBoinkerProgression']['id']
                                level = upgrade_boinker['userBoinkers']['currentBoinkerProgression']['level']

                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Boinker{Style.RESET_ALL}"
                                     f"{Fore.GREEN + Style.BRIGHT} {'Mega ' if upgrade == 'megaUpgradeBoinkers' else ''}Upgrade Successful {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {boink_id} {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} - Level {level} {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                )

                            else:
                                if upgrade == 'megaUpgradeBoinkers':
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boinker{Style.RESET_ALL}"
                                        f"{Fore.RED + Style.BRIGHT} Mega Upgrade Failed {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} Balance Not Enough {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                    )
                                else:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boinker{Style.RESET_ALL}"
                                        f"{Fore.RED + Style.BRIGHT} Isn't Upgraded {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} Balance Not Enough {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                    )

                                break

                            time.sleep(1)

                        else:
                            continue

                        break

                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boinker{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                free_loot = self.event_id()
                if free_loot:
                    live_ops = free_loot.get('liveOps', [])
                    for live_op in live_ops:
                        if 'dynamicLiveOp' in live_op and live_op['dynamicLiveOp'].get('eventType') == 'orderedGrid':
                            operation_id = live_op['_id']
                            dynamic_live_op = live_op['dynamicLiveOp']

                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ ID{Style.RESET_ALL}{Fore.WHITE + Style.BRIGHT} {operation_id} {Style.RESET_ALL}{Fore.MAGENTA + Style.BRIGHT}] [ Приняты в работу ]{Style.RESET_ALL}")

                            # Определяем количество доступных наград
                            milestones_count = next(
                                (i for i, milestone in enumerate(dynamic_live_op.get('milestones', [])) if
                                 milestone.get('cost', {}).get('paymentOption') == 7),
                                None
                            )

                            if milestones_count is not None:
                                progress = self.check_progress_id(token, operation_id)

                                # Здесь мы устанавливаем received_rewards в 0, если нет прогресса
                                received_rewards = len(progress) if progress else 0

                                for idx in range(received_rewards, milestones_count):
                                    if idx < len(
                                            dynamic_live_op.get('milestones', [])):  # Проверка выхода за пределы списка
                                        milestone = dynamic_live_op['milestones'][idx]
                                        try:
                                            cost = milestone['cost']
                                            if cost['paymentType'] == 'dc4' and cost['price'] <= 1000:
                                                reward = self.event_get_new_prize(token, operation_id, idx)
                                                if reward:
                                                    # Извлечение информации о награде
                                                    milestone_response = next(
                                                        (m for m in reward.get('milestones', []) if
                                                         m['milestone'] == idx),
                                                        None)
                                                    if milestone_response and 'prizes' in milestone_response:
                                                        prize_info = milestone_response['prizes'][0]
                                                        self.log(
                                                            f"{Fore.GREEN + Style.BRIGHT}Награда получена для milestone {idx}: {prize_info['prizeName']} - {prize_info['prizeValue']}{Style.RESET_ALL}")
                                                    else:
                                                        self.log(
                                                            f"{Fore.GREEN + Style.BRIGHT}Награда получена для milestone {idx}{Style.RESET_ALL}")
                                                    dc4_balance -= cost['price']  # Обновляем баланс для платных наград
                                                else:
                                                    self.log(
                                                        f"{Fore.RED + Style.BRIGHT}Не удалось получить награду для idx: {idx}{Style.RESET_ALL}")
                                            else:
                                                if cost['price'] > 1000:
                                                    self.log(
                                                        f"{Fore.YELLOW + Style.BRIGHT}Награда для idx: {idx} не получена, так как цена ({cost['price']}) больше 1000{Style.RESET_ALL}")
                                                else:
                                                    self.log(
                                                        f"{Fore.RED + Style.BRIGHT}Недостаточно средств для получения награды для idx: {idx}{Style.RESET_ALL}")
                                        except KeyError:
                                            # Если 'cost' отсутствует, это бесплатная награда
                                            reward = self.event_get_new_prize(token, operation_id, idx)
                                            if reward:
                                                milestone_response = next(
                                                    (m for m in reward.get('milestones', []) if m['milestone'] == idx),
                                                    None)
                                                if milestone_response and 'prizes' in milestone_response:
                                                    prize_info = milestone_response['prizes'][0]
                                                    self.log(
                                                        f"{Fore.GREEN + Style.BRIGHT}Бесплатная награда получена для milestone {idx}: {prize_info['prizeName']} - {prize_info['prizeValue']}{Style.RESET_ALL}")
                                                else:
                                                    self.log(
                                                        f"{Fore.GREEN + Style.BRIGHT}Бесплатная награда получена для milestone {idx}{Style.RESET_ALL}")
                                            else:
                                                self.log(
                                                    f"{Fore.RED + Style.BRIGHT}Не удалось получить бесплатную награду для idx: {idx}{Style.RESET_ALL}")
                                    else:
                                        break  # Выходим из цикла, если пытаемся обработать индекс за пределами массива
                            else:
                                self.log(
                                    f"{Fore.RED + Style.BRIGHT}Не удалось определить количество доступных наград для ID: {operation_id}{Style.RESET_ALL}")
                if USE_GAE:
                    gae = self.gae_data(token)
                    if gae:
                        milestones = gae.get('currentGae', {}).get('milestones', [])
                        last_milestone = milestones[-1] if len(milestones) > 0 else None
                        do_last_milestone = milestones[-2] if len(milestones) > 1 else None

                        self.last_gae_resource = last_milestone.get('gaeResource', None) if last_milestone else None
                        self.do_last_gae_resource = do_last_milestone.get('gaeResource', 0) if do_last_milestone else 0

                        current_gae_id = gae.get('currentGae', {}).get('_id', None)
                        name = gae.get('currentGae', {}).get('name', None)
                        user_gae_id = gae.get('userGae', {}).get('gaeId', None)
                        user_gae_resource = gae.get('userGae', {}).get('gaeResource', 0)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} GAE ID: {Fore.WHITE + Style.BRIGHT}{current_gae_id}{Style.RESET_ALL}, "
                            f"Имя: {Fore.WHITE + Style.BRIGHT}{name}{Style.RESET_ALL}, User GAE ID: {Fore.WHITE + Style.BRIGHT}{user_gae_id}{Style.RESET_ALL}, "
                            f"Ресурс: {Fore.WHITE + Style.BRIGHT}{user_gae_resource}{Style.RESET_ALL}, "
                            f"Ресурс последней вехи: {Fore.WHITE + Style.BRIGHT}{self.last_gae_resource}{Style.RESET_ALL}"
                        )

                        # gae_needed = self.last_gae_resource + self.do_last_gae_resource

                        gae_needed = self.do_last_gae_resource

                        games_energy = user.get('gamesEnergy', {})
                        if user_gae_resource < gae_needed:
                            if games_energy:
                                self.log(
                                    f"{Fore.YELLOW + Style.BRIGHT}[ВНИМАНИЕ]{Style.RESET_ALL} Ресурс пользователя GAE "
                                    f"({Fore.WHITE + Style.BRIGHT}{user_gae_resource}{Style.RESET_ALL}) меньше необходимого "
                                    f"({Fore.WHITE + Style.BRIGHT}{gae_needed}{Style.RESET_ALL}). Проверяем наличие энергии..."
                                )

                                for game_type, details in games_energy.items():
                                    if game_type == 'slotMachine' and game_type in game_thresholds:
                                        energy = details['energy']
                                        self.log(
                                            f"{Fore.CYAN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} Энергии "
                                            f"({Fore.WHITE + Style.BRIGHT}{energy}{Style.RESET_ALL}) достаточно для игры {Fore.WHITE + Style.BRIGHT}{game_type}{Style.RESET_ALL}."
                                        )

                                        thresholds = game_thresholds[game_type]

                                        while energy > 500:
                                            # Определяем подходящий множитель на основе текущей энергии
                                            multiplier = None
                                            for threshold, mult in thresholds:
                                                if energy > threshold:
                                                    multiplier = mult
                                                    break

                                            if multiplier is not None:
                                                spin = self.spin_wheel(token, 'SlotMachine', live_op_id, multiplier)
                                                if not spin:  # Если вращение не удалось (spin вернул None или False)
                                                    self.log(
                                                        f"{Fore.RED + Style.BRIGHT}[ОШИБКА]{Style.RESET_ALL} Вращение не удалось. Выход из цикла.")
                                                    break  # Выход из цикла while
                                                energy = spin['userGameEnergy']['energy']
                                                reward = spin['prize']['prizeValue']
                                                reward_type = spin.get('prize', {}).get('prizeTypeName', 'Gae')
                                                user_gae_resource_prize = spin.get('userGae', {}).get('gaeResource', 0)

                                                self.log(
                                                    f"{Fore.GREEN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} Вращение успешно: "
                                                    f"Тип: {Fore.WHITE + Style.BRIGHT}{game_type}{Style.RESET_ALL}, Награда: "
                                                    f"{Fore.WHITE + Style.BRIGHT}{reward}{Style.RESET_ALL} ({Fore.WHITE + Style.BRIGHT}{reward_type}{Style.RESET_ALL}), "
                                                    f"Осталось энергии: {Fore.WHITE + Style.BRIGHT}{energy}{Style.RESET_ALL}, "
                                                    f"Множитель: {Fore.WHITE + Style.BRIGHT}{multiplier}{Style.RESET_ALL}, "
                                                    f"Gae ресурс: {Fore.WHITE + Style.BRIGHT}{user_gae_resource_prize}{Style.RESET_ALL}"
                                                )

                                                if user_gae_resource_prize > gae_needed:
                                                    self.log(
                                                        f"{Fore.GREEN + Style.BRIGHT}[УСПЕХ]{Style.RESET_ALL} Gae Ресурс "
                                                        f"({Fore.WHITE + Style.BRIGHT}{user_gae_resource_prize}{Style.RESET_ALL}) превысил необходимый "
                                                        f"({Fore.WHITE + Style.BRIGHT}{gae_needed}{Style.RESET_ALL}). Останавливаем вращения."
                                                    )
                                                    break

                                            time.sleep(1)  # Задержка для избежания ограничения API

                        else:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ИНФО]{Style.RESET_ALL} Ресурс пользователя GAE "
                                f"({Fore.WHITE + Style.BRIGHT}{user_gae_resource}{Style.RESET_ALL}) достаточен "
                                f"({Fore.WHITE + Style.BRIGHT}{gae_needed}{Style.RESET_ALL}). Переходим к следующей задаче."
                            )
                raffle = self.raffle_data(token)
                if raffle:
                    raffle_id = raffle.get('userRaffleData', {}).get('raffleId', None)
                    milestone = raffle.get('userRaffleData', {}).get('milestoneReached', 0)
                    ticket = raffle.get('userRaffleData', {}).get('tickets', 0)
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Raffle{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} ID {raffle_id} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Milestone{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {milestone} Reached {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {ticket} Ticket {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    time.sleep(1)

                    while True:
                        claim = self.claim_raffle(token)
                        if claim:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Raffle{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} Ticket {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ Milestone{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {claim['milestoneReached']} Reached {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {claim['tickets']} Ticket {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Raffle{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} Ticket {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}Not Available to Claim{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                            break

                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )

    def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            while True:
                self.clear_terminal()

                live_op_id = self.load_op_id()
                if not live_op_id:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Boinkers{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Blocked By Cloudflare {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Restart Again {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    return

                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)

                for query in queries:
                    query = query.strip()
                    if query:
                        self.process_query(query, live_op_id)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)
                        time.sleep(3)

                seconds = 600
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Boinkers - BOT{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    bot = Boinkers()
    bot.main()