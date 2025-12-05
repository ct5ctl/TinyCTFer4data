## 使用方法

1. 下载沙盒镜像：

   ```bash
   docker pull ghcr.io/l3yx/sandbox:latest
   docker tag ghcr.io/l3yx/sandbox:latest l3yx/sandbox:latest
   
   # 或者使用加速地址:
   # docker pull ghcr.nju.edu.cn/l3yx/sandbox:latest
   # docker tag ghcr.nju.edu.cn/l3yx/sandbox:latest l3yx/sandbox:latest
   ```

2. 创建.env文件并填入LLM Key：

   ```
   cp .env.example .env
   ```

   这里可以使用任意厂商的anthropic兼容api

3. 指定CTF题目地址和工作目录，启动：

   ```bash
   uv run --env-file .env main.py --ctf http://fe18cdc6-2916-439e-8bce-74e9a2ef7563.node5.buuoj.cn:81 --workspace workspace
   ```

​	测试题目是：https://buuoj.cn/challenges#BUU%20XXE%20COURSE%201

​	这个版本默认开启 VNC 服务，可以直观查看解题步骤。（比赛时是多容器并行，为节省性能不开UI）

​	目前设定的 Claude Code Subagent 写的比较耦合，只能用于解CTF，且唯一目标就是找到 flag。后面如果发布正式的版本会支持自定义的安全测试任务甚至通用任务。

![image-20251205040854944](./README/image-20251205040854944.png)

![image-20251205041013949](./README/image-20251205041013949.png)



## 备注

比赛时的调度和运行代码是我和 AI 混合编写的，包含任务并行，题目优先排序，多次失败后提示词动态变换，Hint获取策略等，代码很杂乱，这个仓库的代码是我将核心部分单独抽离出来的版本。

这个版本的代码也比较潦草，最近确实没有时间好好整理，但又不能一直不公开源码，所以先简单梳理了一下，后续可能会重构一下，开源一个正式的项目。

