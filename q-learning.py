import random
import numpy as np
import dq_battle
from collections import defaultdict
import matplotlib.pyplot as plt

DIV_N = 10


class Agent:
    """エージェントクラス"""

    def __init__(self, epsilon=0.2):
        self.epsilon = epsilon
        self.Q = []

    # 方策をε-greedy法で定義
    def policy(self, s, actions):

        if np.random.random() < self.epsilon:

            # epsilonの確率でランダムに行動
            return np.random.randint(len(actions))

        else:

            # （Qに状態sが含まれており、かつそのときの状態におけるQ値が0でなければ）
            if s in self.Q and sum(self.Q[s]) != 0:

                # Q値が最大となるように行動
                return np.argmax(self.Q[s])
            else:
                return np.random.randint(len(actions))

    # 状態を数値に変換する
    def digitize_state(self, s):

        hero_hp, maou_hp = s

        # 勇者と魔王のHPをそれぞれDIV_Nで分割する
        s_digitize = [np.digitize(hero_hp, np.linspace(0, dq_battle.Game.HERO_MAX_HP, DIV_N + 1)[1:-1]),
                      np.digitize(maou_hp, np.linspace(0, dq_battle.Game.MAOU_MAX_HP, DIV_N + 1)[1:-1])]

        # DIV_Nの2乗までの状態数を返す
        return s_digitize[0] + s_digitize[1]*DIV_N

    # Q学習をする
    def learn(self, env, actions, episode_count=1000, gamma=0.9, learning_rate=0.1):

        self.Q = defaultdict(lambda: [0] * len(actions))

        # episode_countの分だけバトルする
        for e in range(episode_count):

            # ゲーム環境をリセット
            tmp_s = env.reset()

            # 現在の状態を数値に変換
            s = self.digitize_state(tmp_s)

            done = False

            # ゲームエンドになるまで行動を繰り返す
            while not done:

                # ε-greedy方策に従って行動を選択
                a = self.policy(s, actions)

                # ゲームを1ターン進め、その時の「状態、報酬、ゲームエンドかどうか」を返す
                tmp_s, reward, done = env.step(a)

                # 状態を数値に変換
                n_state = self.digitize_state(tmp_s)

                # 行動aによって得られた価値(gain) = 即時報酬 + 時間割引率 * 次の状態における最大のQ値
                gain = reward + gamma * max(self.Q[n_state])

                # 現在推測している（学習する前の）Q値
                estimated = self.Q[s][a]

                # 現在の推測値と、行動aを実行してみたときの実際の価値をもとに、Q値を更新
                self.Q[s][a] += learning_rate * (gain - estimated)

                # 現在の状態を次の状態へ
                s = n_state

    # テストバトル
    def test_run(self, env, actions, draw=True, episode_count=1000):

        turn_num = 0  # 撃破ターン数
        win_num = 0  # 勝数

        # episode_countの分だけバトルする
        for e in range(episode_count):

            tmp_s = env.reset()
            s = self.digitize_state(tmp_s)

            done = False

            while not done:
                a = self.policy(s, actions)
                n_state, _, done = env.step(a)
                s = self.digitize_state(n_state)
                if draw:
                    env.draw()  # バトルログを描画

            if env.maou.hp <= 0:
                win_num += 1
                turn_num += env.turn

        # 平均勝率・平均撃破ターン数を出力
        if not win_num == 0:
            print("平均勝率{:.2f}%".format(win_num*100/episode_count))
            print("平均撃破ターン数:{:.2f}".format(turn_num / win_num))
        else:
            print("平均勝率0%")


if __name__ == "__main__":

    game = dq_battle.Game()
    agent = Agent()

    actions = dq_battle.Character.ACTIONS

    """ 完全ランダムでバトル """
    agent.epsilon = 1.0
    agent.test_run(game, actions, episode_count=1000)

    """ Q学習する """
    agent.epsilon = 0.2
    agent.learn(game, actions, episode_count=1000)

    # Q値を出力
    # x = np.arange(50, 60)  # 適当な状態をプロットしてみる

    # for s in x:
    #     print("状態{:0=2}：{}".format(s, agent.Q[s]))

    # y = np.array([agent.Q[s] for s in x])
    # _, ax = plt.subplots(facecolor="w")
    # ax.set_xticks(x)
    # plt.xlabel("state")
    # plt.ylabel("Q-value")
    # plt.plot(x, y[:, 0], label="attack")
    # plt.plot(x, y[:, 1], label="heal")
    # plt.legend()
    # plt.show()

    """ テストバトル """
    agent.epsilon = 0
    agent.test_run(game, actions, episode_count=1000)
