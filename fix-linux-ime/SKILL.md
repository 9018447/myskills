---
name: fix-linux-ime
description: 诊断修复 Linux 桌面(X11)中文/日文等输入法在特定应用中失效的问题(候选框不出现、上屏丢失)。当用户报告"某应用无法输入中文/输入法不工作/候选词上屏失败"时使用。
tags: [user]
---

# 修复 Linux(X11)输入法在特定应用中失效

目标:让输入法在报障的应用里恢复输入。不是重建整个输入法环境。

实践是检验真理的唯一标准:以下规则来自 2026-09-21 一次成功排查(Warp winit 应用 + fcitx5 + Cinnamon/X11),每条都可复验;与新证据冲突时以实测为准。

## Fact(已确认的事实)

- GTK/Qt 应用走 D-Bus 输入法前端(fcitx5-frontend-gtk/qt),自绘应用(如 Warp 的 winit、alacritty、Java、部分 Electron)走 XIM 协议或各自的 IM 接口。**"其他应用正常、唯独某应用失效"说明框架在跑,问题在协议/环境/locale,而不是输入法本体。**
- XIM 的 commit 依赖 Xlib locale:`XSupportsLocale()` 失败时 commit 文本会被**静默丢弃**(无报错)。
- winit 系应用的 commit 只经 `Xutf8LookupString` 一条路;fcitx5 on-the-spot 模式发异步 XIM_COMMIT,可能接不住。两者任一断裂,症状都是"候选框出现、空格后文本消失"。
- Xlib locale 数据由 `libx11-data`(Debian/Ubuntu)提供,包"已安装"不代表文件完整——可用 `dpkg -V <pkg>` 验证。

## 流程(按执行顺序)

### 1. 建立现状事实

```bash
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"        # Wayland 会话不在本 skill 范围
ps -ef | grep -iE 'fcitx|ibus' | grep -v grep     # 实际在跑哪个框架
env | grep -E 'IM_MODULE|XMODIFIERS'              # 会话声明的框架
locale                                            # LANG/LC_CTYPE 是否为 *.UTF-8
```

**完成条件:** 确认"实际运行的框架"与"环境变量指向的框架"是否一致,以及报障应用是用什么 UI 工具包写的(winit/GTK/Qt/Electron)。

不一致 → 修环境变量(见 4a)。一致 → 进入第 2 步。

### 2. 分层验证,先外层后内层

每层验证都产生判别力,不要跳层:

1. **框架层**:在其他应用(GTK 应用即可)里确认输入法可用。不可用 → 问题在框架/会话环境,不在这个应用。
2. **Xlib locale 层**(XIM 应用失效必查):
   ```bash
   ls /usr/share/X11/locale/zh_CN.UTF-8/   # 必须有 XLC_LOCALE 文件,只有 Compose 是损坏
   dpkg -V libx11-data | grep missing      # 列出被删文件;多即重装
   ```
   损坏 → `sudo apt install --reinstall libx11-data`(Debian 系;其他发行版找对应的 xorg-x11-x11-data 类包),重验 `ls` 看到 XLC_LOCALE。
3. **应用↔XIM 层**:用最小 XIM 测试客户端(`references/ximtest.c`)直接验证 XIM 全链路:
   ```bash
   gcc -o /tmp/ximtest references/ximtest.c -lX11
   # 需要用户在弹出的窗口里:Ctrl+Space、打拼音、按空格
   ```
   看输出:`XSupportsLocale FAILED` → 回到第 2 层;`XOpenIM FAILED` → 检查 XMODIFIERS 与 IM 框架;按键后打印出 UTF-8 commit 文本 → XIM 链路是好的,问题在该应用自己的实现(查该应用仓库 issue/源码);收不到 commit → 看第 3 步。

**完成条件:** 定位到唯一断裂层,并有一层验证输出支持该判断。

### 3. 对照症状与已知断裂点

| 症状 | 已知断裂点 | 修复 |
|---|---|---|
| 候选框能出、空格上屏丢失 | Xlib locale 损坏,或 on-the-spot 异步 commit 接不住 | 重装 libx11-data;或 `~/.config/fcitx5/conf/xim.conf` 写 `UseOnTheSpot=False` 后 `fcitx5-remote -r` |
| Ctrl+Space 唤不醒输入法 | XMODIFIERS 指向未运行的框架 | 见 4a |
| 只有一个应用失效且 XIM 测试客户端正常 | 该应用自身 IME 实现 bug | 查上游 issue 与源码,不要继续改系统配置 |

修改 fcitx5 配置后必须 `fcitx5-remote -r`(或重启 fcitx5)并**重启报障应用**再验证——XIC 的样式在应用建窗时协商。

### 4. 持久化与收尾

a. 框架指向修正:`im-config -n fcitx5`(或 ibus),**必须注销重登**才对全会话生效。临时验证可用单次环境变量启动应用:`XMODIFIERS=@im=fcitx GTK_IM_MODULE=fcitx <app>`。

b. 询问用户是否需要保留调试产物;清理临时进程和测试窗口。

**完成条件:** 用户在报障应用中实际输入中文成功,且确认持久化方案(重登后环境变量正确)。

## Invariant

- 修改任何系统配置前,先向用户说明并征得同意;需要 sudo 的命令交给用户执行,不代跑。
- 一次只改一层变量。改了配置必须重启相关进程再验证;禁止在同一轮里叠加多个未验证的修改。

## Default

- 优先怀疑顺序:环境变量指向 → Xlib locale 完整性 → XIM 模式协商 → 应用自身 bug。前三者可由命令直查,最后一个才需要读源码。
- 日志用 `systemd-run --user --unit=<名>` 跑 fcitx5(`--verbose '*=5'`,`journalctl --user -u <名>` 查看),前台管道方式会被 Claude 沙箱回收,日志会断。

## Unknown(不要猜,去查)

- Wayland 会话的输入法走 text-input 协议,与本 skill 的 XIM 路径完全不同——先确认会话类型再套用。
- 该应用具体用哪个 IME 接口(winit 版本、是否 fork 过、有无私有 IM 实现)决定第 3 步结论,需查其依赖树。
- 其他发行版的 locale 数据包名不同,用 `dpkg -S /usr/share/X11/locale/locale.dir` 确认属主。
