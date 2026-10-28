# 【需求评审】基于测试视角进行需求评审的 skill

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年08月19日 08:00
> - 原文链接：<https://articles.zsxq.com/id_qboc2jzws8vx.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文）

---

## 本文诉求

在完整测试工作流程里，需求评审属于前置关键环节。

产品输出需求文档后，会提前把文档同步给测试人员研读。这个阶段非常考验测试人员的项目经验：经验丰富的测试，通读需求就能快速识别出大量漏洞、歧义与风险点，在需求评审会上输出有效问题，避免将问题带到测试阶段；而经验不足的测试，往往很难在评审阶段发现问题。

那我们是否可以借助 AI，站在测试人员的视角完成需求评审，以此提升需求评审的效率与评审质量？本文围绕该目标，设计一套面向测试的需求评审 Skill。

## 评审维度

这里以测试的视角进行需求评审，主要分为下面 5 个维度

![评审5维度](https://article-images.zsxq.com/FtrB5sQnyDLspNDln-vQvXDux6DH)

## 实践步骤

### 1、Skill 下载与导入

Skill 包下载：<https://my.feishu.cn/wiki/QUOtwACm8irtepkm7NHcOG2ynjc?from=from_copylink>

下载解压后，将 Skill 导入到对应 AI 工具的 Skill 目录下（如下图）

![Skill导入](https://article-images.zsxq.com/FsRBQWxIsbyNHtAmr2kMzuTZIS0P)

### 2、执行 skill

这里目前支持三种格式：分别为 pdf、word、md 等

如果需求是放在蓝湖、figma、axure 等这些平台上的，需要先使用对应的 skill 将需求读取下来，输出 md 的格式，

关于如何读取需求可以参考专栏里相关的方案。

下面我们以 md 作为需求文档进行评审

![执行skill输入](https://article-images.zsxq.com/FmtjWHFcBWUZicyPC9gZgCkC8OtM)

### 3、输出结果

在执行完 skill 之后输出了一份 md 格式的评审报告，下面我们讲一下报告中的内容

首先是输出了需求速览，整理出了需求的功能模块、角色、流程图，便于我们快速地对需求进行理解

![需求速览-1](https://article-images.zsxq.com/FuccMMrcGy5Kj-PPar17jskNssux)

![需求速览-2](https://article-images.zsxq.com/Fr8Zulq2efomPwT4-KvkEgCk9TEE)

![需求速览-3](https://article-images.zsxq.com/Fi43kEJeqBc6_a0-TekX-JW6zpiT)

之后从 5 个维度，输出评审的结果

**可测性与验收标准**

![可测性与验收标准](https://article-images.zsxq.com/FuBfwV90n7UWe3emNCi9mQ9Ruiqx)

**边界与异常**

这一部分是一些产品经常会忽略的内容，例如：边界、是否必填、删除后的逻辑处理等等，下面的案例就可以看到它对需求文档中的字段，进行了输出

![边界与异常](https://article-images.zsxq.com/FgIAjofDsF3F7zbliNB-4IP8y8sY)

**场景和状态**

![场景和状态](https://article-images.zsxq.com/FrHO7qv79jjY3DURBPwCKhQlRRme)

其他部分没有太多的问题，这边就不举例了

另外还会输出一份开放问题清单，这些内容可以找产品或者业务进行了解确认

![开放问题清单](https://article-images.zsxq.com/Fo9Wl48kBmYAc-9RaNnUJCy8R0kG)

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为本目录版本与文章所述版本的对照：

- 文中 5 维度（可测性与验收标准 / 边界与异常 / 场景与状态 / 数据与环境依赖 / 测试阻塞点）与本目录 `references/dimensions.md` 一致；每维度先给结论再列问题表、问题四级字段（级别/原文依据/问题/建议）与总体结论规则（有阻断即不通过）为本仓库版细化。
- 文中「需求速览」已固化为 7 步流程中的第 3 步（含最多 2 张 Mermaid 图约束）。
- 文中「开放问题清单」对应本仓库「测试阻塞点」维度中的开放问题检查项（并入分维度表格，不再单列清单节）。
- pdf/docx 抽取由 `scripts/extract_text.py` 承接（依赖 pdfplumber、python-docx）；抽取失败禁止编造。
- 使用说明见同目录 [使用说明.md](使用说明.md)。
