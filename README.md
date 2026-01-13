[![badge](./README/badge.png)](https://zc.tencent.com/competition/competitionHackathon?code=cha004)

## 介绍

腾讯云黑客松-智能渗透挑战赛 **第 4 名** 核心代码。

文章：https://mp.weixin.qq.com/s/jT4poWZ4Gfu3faXvul07HA

PPT：https://wiki.chainreactors.red/blog/2025/12/01/intent_is_all_you_need/

演讲视频：https://www.bilibili.com/video/BV1z12eBkETz

比赛详情以及其他队伍资料：https://zc.tencent.com/competition/competitionHackathon?code=cha004



## 使用方法

1. 下载沙盒镜像：

   ```bash
   docker pull ghcr.io/l3yx/sandbox:latest
   docker tag ghcr.io/l3yx/sandbox:latest l3yx/sandbox:latest
   
   # 或者使用加速地址:
   # docker pull ghcr.nju.edu.cn/l3yx/sandbox:latest
   # docker tag ghcr.nju.edu.cn/l3yx/sandbox:latest l3yx/sandbox:latest
   ```

2. 创建.env文件并填入LLM Key（这里可以使用任意厂商的 Anthropic 兼容 api ）：

   ```
   cp .env.example .env
   ```

   可选：如果需要使用代理，可以在 `.env` 文件中添加：
   ```
   PROXY_HOST=192.168.121.171
   PROXY_PORT=7890
   ```
   或者在命令行中使用 `--proxy-host` 和 `--proxy-port` 参数。

   可以提前使用以下命令进入容器检查 api 和 key 的可用性，如果不可用的话直接启动 tinyctfer.py 会无响应很久（Claude Code 设计问题，会一直重试连接）

   ```
   docker run --rm -ti --entrypoint bash l3yx/sandbox:latest
   
   ANTHROPIC_MODEL=GLM-4.6 ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic ANTHROPIC_AUTH_TOKEN=xxx claude hello
   ```
   
   如果需要测试代理，可以在容器内设置代理环境变量：
   ```
   export http_proxy="http://192.168.121.171:7890"
   export https_proxy="http://192.168.121.171:7890"
   export GIT_SSH_COMMAND="ssh -o ProxyCommand='nc -x 192.168.121.171:7890 %h %p'"
   ```

3. 指定CTF题目地址和工作目录，启动：

   ```bash
   uv run --env-file .env tinyctfer.py --ctf http://821dd238-6bbe-4d44-8294-82ff25743b70.node5.buuoj.cn:81 --workspace workspace
   ```
   
   如果需要使用代理，可以：
   - 在 `.env` 文件中设置 `PROXY_HOST` 和 `PROXY_PORT`
   - 或使用命令行参数：`--proxy-host 192.168.121.171 --proxy-port 7890`
   
   示例：
   ```bash
   uv run --env-file .env tinyctfer.py \
     --ctf http://821dd238-6bbe-4d44-8294-82ff25743b70.node5.buuoj.cn:81 \
     --workspace workspace \
     --proxy-host 192.168.121.171 \
     --proxy-port 7890
   ```

​	测试题目是：https://buuoj.cn/challenges#BUU%20XXE%20COURSE%201

​	这个版本默认开启 VNC 服务，可以直观查看解题步骤。（比赛时是多容器并行，为节省性能不开UI）

​	目前设定的 Claude Code SubAgent 比较耦合，只能用于解CTF，且唯一目标就是找到 flag。后面如果发布正式的版本会支持自定义的安全测试任务甚至通用任务。

## 步骤级日志记录

系统会自动记录渗透测试过程中的每一步操作，日志保存在 `workspace/logs/steps.jsonl`。

### 日志格式

每条日志记录包含以下字段：
- `ts`: UTC 时间戳
- `tag`: 分类标签（`code_execution`, `terminal`, `planning` 等）
- `thought`: AI 的思考/规划（需要 AI 主动记录）
- `action`: 执行的操作摘要（代码摘要、命令等）
- `observation`: 观测到的结果/输出

### 自动记录的内容

1. **代码执行**：每次通过 `mcp__sandbox__execute_code` 执行代码时，自动记录：
   - `action`: 代码摘要（提取代码的第一行或关键部分）
   - `observation`: 执行输出（stdout、返回值、错误信息等）
   - `execution_time_seconds`: 执行时间
   - `has_error`: 是否有错误

2. **终端操作**：每次使用 `toolset.terminal` 时，自动记录：
   - `action`: 执行的命令
   - `observation`: 命令输出

### 手动记录规划

AI 会在执行代码前主动记录规划（通过 `toolset.logger.log_step()`），包含：
- `thought`: 为什么这么做
- `action`: 准备做什么
- `observation`: 执行后的结果

### 查看日志

```bash
# 查看所有日志
cat workspace/logs/steps.jsonl | jq .

# 只看代码执行日志
cat workspace/logs/steps.jsonl | jq 'select(.tag == "code_execution")'

# 只看规划日志
cat workspace/logs/steps.jsonl | jq 'select(.tag == "planning")'
```

### 禁用日志

设置环境变量 `DISABLE_STEP_LOG=1` 可以禁用自动日志记录。

![image-20251205040854944](./README/image-20251205040854944.png)

![image-20251205041013949](./README/image-20251205041013949.png)



## 其他

比赛时的调度和运行代码是我和 AI 混合编写的，包含任务并行，题目优先排序，多次失败后提示词动态变换，hint 获取策略，LLM 和 Agent switch 机制等，代码很杂乱，这个仓库的代码是我将核心部分单独抽离出来的版本，方便大家复现和学习。但是代码也比较潦草，最近确实没有时间好好整理，但又不能一直不开源，所以先简单梳理了一下，后续可能会重构，开源一个正式的项目。

赛前写的很匆忙，这个项目中对 Meta-Tooling 的实现还有非常大的优化空间，欢迎各位大佬一起来交流讨论。
