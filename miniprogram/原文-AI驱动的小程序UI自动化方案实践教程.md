# AI驱动的小程序 UI自动化方案实践教程

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年07月22日 08:00
> - 原文链接：<https://articles.zsxq.com/id_ce8e094e4o0x.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文；代码块按原文内容复原）

---

## 本文诉求

之前我们分享过 app、web、桌面端的 UI 自动化，然后也有不少伙伴们希望能出一套微信小程序的 UI 自动化方案，因此我这边去调研了多种方案，

miniprogram-automator、Minium、Airtest+Poco、Appium、XCUITest，但是发现官方的 miniprogram-automator 框架具备更大的优势，微信官方 miniprogram-automator 深度适配小程序底层，可直接操控逻辑层与自定义组件、原生 mock 小程序 API，依托开发者工具无需真机，易接入前端测试框架与 CI 流水线，适配小程序全场景自动化。

因此本文则基于 miniprogram-automator 设计 skill，分享下 Skill 原理和整体实践方案

## 概念介绍

### 什么是 miniprogram-automator

**一、基础定义**

miniprogram-automator 是微信官方出品的小程序 E2E 自动化测试 SDK，发布在 npm 官方包，专门通过 Node.js 脚本远程操控「微信开发者工具」，自动模拟用户操作、校验页面逻辑，实现小程序全流程自动化回归测试。简单理解：用代码代替人工手动点小程序，做自动化功能测试。

**二、核心原理**

- 微信开发者工具开启 CLI/HTTP 调用、自动化端口（默认 9420）；
- Node 脚本通过 WebSocket 连接工具内部协议；
- SDK 下发指令：打开项目、跳转页面、点击、输入、获取数据、Mock 接口、截图；
- 脚本可搭配 Jest/Mocha 等测试框架做断言，输出测试报告

### 什么是 Jest

Jest 是 Facebook 开源、面向 JavaScript/TypeScript 的一站式测试框架，最常用于 Vue、React、小程序、Node.js 项目，用来写自动化测试用例。

简单介绍：

miniprogram-automator 负责操控小程序模拟器点页面，Jest 负责管理用例、写断言、统计测试结果、生成报告，二者经常搭配使用做小程序 E2E 自动化。

## skill 原理

