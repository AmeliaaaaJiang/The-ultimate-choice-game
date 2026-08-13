from flask import Flask, render_template, request, redirect, url_for, session
import random
import uuid
import os


# =========================================================
# Flask
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "jiaojiao-local-dev-secret"
)


# =========================================================
# 48 个选项
# =========================================================

OPTIONS = [
    "皱如老树",
    "肥如年猪",
    "露营直播搭子眼睛被烟熏不闻不问",
    "831狂舞鬼船，卖腐对象是谁啊我不认识",
    "过年7天搭子评论一条不回",
    "高途vlog背景音和女stf打闹",
    "和赵小姐打闹",
    "单曲py的眷顾",
    "傻傻",
    "直播一板子浪花 可爱的小浪花",
    "背吉他回湖南",
    "演子",
    "呆比单线程",
    "晚安xyp",
    "whoo直播躲腐教程大全",
    "1227弹射皱眉路易十六",
    "唱歌如鸭叫",
    "跳舞如被电",
    "玩手机玩到腱鞘炎",
    "塑料片子和浴巾",
    "生日会切蛋糕捏着刀背也不肯碰到手",
    "不会照顾人",
    "面试+日料（仅文字料不负责真实程度）",
    "鬼船坐腿上",
    "长胖大于二十斤",
    "讨好老板d699",
    "卖团魂D499",
    "直播说搭子牙上有菜",
    "vlog尿流上班如上坟",
    "dzdp打卡按摩",
    "普通话倒欠二级 还一直在退步",
    "直播一直看提词器",
    "跟直播主持人开很亲密/莫名其妙的玩笑",
    "wb双人营业后ins只发单人照片",
    "抽烟熬夜狂喝全糖阿萨姆",
    "熬夜玩手机狂吃含糖水果",
    "不麦麸的单商后稳定更新自嬷擦边照",
    "长得快出栏了拍摄自嬷擦边照",
    "觅觅亲的",
    "jh那狗叫什么",
    "猪妞厕品代卖",
    "机场临时走v nj发视频",
    "男人味冲天仿佛随时要空气投篮",
    "姨味冲天仿佛要捏兰花指当牢星同类",
    "翻牌同一个wf多次",
    "sj粉圈还手滑关注",
    "车墩小红书没发双人图",
    "蹭狼兔"
]


# =========================================================
# 每一轮
# =========================================================

STAGES = {

    "round48": {
        "title": "ROUND 01",
        "name": "48 强",
        "flow": "48 → 24"
    },

    "round24": {
        "title": "ROUND 02",
        "name": "24 强",
        "flow": "24 → 12"
    },

    "round12": {
        "title": "ROUND 03",
        "name": "12 强",
        "flow": "12 → 6"
    },

    "round6": {
        "title": "ROUND 04",
        "name": "六强晋级",
        "flow": "6 → 4"
    },

    "semifinal": {
        "title": "SEMIFINAL",
        "name": "半决赛",
        "flow": "4 → 2"
    },

    "final": {
        "title": "FINAL",
        "name": "冠军赛",
        "flow": "2 → 1"
    },

    "bronze": {
        "title": "THIRD PLACE",
        "name": "季军赛",
        "flow": "3RD PLACE"
    }
}


# =========================================================
# 游戏临时数据
#
# 目前是本地 MVP，所以存在 Python 内存。
# 后面真正部署时可以换数据库。
# =========================================================

GAMES = {}


# =========================================================
# 准备一轮比赛
# =========================================================

def prepare_stage(game, stage, players):

    players = list(players)

    # 每轮重新随机
    random.shuffle(players)

    game["stage"] = stage
    game["match_index"] = 0
    game["winners"] = []
    game["byes"] = []


    # -----------------------------------------------------
    # 六强特殊处理
    #
    # 6 个选项：
    #
    # 2 个随机轮空
    # 4 个参加两场 PK
    #
    # 得到：
    # 2 个轮空 + 2 个赢家 = 4 强
    # -----------------------------------------------------

    if stage == "round6":

        game["byes"] = players[:2]

        game["match_pool"] = players[2:]

        game["winners"] = game["byes"].copy()

        game["byes_history"][stage] = game["byes"].copy()

    else:

        game["match_pool"] = players


# =========================================================
# 创建一局
# =========================================================

def create_game():

    game_id = str(uuid.uuid4())

    players = OPTIONS.copy()

    random.shuffle(players)


    game = {

        "stage": None,

        "match_pool": [],

        "match_index": 0,

        "winners": [],

        "byes": [],

        "byes_history": {},

        "history": [],

        "semifinal_losers": [],

        "champion": None,

        "runner_up": None,

        "third_place": None,

        "finished": False
    }


    GAMES[game_id] = game


    prepare_stage(
        game,
        "round48",
        players
    )


    return game_id


# =========================================================
# 当前 PK
# =========================================================

def get_current_pair(game):

    index = game["match_index"] * 2

    pool = game["match_pool"]


    if index + 1 >= len(pool):

        return None


    return (
        pool[index],
        pool[index + 1]
    )


# =========================================================
# 下一轮
# =========================================================

