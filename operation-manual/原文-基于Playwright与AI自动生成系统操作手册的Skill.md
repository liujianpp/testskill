# 基于 Playwright+AI 自动生成系统操作手册的 Skill

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年08月14日 08:00
> - 原文链接：<https://articles.zsxq.com/id_govt366kvfw8.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文）

---

## 本文诉求

在日常工作中，有些公司会要求测试同学负责编写产品操作手册，这个过程特别耗费人力，页面点击、流程步骤都要手动记录。那么能否可以结合 UI 自动化工具与 AI，实现浏览器端自动操作、同步生成标准化操作手册？

我这边做了个尝试，基于 Playwright 开发了一套 Skill，当前可覆盖 80%~90% 业务场景，基本满足日常手册编写需求。下文将拆解该方案的实现原理与完整使用流程。

## Skill 原理

![Skill原理](https://article-images.zsxq.com/FtY5ZVZ4wo3KLdFoV17qA6ecJL4h)

**执行流程解析：**

1、收集输入

向用户要网站地址、产品名称等必填信息；缺什么就追问，齐了再往下走。

2、规划探索

打开网站，看导航和菜单，列出要覆盖的功能模块，以及每块需要截哪些图。

3、探索与截图

用浏览器逐模块操作并截图。假设网站需要需要登录，则先登录并保存状态，如果不需要则直接探索

4、生成大纲

按模板整理章节结构；用户要确认就先展示，回复「直接生成」可跳过。

5、撰写手册

按「目的 → 操作 → 截图 → 预期结果」写正文，没探索到的标「待补充」。

6、润色与输出

文字润色后，输出 Markdown 和 assets/ 截图目录，做质量检查，关闭浏览器并清理临时文件。

## 操作流程

### 1、skill 安装

将 skill 导入到你的项目中

skill 包下载：<https://mxhjscggz8q.feishu.cn/wiki/HaoVwgwGhigywvkn0kbcvmCInLe?from=from_copylink>

### 2、skill 执行

输入信息：

```text
/operation-manual
网站：xx
其他信息：xx
```

![输入信息](https://article-images.zsxq.com/FuD9mZJTZR2w2ccsHF3bGlwQigj5)

这里可以将你的网站、账号密码等信息输入给 AI，如果担心安全问题的话，也可以只提供网站，然后自己输入帐号密码

**AI 执行过程：**

使用 playwright cli 打开界面，抓取快照，确定网站上有什么功能/元素，用于后续的操作网站

![抓取快照](https://article-images.zsxq.com/FubzM61mT4c1Ygp3LqUstZofkrgB)

在获取可执行元素之后，使用 playwright cli 指令，进行点击操作

![点击操作](https://article-images.zsxq.com/FgT56AVgCxDoKMpPFWfDLVHNIgh1)

对相关的页面进行截图，并保存到本地文件夹中，用于后续操作手册的编写

![页面截图保存](https://article-images.zsxq.com/FjU-0Pn3KdYmWuGzbWhASRwSYcuw)

**最终输出结果：**

操作手册中，有不同模块的大纲

包含功能说明、截图、操作步骤、预期结果

![输出手册-1](https://article-images.zsxq.com/Fo9LkjkLq_uIwqxEIZNm3TttbRR3)

![输出手册-2](https://article-images.zsxq.com/Fk3G2vL7QKY41YepVjWKYnzBUTXV)

![输出手册-3](https://article-images.zsxq.com/Fmh9D77Bk8EsZUxvUfA0yz7komP5)

**常见问题**

以及输出了一个常见问题，用于操作手册的讲解等

![常见问题](https://article-images.zsxq.com/FrB-gKnE-2P_QsDRMcWoVgsuhQJV)

**附录**

![附录](https://article-images.zsxq.com/FvpAXSplmUnEvjUrUQqVFmwqSREm)

基本上完成了，当然由于业务信息的不充足，AI 只会根据页面中元素做判断，然后写出一份基础的操作手册文档，我们也可以让 AI 录制视频，但是时间可能会比较长，我这里就不做演示了，大家如果需要的话，可以基于这个 skill 去做优化，让 AI 录制视频

## 写在最后

AI 写的操作手册，不一定能够一次就满足我们想要的需求，可能有一些细节的内容没有进行补充，或者部分功能没有编写，这个时候，就需要我们人工做一些检查，或者可以让 AI 做检查，检查后，和 AI 二次对话，让其进行内容的补充，不断完善操作手册说明，达到真正实现效率的提升。

但是本 skill 也是能够一定的解放我们时间，希望能够帮助到你～

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为本目录版本与文章所述版本的对照：

- 文中六步执行流程与本目录 SKILL.md 一致（收集输入 → 规划探索 → 探索与截图 → 生成大纲 → 撰写手册 → 润色与输出）；本仓库版补充了输入字段表、截图命名约定（`{模块}-{步骤序号}-{简述}.png`）、`humanizer-zh` 润色规则与 6 项质量检查清单。
- 文中「可以让 AI 录制视频（较耗时，未演示）」在本仓库版未纳入默认流程，保持截图式手册产出。
- 登录/凭据约定一致：可只提供网站、账号密码自行输入；凭据不入手册不入 git。
- 使用说明见同目录 [使用说明.md](使用说明.md)。
