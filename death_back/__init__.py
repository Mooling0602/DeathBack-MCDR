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
    get_player_pos(player)

def tp_back_player(src: CommandSource):
    global position_data
    player = src.player
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
