# openagents-game-demo

OpenAgents 端到端演示：由 OpenAgents 多 agent 自主实现一个可运行的小游戏。

## 贪吃蛇（命令行 · Python 标准库 · curses TUI）

纯 Python 标准库实现的终端贪吃蛇。规则内核 `snake_game.py` 与终端 I/O 外壳
`snake.py` 解耦：内核不 import curses、随机源可注入，便于 `pytest` 确定性覆盖；
入口只负责读键、按节拍推进、渲染。零第三方依赖。

### 运行

```bash
python snake.py
```

在类 Unix 终端（macOS / Linux）真实 tty 下运行即开始。原生 Windows 无 `curses`，
请用 WSL。非终端环境（无 tty）会打印友好提示而非崩溃回溯。

### 按键

| 按键 | 作用 |
|------|------|
| `↑ ↓ ← →` 或 `W A S D`（大小写均可） | 转向 |
| `q` / `Q` | 退出 |

### 玩法规则

- 蛇按当前方向定时前进一格。
- 吃到食物 `*` → 身体变长一节、得分 +1，并在空格随机刷新新食物。
- 撞墙（越过边框）或撞到自身 → 游戏结束，清屏显示 `Game Over` 与最终得分，按任意键退出。
- 反向保护：正在向右时按「左」（正相反方向）会被忽略，避免瞬间掉头撞进自己。

### 跑测试

```bash
pip install pytest ruff        # 一次性安装开发依赖
pytest tests/test_snake_game.py   # 内核单测：移动/转向/反向/吃食物/碰撞/食物避身
ruff check .                       # 代码风格检查
```

### 离线端到端验证

```bash
bash scripts/e2e-spec-0001-snake-cli-game.sh
```

聚合离线验证：`ruff check` + `pytest` + 对 `snake.py` 的 grep 锚点（`curses.wrapper`、
方向键/WASD 映射、`__main__` 入口）。退出码 0 视为离线段通过。

### 人工终端验证清单

`curses` 交互层需真实 tty，无法在无头 CI 稳定驱动，请在本地终端手动验证：

1. `python snake.py` 直接进入游戏，出现带边框网格、蛇与食物 `*`、底部 `Score: 0`。
2. 方向键 `↑↓←→` 与 `W A S D` 均能控向；蛇不会因按反向键而瞬间掉头。
3. 吃到食物后蛇变长、`Score` 递增、食物在新位置刷新。
4. 撞墙或撞自身后清屏显示 `Game Over` 与 `Final score: N`，按任意键退出。
5. `q` 随时退出并恢复终端。