def advance_stage(game):

    stage = game["stage"]

    winners = game["winners"].copy()


    if stage == "round48":

        prepare_stage(
            game,
            "round24",
            winners
        )


    elif stage == "round24":

        prepare_stage(
            game,
            "round12",
            winners
        )


    elif stage == "round12":

        prepare_stage(
            game,
            "round6",
            winners
        )


    elif stage == "round6":

        prepare_stage(
            game,
            "semifinal",
            winners
        )


    elif stage == "semifinal":

        prepare_stage(
            game,
            "final",
            winners
        )


    elif stage == "final":

        # 冠军确定后，
        # 两位半决赛失败者参加季军赛

        prepare_stage(
            game,
            "bronze",
            game["semifinal_losers"]
        )


    elif stage == "bronze":

        game["finished"] = True


# =========================================================
# 首页
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        option_count=len(OPTIONS)
    )


# =========================================================
# 开始游戏
#
# HTML 对应：
#
# url_for("start")
# =========================================================

@app.route("/start", methods=["POST"])
def start():

    game_id = create_game()

    session["game_id"] = game_id


    return redirect(
        url_for("game")
    )


# =========================================================
# 游戏页面
# =========================================================

@app.route("/game")
def game():

    game_id = session.get("game_id")


    if not game_id:

        return redirect(
            url_for("index")
        )


    state = GAMES.get(game_id)


    if not state:

        return redirect(
            url_for("index")
        )


    if state["finished"]:

        return redirect(
            url_for("result")
        )


    pair = get_current_pair(state)


    if pair is None:

        return redirect(
            url_for("index")
        )


    left, right = pair


    total_matches = (
        len(state["match_pool"]) // 2
    )


    current_match = (
        state["match_index"] + 1
    )


    progress = (
        current_match
        / total_matches
        * 100
    )


    return render_template(

        "game.html",

        left=left,

        right=right,

        meta=STAGES[
            state["stage"]
        ],

        current_match=current_match,

        total_matches=total_matches,

        progress=progress,

        byes=state["byes"]
    )


# =========================================================
# 用户选择
# =========================================================

@app.route("/choose", methods=["POST"])
def choose():

    game_id = session.get("game_id")


    if not game_id:

        return redirect(
            url_for("index")
        )


    game = GAMES.get(game_id)


    if not game:

        return redirect(
            url_for("index")
        )


    pair = get_current_pair(game)


    if pair is None:

        return redirect(
            url_for("game")
        )


    left, right = pair


    choice = request.form.get(
        "choice"
    )


    if choice == "left":

        winner = left
        loser = right


    elif choice == "right":

        winner = right
        loser = left


    else:

        return redirect(
            url_for("game")
        )


    # =====================================================
    # 保存比赛历史
    # =====================================================

    game["history"].append({

        "stage":
            game["stage"],

        "left":
            left,

        "right":
            right,

        "winner":
            winner,

        "loser":
            loser
    })


    # =====================================================
    # 半决赛输家
    # =====================================================

    if game["stage"] == "semifinal":

        game[
            "semifinal_losers"
        ].append(
            loser
        )


    # =====================================================
    # 决赛
    # =====================================================

    if game["stage"] == "final":

        game["champion"] = winner

        game["runner_up"] = loser


    # =====================================================
    # 季军赛
    # =====================================================

    if game["stage"] == "bronze":

        game["third_place"] = winner


    # =====================================================
    # 当前赢家晋级
    # =====================================================

    game["winners"].append(
        winner
    )


    game["match_index"] += 1


    # =====================================================
    # 判断当前 Round 是否结束
    # =====================================================

    total_matches = (
        len(game["match_pool"])
        // 2
    )


    if (
        game["match_index"]
        >= total_matches
    ):

        advance_stage(game)


    # =====================================================
    # 如果季军赛也结束
    # =====================================================

    if game["finished"]:

        return redirect(
            url_for("result")
        )


    return redirect(
        url_for("game")
    )


# =========================================================
# 结果页面
# =========================================================

@app.route("/result")
def result():

    game_id = session.get(
        "game_id"
    )


    if not game_id:

        return redirect(
            url_for("index")
        )


    game = GAMES.get(
        game_id
    )


    if not game:

        return redirect(
            url_for("index")
        )


    if not game["finished"]:

        return redirect(
            url_for("game")
        )


    stage_order = [

        "round48",

        "round24",

        "round12",

        "round6",

        "semifinal",

        "final",

        "bronze"
    ]


    groups = []


    for stage in stage_order:

        matches = [

            match

            for match
            in game["history"]

            if match["stage"] == stage

        ]


        if matches:

            groups.append({

                "stage":
                    stage,

                "meta":
                    STAGES[stage],

                "matches":
                    matches,

                "byes":
                    game[
                        "byes_history"
                    ].get(
                        stage,
                        []
                    )
            })


    return render_template(

        "result.html",

        champion=
            game["champion"],

        runner_up=
            game["runner_up"],

        third_place=
            game["third_place"],

        groups=
            groups
    )


# =========================================================
# 再玩一次
# =========================================================

@app.route("/restart", methods=["POST"])
def restart():

    old_game_id = session.get(
        "game_id"
    )


    if old_game_id:

        GAMES.pop(
            old_game_id,
            None
        )


    new_game_id = create_game()

    session[
        "game_id"
    ] = new_game_id


    return redirect(
        url_for("game")
    )


# =========================================================
# 启动
# =========================================================

if __name__ == "__main__":

    print("")
    print("================================")
    print("角角落落不辱怎么追")
    print(f"{len(OPTIONS)} 个选项加载完成")
    print("服务器：http://127.0.0.1:5001")
    print("================================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True,
        use_reloader=False
    )