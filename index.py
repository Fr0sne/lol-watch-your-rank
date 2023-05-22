import requests
from bs4 import BeautifulSoup
import time
import inquirer
import json
from datetime import datetime
import os
from colorama import Fore, init, Style
import re

init()
try:
    stored = json.load(open('champions.json', 'r'))
except:
    all_champions = json.loads(requests.get("https://www.leagueoflegends.com/page-data/en-us/champions/page-data.json").text)['result']['data']['allChampions']['edges']
    json.dump(all_champions, open('champions.json', 'w'), indent=4)
    stored = all_champions

champions_names = list(map(lambda _: _['node']['champion_name'], stored))
regions = ["BR", "EUW", "KR", "LAS", "OCE", "RU", "TH", "TW", "VN", "TR", "SG", "PH", "NA", "LAN", "JP", "EUNE"]
last_pos = 0
messages = []
last_update = None
close_flag = False
stored.clear()
ua = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-A720F Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.120 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/331.1.0.29.117;]"
}

def flush_messages( success_message = "", inquirer_ = None, input = None):
    global messages
    selected_value = None
    if inquirer_:
        inquirer_result = inquirer.prompt(inquirer_)
        selected_value = inquirer_result[list(inquirer_result.keys())[0]]
    elif input:
        selected_value = input
    messages.append(success_message + Fore.YELLOW + selected_value + Style.RESET_ALL)
    os.system('cls')
    for message in messages: print(message)
    return selected_value

def info_messages():
    print('❗ Ctrl + C para parar o programa.')


def load_data():
    try:
        stored = json.load(open('data.json', 'r', encoding="utf-8"))
        options = [f'{index}. {item["summoner"]} | {item["champion"]} | {item["region"]}' for index, item  in enumerate(stored)]
        options.append('❌ Criar novo')
        load = inquirer.prompt([inquirer.List("load", message="Selecione um dado salvo", carousel=True, choices=options)])
        if 'Criar novo' in load:
            return
        return stored[int(load['load'].split('.')[0])]
    except: pass


def setup():
    global regions, champions_names, close_flag
    load = inquirer.prompt([inquirer.Confirm("load", True, message="Existem dados salvos. Deseja carregar?",) ])
    loaded = load_data() if load["load"] else None
    if not loaded:
        regions_options = [inquirer.List(name="region", message="Escolha sua região", carousel=True, choices=regions)]
        champions_options = [inquirer.List(name="champion", message="Escolha um campeão", carousel=True, choices=champions_names)]
        target_champion = flush_messages(f"✅ Campeão selecionado: ", champions_options)
        target_summoner = flush_messages(f"✅ Invocador selecionado: ", input=input('[?] Nome de invocador: '))
        target_region = flush_messages(f"✅ Região selecionada: ", regions_options)
        save = inquirer.prompt([inquirer.Confirm("test", True, message="Deseja salvar esses dados para uma próxima execução?",) ])
        if save:
            new_data = {"champion": target_champion, "summoner": target_summoner, "region": target_region}
            try:
                stored = json.load(open('data.json', 'r', encoding="utf-8"))
                stored.append(new_data)
                json.dump(stored, open('data.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)
            except: json.dump([new_data], open('data.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)
                
    else:
        target_champion = loaded['champion']
        target_summoner = loaded['summoner']
        target_region = loaded['region']
    main(re.sub(r'[^A-Za-z]', '', target_champion.lower()), target_region.lower(), target_summoner.lower(), target_champion)

def main(champion, region, summoner, original_champion_name):
    global  last_pos, close_flag
    url = f"https://www.leagueofgraphs.com/en/summoner/champions/{champion}/{region}/{summoner}"
    try:
        response = requests.get(url, headers=ua)
        now = datetime.now()
        current_time = now.strftime("%Hh:%Mm:%Ss")
        soup = BeautifulSoup(response.text, 'html.parser')
        pos = int(soup.find_all(attrs={"class": "solo-number"})[1].text.replace(',', '').replace('#', ''))
        last_update = current_time
        last_operation = "📉" if pos < last_pos else ("📈" if (pos > last_pos and last_pos != 0) else "-")
        print(f"\r✅ 👑 Ranking {original_champion_name}: {pos} {last_operation} | Last update: {current_time}", end="", flush=True)
        print(" ", end="", flush=True)
        last_pos = pos
        time.sleep(60)
    except (KeyboardInterrupt, Exception) as e:
        if KeyboardInterrupt:
            close_flag = True
        print(f"\r✅ 👑 Ranking Evelynn: {pos} {last_operation} | Last update: {last_update} ❌", end="", flush=True)
        print(" ", end="", flush=True)
    finally:
        if close_flag: exit()
        main(champion, region, summoner, original_champion_name)
        




if __name__ == '__main__':
    setup()