![skill原理](https://article-images.zsxq.com/FlV5Lcro7fVQBMyqf0zSl6VdeExD)

Skill 包下载：<https://mxhjscggz8q.feishu.cn/wiki/TVTNwINMPiWffckZxGacIsTdncd?from=from_copylink>

## 微信开发者工具安装和使用

在执行微信小程序 UI 自动化中，我们使用微信小程序的模拟器，也就是官方所提供的微信开发者工具

### 1、安装包下载

点击网页 <https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html>

选择你的系统版本，点击下载

![下载页](https://article-images.zsxq.com/Fnc6V9rnuA3AmSTOnS6otozhEwrn)

安装后打开程序

### 2、导入项目

这里可能需要获取到微信小程序的源码，需要和开发申请权限，我这边后续也会整理提供出一个公寓系统的微信小程序源码，供大家学习和使用，然后使用 git clone 拉取到本地

点击「+」

![点击+](https://article-images.zsxq.com/FiqALjyz_U34FNhJY8GCvW7qcxIe)

填写相应的信息，点击创建

![填写信息](https://article-images.zsxq.com/Fnmb56O9WEvL4NZknVNnRkIbaI5O)

点击信任并运行

![信任并运行](https://article-images.zsxq.com/FktPxbPWFAyGaXRAtEsExGF6J0zC)

等待编译，编译后就启动起来了，可以看到右侧的信息

![等待编译](https://article-images.zsxq.com/FthQGmTYCx0JVwXocUOyVI1LUnJf)

### 3、打开服务端口

找到设置，点击安全设置

![安全设置](https://article-images.zsxq.com/FkS3zTKKGc4IOBtExMi6u7jJAMoK)

点击「开启服务端口」和「自动化接口打开工具时默认信任项目」

![开启服务端口](https://article-images.zsxq.com/FqKGkyuOhQ6QotDTj9TO9WvcGJE0)

## 实践操作

本篇文章的案例，是让 skill 去基于小程序进行 UI 自动化的脚本编写和执行

小程序是公寓系统客户端，包含登录，我的房间、个人信息、工单的模块，算是一个比较常见的场景了

### 1、skill 导入

Skill 包下载：<https://mxhjscggz8q.feishu.cn/wiki/TVTNwINMPiWffckZxGacIsTdncd?from=from_copylink>

下载 Skill 包，解压到 AI 工具的 Skill 目录下，例如：`.claude/skills/`

![skill导入](https://article-images.zsxq.com/Fk3XIXtB3hV_DegQeXx2mDggdn3F)

### 2、探索 & 脚本编写

输入规则：`/miniprogram-script-author` 测试用例文件 项目地址 其他信息

输入：

![输入示例](https://article-images.zsxq.com/FtQFkd7fGnWfSDWBkrbkpZe1EL1B)

这里的用例就是我们常规中编写的测试用例

![测试用例](https://article-images.zsxq.com/FrRKoKNXoqTwLUmYVaL3QCAgBAY5)

**AI 执行过程**

在执行过程中，将 excel 中的用例进行页面探索，采集 meta.json 和 wxml

![页面探索采集](https://article-images.zsxq.com/FrIga4F1Nl19Kdupmzq6DWBaD0K6)

检索到相关的元素之后，会生成 spec.js 代码

![生成spec代码](https://article-images.zsxq.com/FtDdO71BVWljxdkq8SNl5pu4MyM9)

生成不同模块的代码

![生成模块代码](https://article-images.zsxq.com/Fjuk-1HvFW9QPl2kMiX-qqEQdixK)

### 3、脚本执行

输入：

![脚本执行输入](https://article-images.zsxq.com/FrzA9PH0pjcEQvi_Alqf-3QnRMWR)

执行之后，则会唤起微信开发者工具，在模拟器中进行操作

在执行之后，会直接唤起一个 html，记录执行的报告结果

![HTML执行报告](https://article-images.zsxq.com/FvSPNM-3ezCUix80NUQBh7K8VB2L)

但是 automator 不支持直接录制 video 和 trace，因此使用的是伪 trace，将脚本中执行的步骤和相关的图片进行截图

![伪trace](https://article-images.zsxq.com/FoLagc9MLb9ZgD1dm4vs1q7jjRAp)

默认不开启视频录制，如果需要的话，可以让 AI 开启，使用 ffmpeg 的方式进行录制

### 4、报错脚本修复

AI 会对执行失败的脚本，输出原因，如下：

![失败原因输出](https://article-images.zsxq.com/Fvb_sY0OCQUn8s9wVnbYZ21LYU98)

可以根据 AI 输出的失败原因进行修改，修改后重跑即可

## 是否支持手动执行

在实际的 UI 自动化使用中，我们都期望脚本可以进行复用，那么使用 jest 脚本的目的，就是便于我们进行重复执行，那么要如何执行呢？

**方式一：用现成执行脚本（带报告）**

脚本在 skill 目录里，但本身就是 bash，不依赖 Cursor：

下面的 `.cursor/skills` 需要切换为你的目录

```bash
# 按 suite.json 逐条跑全部用例（含报告、artifacts、伪 Trace）
bash .cursor/skills/miniprogram-run/run-with-reports.sh suite

# 从某条续跑
bash .cursor/skills/miniprogram-run/run-with-reports.sh suite --from TC-MP-003

# 跑某个模块文件里的全部 describe
bash .cursor/skills/miniprogram-run/run-with-reports.sh single miniprogram/tests/auth/auth.spec.js
```

如下：

![bash执行](https://article-images.zsxq.com/FgHd71-f82RJ4tANsCGRjx10oUQc)

**方式二：直接用 Jest（不写台账/批量报告）**

方式二不会输出报告，因此建议还是使用方式一的方式去执行

```bash
# 跑整模块文件
npx jest miniprogram/tests/auth/auth.spec.js --runInBand

# 只跑某一条（describe 名以用例 ID 开头）
npx jest miniprogram/tests/auth/auth.spec.js --runInBand --testNamePattern='TC-MP-001'

# 或用 npm script（等同 jest --runInBand）
npm test -- miniprogram/tests/home/home.spec.js --testNamePattern='TC-MP-003'
```

## 问题

### 版本问题

如果说在执行的过程中，稳定版本一直失效，没有唤起模拟器和执行操作的话

则要下载高一些的版本，开发版

<https://developers.weixin.qq.com/miniprogram/dev/devtools/log.html#nightly-2.02.2607162>

### 微信小程序官方也出了一套 skill，为什么不直接拿来用？

可以看到下面的链接，微信小程序官方也出了一套 skill

<https://developers.weixin.qq.com/miniprogram/dev/devtools/Skills.html>

官方的 skill 比较适用于进行单次模拟操作，没法生成代码的方式，重复执行，因此还是采用才出 jest 代码的方式

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为本目录三件套与文章所述版本的对照：

- 文中两个技能（script-author 写脚本、run 执行）即本目录 `miniprogram-script-author` / `miniprogram-run`；本仓库另拆出 `miniprogram-shared` 共享层（conventions/selectors/脚手架模板）。
- 本仓库版本的关键强化：**WXML inspect 是选择器唯一依据**（禁止仅凭 Excel 写 `page.$()`）、**suite.json 唯一编排源**（`--testNamePattern` 按 id 命中 describe）、一模块一文件、会话复用（`ensureLoggedIn`/`forceLogin`）、script-author 不执行不下结论。
- 文中提到的「默认不开启视频录制，需要时用 ffmpeg」与本仓库一致：伪 Trace 为默认证据链（automator 不支持 Playwright video/trace.zip）。
- 使用说明见同目录 [使用说明.md](使用说明.md)。
