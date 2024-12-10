import json
import os

from mcdreforged.api.all import *
import minecraft_data_api as api

psi = ServerInterface.psi()
position_data = {}

def on_load(server: PluginServerInterface, prev_module):
    server.register_event_listener("PlayerDeathEvent", on_player_death)
    server.register_command(
        Literal('!!back')
        .runs(
            lambda src: tp_back_player(src)
        )
    )

@new_thread('DeathBack: GetPlayerPos')
def get_player_pos(player: str):
    global position_data
    position: list = api.get_player_info(player, "Pos")
    dimension: str = api.get_player_info(player, "Dimension")
    position_data[player] = {
        'position': position,
        'dimension': dimension
    }
    
def format_position(position: list):
    x = position[0]
    y = position[1]
    z = position[2]
    formatted_pos = f"{x} {y} {z}"
    return formatted_pos

def on_player_death(server, player, event, content):
    server.logger.info(f"检测到玩家{player}的死亡事件，正在记录其位置...")
    get_player_pos(player)

def tp_back_player(src: CommandSource):
    global position_data
    APIMode = False
    player = src.player
    api_inject = f"{psi.get_data_folder()}/api.json"
    injected_plg = {}
    if os.path.exists(api_inject):
        try:
            with open(api_inject, "r", encoding="utf-8") as f:
                contents = f.read()
            injected_plg = json.loads(contents)
            if injected_plg["api"]["enabled"] and injected_plg["api"]["register"] is not None:
                APIMode = True
        except UnicodeDecodeError:
            with open(api_inject, "r", encoding="gbk") as f:
                contents = f.read()
            injected_plg = json.loads(contents)
            if injected_plg["api"]["enabled"] and injected_plg["api"]["register"] is not None:
                APIMode = True
    if not APIMode:
        try:
            player_data = position_data[player]
            pos = player_data['position']
            dim = player_data['dimension']
            loc = format_position(pos)
            psi.execute(f"execute in {dim} run tp {player} {loc}")
            del position_data[player]
            src.reply("传送执行完毕！")
        except KeyError:
            src.reply("没有你的死亡点位数据，可能你开服以来还没死过，或者你死后插件才加载或者发生重载。")
    else:
        plg_name = [injected_plg["api"]["register"]]
        src.reply(f"插件被用作前置API，无法进行传送，请使用下游插件：{plg_name}的功能！")
