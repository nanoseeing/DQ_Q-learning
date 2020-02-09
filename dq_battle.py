from enum import Enum, auto
import random
import numpy as np
from collections import deque


class Character(object):

    """ キャラクタークラス"""

    ACTIONS = {0: "攻撃", 1: "回復"}

    def __init__(self, hp, max_hp, attack, defence, agillity, intelligence, name):
        self.hp = hp  # 現在のHP
        self.max_hp = max_hp  # 最大HP
        self.attack = attack  # 攻撃力
        self.defence = defence  # 防御力
        self.agillity = agillity  # 素早さ
        self.intelligence = intelligence  # 賢さ
        self.name = name  # キャラクター名

    # ステータス文字列を返す
    def get_status_s(self):
        return "[{}] HP:{}/{} ATK:{} DEF:{} AGI:{} INT:{}".format(
            self.name, self.hp, self.max_hp, self.attack, self.defence, self.agillity, self.intelligence)

    def action(self, target, action):

        # 攻撃
        if action == 0:

            # 攻撃力 - 防御力のダメージ計算
            damage = self.attack - target.defence
            draw_damage = damage  # ログ用

            # 相手の残りHPがダメージ量を下回っていたら、残りHPちょうどのダメージとする
            if target.hp < damage:
                damage = target.hp

            # ダメージを与える
            target.hp -= damage

            # 戦闘ログを返す
            return "{}は{}に{}のダメージを与えた".format(
                self.name, target.name, draw_damage)

        # 回復
        elif action == 1:

            # 回復量をINTの値とする
            heal_points = self.intelligence
            draw_heal_points = heal_points  # ログ用

            # 最大HPまで回復できるなら、最大HP - 現在のHPを回復量とする
            if self.hp + heal_points > self.max_hp:
                heal_points = self.max_hp - self.hp

            # 回復
            self.hp += heal_points

            # 戦闘ログを返す
            return "{}はHPを{}回復した".format(
                self.name, draw_heal_points)


class GameState(Enum):

    """ ゲーム状態管理クラス"""
    TURN_START = auto()      # ターン開始
    COMMAND_SELECT = auto()  # コマンド選択
    TURN_NOW = auto()        # ターン中（各キャラ行動）
    TURN_END = auto()        # ターン終了
    GAME_END = auto()        # ゲーム終了


class Game():

    """ ゲーム本体"""

    HERO_MAX_HP = 20
    MAOU_MAX_HP = 50

    def __init__(self):

        # キャラクターを生成
        self.hero = Character(
            Game.HERO_MAX_HP, Game.HERO_MAX_HP, 4, 1, 5, 7, "勇者")

        self.maou = Character(
            Game.MAOU_MAX_HP, Game.MAOU_MAX_HP, 5, 2, 6, 3, "魔王")

        # キャラクターリストに追加
        self.characters = []
        self.characters.append(self.hero)
        self.characters.append(self.maou)

        # 状態遷移用の変数を定義
        self.game_state = GameState.TURN_START

        # ターン数
        self.turn = 1

        # 戦闘ログを保存するための文字列
        self.log = ""

    # 1ターン毎にゲームを進める
    def step(self, action):

        # メインループ
        while (True):
            if self.game_state == GameState.TURN_START:
                self.__turn_start()
            elif self.game_state == GameState.COMMAND_SELECT:
                self.__command_select(action)  # 行動を渡す
            elif self.game_state == GameState.TURN_NOW:
                self.__turn_now()
            elif self.game_state == GameState.TURN_END:
                self.__turn_end()
                break  # ターン終了でもループを抜ける
            elif self.game_state == GameState.GAME_END:
                self.__game_end()
                break

        # ゲームが終了したかどうか
        done = False
        if self.game_state == GameState.GAME_END:
            done = True

        # 「状態s、報酬r、ゲームエンドかどうか」を返す
        return (self.hero.hp, self.maou.hp), self.reward, done

    # ゲームを1ターン目の状態に初期化
    def reset(self):
        self.__init__()
        return (self.hero.hp, self.maou.hp)

    # 戦闘ログを描画
    def draw(self):
        print(self.log, end="")

    def __turn_start(self):

        # 状態遷移
        self.game_state = GameState.COMMAND_SELECT

        # ログを初期化
        self.log = ""

        # 描画
        s = " *** ターン" + str(self.turn) + " ***"
        self.__save_log("\033[36m{}\033[0m".format(s))
        self.__save_log(self.hero.get_status_s())
        self.__save_log(self.maou.get_status_s())

    def __command_select(self, action):

        # 行動選択
        self.action = action

        # キャラクターを乱数0.5〜1.5の素早さ順にソートし、キューに格納
        self.character_que = deque(sorted(self.characters,
                                          key=lambda c: c.agillity*random.uniform(0.5, 1.5)))

        # 状態遷移
        self.game_state = GameState.TURN_NOW

        # ログ保存
        self.__save_log("コマンド選択 -> " + Character.ACTIONS[self.action])

    def __turn_now(self):

        # キャラクターキューから逐次行動
        if len(self.character_que) > 0:
            now_character = self.character_que.popleft()
            if now_character is self.hero:
                s = now_character.action(self.maou, self.action)
            elif now_character is self.maou:
                s = now_character.action(self.hero, action=0)  # 魔王は常に攻撃

            # ログを保存
            self.__save_log(s)

        # HPが0以下ならゲームエンド
        for c in self.characters:
            if c.hp <= 0:
                self.game_state = GameState.GAME_END
                return

        # 全員行動終了したらターンエンド
        if len(self.character_que) == 0:
            self.game_state = GameState.TURN_END
            return

    def __turn_end(self):

        # 報酬を設定
        self.reward = 0

        # キャラクターキューの初期化
        self.character_que = deque()

        # ターン経過
        self.turn += 1

        # 状態遷移
        self.game_state = GameState.TURN_START

    def __game_end(self):

        if self.hero.hp <= 0:
            self.__save_log("\033[31m{}\033[0m".format("勇者は死んでしまった"))
            self.reward = -1  # 報酬を設定
        elif self.maou.hp <= 0:
            self.__save_log("\033[32m{}\033[0m".format("魔王をやっつけた"))
            self.reward = 1  # 報酬を設定

        self.__save_log("-----ゲームエンド-----")

    def __save_log(self, s):
        self.log += s + "\n"
