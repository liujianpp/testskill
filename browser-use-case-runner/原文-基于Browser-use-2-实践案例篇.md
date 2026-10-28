# 【基于Browser use】2. Browser use+Skill实现web UI自动化实践案例

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年05月06日 08:00
> - 原文链接：<https://articles.zsxq.com/id_0l9ah228ce6r.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文）

---

## 本文目的

这篇文章将通过一个项目案例带大家上手基于 Browser use 的 UI 自动化测试实战，以及分享该方案的整体实现思路和相关 Skill。

## 学习建议

1、上一篇文章，我们介绍了 Browser use 的相关基础概念，没了解过 Browser use 的同学可以先看下（<https://articles.zsxq.com/id_x29slsufdbwn.html>），再开始这篇文章的学习

2、建议借助能力较强的大模型辅助完成（我在实操中使用 Cursor 的 Auto 模式）

3、主要是提供一套 skill 框架和实现思路给大家，在实际工作环境中，大家的需求可能都不一样，可以先去实践看看，结合自己的情况去优化这套 skills，让它成为真正适用你需求的方案。

4、本案例在执行的过程中，由于不同的环境以及大模型能力的强弱，可能会有不一样的输出结果，因此大家在遇到问题的时候，优先对照日志和结合 ai 辅助排查；多记录踩坑点，后续复用在自己项目时会更加顺畅。

## browser-use-case-runner skill 介绍

该 skill 是我在 browser-use 的基础上进行改造，用于执行用户提供的用例，中间设置了不同维度的策略的新增，分别如下：

1、支持直接读取 Excel、md 文件等测试用例执行自动化

2、内置执行配置管理（单会话 / 多会话灵活切换）

3、简易验证码识别 / 图片识别、自动化执行

4、同时具备遇阻即停、智能分级处理机制：任务执行异常时先自动阻塞，优先由 AI 尝试智能修复，AI 无法处理时再转人工介入，大幅提升自动化稳定性与通过率，而不是一次性全部执行完，出现一堆阻塞和失败的用例

skill 内部执行逻辑：

![skill内部执行逻辑](https://article-images.zsxq.com/FpsKDPi7j7CKfqsBUDlaU4jWcj2T)

## 实战步骤

### 1、skill 下载与介绍

下载 skill 并解压到对应的 skill 目录下，如：.claude/skills 或者 .cursor/skills

<https://mxhjscggz8q.feishu.cn/wiki/Adz2wz4tginmuJkSzxBcduxGnqc?from=from_copylink>

Skills 介绍

![Skills介绍](https://article-images.zsxq.com/Fo92-VD1M7BGKQJpoV4BnJk-U3b4)

包含两个 Skills，分别是官方的 browser-use、以及我这边基于官方 browser-use 的基础上进行改造的 browser-use-case-runner（用例执行 skill）

### 2、用例准备

这里准备了常规的 excel 测试用例，可以是我们日常中手动编写的，也可以是使用 AI 生成测试用例

将用例文件放在根目录下

![用例文件放根目录](https://article-images.zsxq.com/FkE1ziBA0DcxNoVWO0EXLa0Z8nrG)

我这边使用的测试用例案例：

![测试用例案例](https://article-images.zsxq.com/FqrjhMmikMCmgB_H0o3-MizfX36b)

### 3、用例执行

输入：

`/ browser-use-case-runner` + `@excel用例文件`

项目地址、登录帐号密码等其他上下文信息

![执行输入示例](https://article-images.zsxq.com/Flcqps5Wni-br0PDNtR9wSEse4D7)

### AI 执行过程

1、基于 browser use 官方 skill 进行优化，支持抓取图片，并使用大模型进行识别

![抓取图片并用大模型识别](https://article-images.zsxq.com/Fsw5UCAoy0FaT4bAieyOe4D557EA)

2、在执行中，会生成一个配置文件

可用于配置下面这些信息

sessionStrategy：是否单会话，可用于复用登录态

videoRecording：是否支持录制，但是由于 browser-use 本身不支持 video 录制，只支持截图，因此这里暂时未扩展该能力，如果需要的话，可以配合第三方工具 ffmpeg 进行视频录制

![生成的配置文件](https://article-images.zsxq.com/FueUSk2hAlvO1Qf0m_ee57RtqlkB)

3、DOM 抓取和 UI 执行

Browser use 在执行的过程中，如果 DOM 发生了变更，则会抓取最新的 DOM 结构，对元素赋予唯一 ID，之后作为 AI 的上下文，由 AI 进行执行

![DOM抓取与UI执行-1](https://article-images.zsxq.com/FsNkI54aUuuzX14fqQRQdkQtEoTt)

![DOM抓取与UI执行-2](https://article-images.zsxq.com/Fv2FhxfVPWwba2z8PGICqkJh6Clv)

之后会对结果进行记录

![结果记录](https://article-images.zsxq.com/Fqc43i0QMnntIhlEsuy9YfMvKEUz)

4、最终输出报告

![最终输出报告](https://article-images.zsxq.com/Fu-FEGHpWeTvLD6jeCIqEwxSk-LH)

## 小结

Browser-use 具备自行快照探索、元素定位的能力封装，使得我们能够基于自然语言实现 UI 自动化，且不是通过视觉识别的方式，减低了 token 的消耗且提高了一定的速度，是一种不错的浏览器 UI 自动化的方式，推荐学习和使用。

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为当前仓库版本与文章所述版本的对照：

- 文章所述 videoRecording「因 browser-use 不支持视频录制暂未扩展，可配合 ffmpeg」——本仓库版本已扩展为完整约定：默认 `enabled=false`（方式 1 关键截图留痕），用户显式要求时走 ffmpeg 桌面级采集流程（仍非 browser-use 内置）。
- 文章所述配置文件即本仓库的**当轮 run-config**（`reports/run-config-<UTC>.json`）；仓库版进一步把 skill 目录 `runner-config.json` 明确为仅 `--defaults` 模板，当轮文件为唯一真源。
- 验证码处理在本仓库版细化为「截图落盘 → 视觉 Agent 识别（须报置信度）→ 人工兜底」三级。
- 系列第 1 篇（概念篇）见同目录 [原文-基于Browser-use-1-概念与知识澄清篇.md](原文-基于Browser-use-1-概念与知识澄清篇.md)；使用说明见 [使用说明.md](使用说明.md)。
