# 【用例生成】基于 playwright cli + 需求文档生成测试用例

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年09月24日 08:00
> - 原文链接：<https://articles.zsxq.com/id_ucr7vooqhchw.html>
> - 本地存档时间：2026-10-27（正文与图片为原文完整还原，图片直链来自原文）

---

## 本文诉求

写测试用例时，很多同学都会碰到两类棘手场景：

一是项目没有完整需求文档；

二是仅有一份简略的需求文档，很多业务细节没有写明。

测试只能自己脑补、补充大量操作步骤来写用例，很容易出现理解偏差，等到执行阶段才发现各种问题。

于是我尝试了一个新的方案：能不能借助 Skill，结合页面界面与现有需求资料，自动生成更完整的测试用例？

本次实践，依靠 Playwright CLI 探查页面元素，搭配需求文档提取测试点，最终输出完整用例，下面介绍具体实现思路。

## Skill 介绍

### Skill 下载

下载地址：[基于 playwright cli +需求文档生成测试用例](https://my.feishu.cn/wiki/ADwpwLHZkiFHCXkDwyLcZkiLnof?from=from_copylink)

### Skill 执行步骤

![Skill 执行步骤](https://article-images.zsxq.com/FsM1EYheg8Cn6rvGFi16X8Uy-z-b)

下面进行两个案例的演示

## 案例 1：只提供系统地址

### 1、执行 Skill

![案例1-执行Skill](https://article-images.zsxq.com/FhFTvkgkZPTNMrxxyMUl8fD8iUzz)

这里如果有需求文档的话，也可以提供需求文档，这样子 AI 就会根据需求文档去操作相关的界面，遇到一些不同的元素的时候，则会提供给你做判断，看你认可需求文档还是当前界面

### 2、界面探索

跳转到对应界面中，生成快照

![案例1-界面快照](https://article-images.zsxq.com/FhI11HNtRvqVH8mZ79B6TWk_xLTc)

点击和操作快照中的元素，将涉及的界面的元素和步骤基本都操作一遍

![案例1-操作元素](https://article-images.zsxq.com/FsqF-sTLTdH0V--x4GhOO-kjC86_)

### 3、产出计划

在界面探索完成之后，会生成一个`计划.md`文件，将本次探索的相关内容，使用一个文件进行记录，然后提供给我们人工进行确认，以及生成测试点等，在相关事项确认之后才进行用例的生成，这样子产出的用例质量会高一些

下面是计划文档的内容讲解

**界面推断功能**

AI 会根据 playwright 探索的界面，记录界面中有什么功能

![计划-界面推断功能](https://article-images.zsxq.com/FlXq7vNw0NxB5-N1jjOiZlc-PWAu)

**探索的界面**

![计划-探索的界面](https://article-images.zsxq.com/FpTkbwMWfQ_eaCYYzHOEsxAMzYT0)

**差异性和一致性判断**

这里如果有需求的话，则会判断需求和界面的差异和一致，如果没有需求的话，AI 就会去判断当前的界面的合理性，

如下：

![计划-差异性和一致性判断](https://article-images.zsxq.com/Ft5PgV-C2qdQS81kF_DdNix7Ylas)

之后如果对这些差异不认可的话，可以进行二次对话，将正确的业务内容在对话框中输入

**测试点**

生成了测试点，这里可以进行预览，判断生成的测试点是否遗漏等等

![计划-测试点](https://article-images.zsxq.com/FqD_kOE_-TPjMmUKT7bb4uDYnxd-)

### 4、生成用例

AI 会让你去检查 plan 是否有问题，如果没问题的话，则回复"确认"即可

![确认对话](https://article-images.zsxq.com/FmsyDJVbxll7WD8kEzGGi0m_sbUt)

之后就会产出用例了，默认生成的是 excel 格式，可以看到，生成的测试步骤也会相对比较详细

![生成的Excel用例](https://article-images.zsxq.com/FhPI__ndzQkV2uMU75ngr9x69Kwu)

如果需要 xmind 格式的话，则继续对话即可，如：

![要求XMind的对话](https://article-images.zsxq.com/FolMsXHL6jdS1nSYR4PRVatLGfaO)

生成的 xmind 用例

![生成的XMind用例](https://article-images.zsxq.com/FvWwKyxonPBWl0HmSgSYfZytsJ9C)

## 案例 2：提供需求文档和 URL

这里就不把全部的步骤都列出来了，和上面内容是有些重复的

输入：

![案例2-输入](https://article-images.zsxq.com/Fnh-4LUOhs63DV2n0frK_mYA6B2R)

之后会如同方案 1 一样，产出计划

但是这里和方案 1 有区别，在计划中，会有一个界面和需求不一致功能的表格

![案例2-需求与界面不一致表格](https://article-images.zsxq.com/FqQxJGuaDzS6wKzIMf-shNI_9k7S)

AI 会自动比对需求文档与页面界面，识别两者之间的差异。默认以需求文档作为验收基准；如果确认页面实际实现才是正确版本，也可以通过对话交互调整基准，最终生成的测试用例就会以界面为准。

后面的内容就是和方案 1 一样，先产出测试点，之后基于测试点产出测试用例，这里就不重复讲了。

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为本目录 1.0.1 版本与文章所述版本的差异，供对照：

- **验收基准**：文章案例 2 写「默认以需求文档作为验收基准，可对话调整」；本地 1.0.1 SKILL.md 收紧为——存在「不一致」时**必须由用户选定**验收基准（按需求 / 按界面），技能不得默认替用户拍板，未选定前不得发出「请确认测试点」终态。
- **无需求时的差异判断**：文章写「无需求时 AI 判断当前界面的合理性」；本地 1.0.1 计划中「需求 vs 界面」一栏无需求时写「不适用（基于界面探索推断）」。
- 本地 1.0.1 增加了明确的**登录墙与验证码处理规约**：遇登录停下问测试账号；纯字符图片验证码仅自动尝试一次识别，滑块/点选/短信等类型转人工。
- 本地 1.0.1 明确不生成 Playwright 自动化脚本（`.spec.ts`）。
- 详见同目录 [使用说明.md](使用说明.md)。
