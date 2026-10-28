# 【TesterArmy e2e】基础认识+自动化实践案例

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年10月26日 07:50
> - 原文链接：<https://articles.zsxq.com/id_j2ccp6n8j3lc.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文）

最近 TesterArmy 在测试圈热度挺高的，但是细看网上的文章，又没太多的实践，大部分是基于官方的说明文，让AI修饰一遍就发布了，没法实际看出效果究竟是咋样。

网上跟风一多，就导致不少同学开始焦虑：这是不是又一门必须跟上的新技术？

因此我这边调研了一下，并结合真实案例进行了UI自动化测试的实践，这篇文章给大家分享下整体实践过程以及说说TesterArmy 的实际体验。

## 一、什么是testerArmy e2e？

TesterArmy e2e 是 TesterArmy 开源的 Agentic（AI 智能体）端到端测试框架，Web + iOS/Android 移动端统一支持，在github上，已经有一定数量的star。

![图片.png](https://article-images.zsxq.com/FlFopSUIlvn0N1-fZIj9wpWmII0C)

### 它有什么优势呢？

#### 1、 一套 API，同时覆盖 Web 和移动端

TesterArmy e2e 同时支持 Web、iOS 和 Android。Web 端底层使用 Playwright，移动端则通过统一接口操作模拟器。

这意味着，团队不需要分别维护 Playwright、Detox 等多套技术栈，就能用相近的方式编写和管理 Web、iOS、Android 自动化用例。

#### 2、传统自动化与 AI 操作可以混合使用

在同一条用例中，既可以使用 Playwright 的定位器和确定性断言，也可以通过 `agent.act()` 让 AI 完成页面操作。

两种方式可以根据场景灵活搭配：

- 页面稳定、需要精确校验的步骤，使用传统 Locator 和断言；
- 页面频繁改版、元素难以定位的步骤，交给 Agent 根据自然语言目标完成。

这样既保留了传统自动化的稳定性，也能减少复杂定位器带来的编写和维护成本。

如下：

![图片.png](https://article-images.zsxq.com/Fh-jyOi4dmEpeHO4GmoB_6ztBIrx)

- 这个是它比较重要的特点，用简单的话来解释，就是有稳定的元素，则用playwright去编写，如果对于一些复杂的场景，没法明确的元素，则让agent去识别界面，决策和操作。

#### 3. Agent 动作支持缓存重放

当 `agent.act()` 操作成功，并且后续断言验证通过后，e2e 会缓存这次操作。

下次执行相同用例时：

- 如果页面没有变化，直接回放缓存动作，不再调用大模型，从而减少 Token 消耗并提升执行速度；
- 如果页面发生变化、缓存无法继续使用，则自动交回 Agent，由 AI 重新识别并完成操作。

简单来说，它不会每次都调用 AI，也不会在页面变化后直接报错，而是在执行效率和页面适应能力之间做了平衡。

#### 4、能够自定义大模型

<!-- 存档注记：原文此小节仅有标题，无正文 -->

## 和browser use的区别

agent自主决策和进行页面操作，本身也并不稀奇，之前我们也分享过browser use，那么他们有什么区别呢？

| 对比项 | TesterArmy e2e | Browser Use |
|--------|----------------|-------------|
| 产品定位 | 端到端自动化测试框架 | 通用浏览器 Agent 工具 |
| 支持平台 | Web、iOS、Android | 以 Web 浏览器为主 |
| 操作方式 | 定位器、断言与 AI 操作可混合使用 | 主要由 AI 根据目标规划并执行 |
| 结果校验 | 支持确定性断言和 AI 判断 | 可使用代码或 AI 校验，需要自行组织测试结构 |
| 执行效率 | 已验证的 Agent 动作可以缓存重放 | 通常需要模型参与任务规划与执行 |
| 适用场景 | 回归测试、CI 检查、长期维护的自动化用例 | 网页探索、数据采集、一次性浏览器任务 |

## 二、Skill说明

为了让大家更快上手，我将其封装成了 5 个 Skill，覆盖环境初始化、用例生成、测试执行、报告生成和失败修复等环节。

### Skill介绍

| Skill 名称 | 主要作用 |
|------------|---------|
| e2e-init | 初始化 e2e 环境，选择 Web 或移动端，配置测试引擎、模型及相关参数 |
| e2e-explore-draft | 根据需求、测试用例或 URL 探索页面，生成 .e2e.ts 测试脚本初稿 |
| e2e-run | 运行指定测试，汇总执行结果并分析失败原因 |
| e2e-report | 读取 .e2e/report.json 等测试产物，生成 Markdown 和 HTML 报告 |
| e2e-fix | 根据失败报告和 Trace 定位问题，修复测试脚本或元素定位器 |

### Skill使用流程

![图片.png](https://article-images.zsxq.com/FkDTHK7YTaPLbQD2KCQCc-3zmWhC)

### Skill下载

下载地址：<https://my.feishu.cn/wiki/JuW2wB1c4iHAgTk5SCEc6lRbnCh>

## 三、操作步骤

### 1、初始化

testerarmy本身是需要进行环境配置的，如果手工去配置的话，相对还是比较麻烦的，且它所使用的模型是需要配置的，没法直接用AI工具（如：cursor）内置的大模型

因此我这里提供了一个Skill进行配置，减少繁琐的配置步骤

输入：

![图片.png](https://article-images.zsxq.com/Fhmz4th7HKtygBkoE86LbQwtFFYh)

AI会输出下面的内容给你做选择

- 首先是选择引擎，是web还是app
- 模型厂商

![图片.png](https://article-images.zsxq.com/FtTokSuUIp3aChSWY5OjLuH4_XRu)

回复案例：

- 这里我选择web、和deepseek作为案例

![图片.png](https://article-images.zsxq.com/Fu5O9-Wa3JOZh3wCph5Sz_Bx7vhr)

之后AI就会去执行testerarmy/e2e的初始化指令

![图片.png](https://article-images.zsxq.com/Fke8Pbz77bL6etbBzNCsHRbCHoi0)

生成下面的文件：

![图片.png](https://article-images.zsxq.com/FgNwxi9izk11GLybk8jfthGFwguM)

- e2e.config.ts：e2e的配置文件
- .env：环境配置文件

### 2、修改环境配置

这里需要手动去配置一下刚刚你所选择的apikey，例如下边我使用的deepseek，所以我需要在.env文件中配置deepseek apikey

![图片.png](https://article-images.zsxq.com/Fu0DN6FhJtb9vGHj2tcD9KmRoDKM)

### 3、界面探索

输入：

![图片.png](https://article-images.zsxq.com/FncG0eJb3ii1_LviSIH2RFPn8HhP)

这里我默认是有头的，因为如果是无头的话，不确定是否在执行，没法很好的看出效果

探索后，最终会产出相应的代码

![图片.png](https://article-images.zsxq.com/FqOJnuLLbAAaNK4hY7wVL1410o4z)

这里我们可以看看效果，产出的代码用的是ts

可以看到，它会获取稳定的标签定位器，如下是登录的账号和密码

![图片.png](https://article-images.zsxq.com/FrIvcPAttrC0msi6GY5FXUETYUsp)

对于不稳定的元素或者操作，则使用agent去做处理，可以看到，它将操作步骤用提示词写入，在执行的过程中，会去调用agent执行

![图片.png](https://article-images.zsxq.com/Fh-jyOi4dmEpeHO4GmoB_6ztBIrx)

### 4、执行脚本

这里有两种方式，一种是执行Skill，另外一种是直接执行命令

Skill的方式：

![图片.png](https://article-images.zsxq.com/Fo5LtwgAPSSUFCrWj9oAwmbK4vAp)

脚本的话，则在终端执行：

```bash
npm run test:e2e
```

如果是使用Skill去执行，会大概总结出成功和失败的用例，并且输出失败摘要

![图片.png](https://article-images.zsxq.com/FtuMOg25RHFgv7ddkV24doFJb7Li)

### 5、修复（非必选）

如果在会话中本身有失败的用例，或者用户直接提供失败的日志，那么可以执行下面的Skill

![图片.png](https://article-images.zsxq.com/FujLwlJv4j1wmNJ7SQ3bLQ-WH-Mu)

之后可以对代码进行修复

![图片.png](https://article-images.zsxq.com/FnYNnQq2M4BR_qYx7CBfLZxJm4ix)

### 6、报告生成

一般来说，在执行之后，就会自动生成一份报告，报告如下

![图片.png](https://article-images.zsxq.com/Fsqzuk_BrFETdmY1_kpWjJ95Yyf8)

也可以通过Skill去执行

![图片.png](https://article-images.zsxq.com/Fj9-fvpJvl0X2ASokD43dXYprKNK)

或者在终端中，执行脚本

```shell
npm run report:e2e
```

就会生成一份HTLM文件，可以直接打开

## 个人体验

### 不错的点

1、将稳定的元素用playwright脚本编写，不稳定的元素采用AI去执行，这是一个不错的思路，能够解决部分元素不稳定的场景

2、执行起来速度也还可以，不会特别慢

### 不足的点

1、使用门槛并不算低

TesterArmy e2e 并非零代码工具。虽然可以用自然语言描述操作，但测试脚本仍需手动或借助 AI 编写。遇到验证码、复杂判断等场景时，还要额外编写提示词和处理逻辑，后续维护也会更麻烦。

![图片.png](https://article-images.zsxq.com/Fkd_e907Y3YxA8im_W3ogLcTlTDH)

且我这边使用deepseek去识别验证码，失败率较高

2、agent执行的不稳定性

用例编写，采用的是自然语言，由agent自己决策，模型每轮决策不同，同一条用例执行不稳定。比 Playwright 固定定位器更容易失败

![图片.png](https://article-images.zsxq.com/Fk6HdnRXXN5c-1qGoxF5oS2YnyKz)

3、排查成本变高

排查失败原因更复杂， Playwright 失败大多是选择器、网络、超时；Agent 失败原因可能是：模型理解偏差、截图识别、页面时机、缓存匹配逻辑、模型限流超时，排障链路更长、更玄学。

4、早期版本

版本还在 0.x，API 不稳定 属于早期版本，小版本升级可能改配置、API、缓存规则，不适合直接把主干核心回归全量迁移上去，升级有改脚本成本

![图片.png](https://article-images.zsxq.com/FniQF6sNSdgWhReHIgkmflUFeYXg)

---

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任
