# 【基于Browser use】1. Browser use+Skill实现web UI自动化-概念&知识澄清篇

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年05月06日 07:50
> - 原文链接：<https://articles.zsxq.com/id_x29slsufdbwn.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文）

---

## 本文目的

AI 驱动 UI 自动化的方案里，除了我们前面分享过的 playwright mcp、playwright cli、Midscene.js 这几个比较常见的方案，还有一个近期热度较高的 UI 自动化解决方案—— **Browser-use**。

今天这篇文章给大家分享一下 Browser-use 的原理、与 playwright cli 的区别、使用流程等前置基础知识，大家可以先学习了解一下，下篇文章会分享基于 Browser use 实现 web UI 自动化的整体流程。

## Browser-use 是什么？

Browser-use 是当前比较主流的浏览器 UI 自动化解决方案之一，整体底层完全基于 Playwright 框架开发，采用 **大模型 LLM + 浏览器智能 Agent + Playwright 底层驱动** 的三层架构，核心是把自然语言任务转化为可执行的浏览器原生操作。

简单而言，Browser-use 内置了 DOM 快照抓取、元素定位的能力，让我们不需要太多于关注内部逻辑，而是关注自然语言编写的测试用例即可。

### 与 playwright cli 的区别

playwright cli 需要关注快照以及编写 playwright cli 执行的元素定位脚本，而 Browser-use 不需要，Browser-use 会在执行的过程中去抓取快照，并且进行临时缓存元素定位，因此也有个弊端，在关闭会话，或者上下文过多的时候，Browser-use 执行，就需要重新去抓取快照进行分析，因此二者也具备其利弊，都可以进行学习，然后选择适合自己的方案。

## Browser-use 具备能力

![Browser-use具备能力](https://article-images.zsxq.com/FrwYNbGv1G6IbXptqNUrTXnU_59c)

## Browser-use 使用流程

简单说明，就是用命令行控制一个浏览器，先 open 进网页，用 state 看页面上能点的元素编号，再 click / input 等去操作；页面一变就再 state 拿新编号。可以无头跑、有头看窗口，也可以接本机 Chrome 或云端。需要画面就 screenshot，要取字就 get text 等，用完 close 关掉。适合自动点网页、测流程、截屏、抓数据。

![Browser-use使用流程](https://article-images.zsxq.com/FnuATuEUnH8sYkijU-OeqLVEZVMN)

## 常见问题

### Browser use 抓取 dom 之后，是否会进行缓存，减少上下文信息？

不会把 DOM 当成文件长期保存下来给你复用。

`browser-use state` 每次会重新走 `get_browser_state_summary()`，把当前页的 DOM 序列化成文本（`dom_state.llm_representation()`）打印出来，没有把整份 DOM 写到磁盘、下次直接加载复用的机制。

会在内存里缓存「索引 → 节点」映射，但只服务于同一会话、同一次快照周期。交互时用到的 `click` / `input` 等会通过 `get_element_by_index` 从 `_cached_selector_map` 里按数字下标取节点；这个 map 在 DOM 重建后会被 `update_cached_selector_map` 整体换掉。

可以看到下面的例子，在同一个会话中，如果已经抓取过快照，则不会重新去抓取 DOM，而是会直接去进行操作

![同会话复用快照示例](https://article-images.zsxq.com/FmTEfJaEOnPsof2RTKKCCMwfGSYW)

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

- 本文是 Browser-use 系列第 1 篇（概念篇）；第 2 篇（实践案例篇）见同目录 [原文-基于Browser-use-2-实践案例篇.md](原文-基于Browser-use-2-实践案例篇.md)。
- 本仓库 [browser-use/SKILL.md](../browser-use/SKILL.md) 即文中所述官方 browser-use skill 的命令契约；本目录 SKILL.md 为文中所述基于官方改造的 browser-use-case-runner。
