# 基于 Playwright+Midscene 的 UI 自动化方案

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年09月21日 08:00
> - 原文链接：<https://articles.zsxq.com/id_2t0wd85t30bw.html>
> - 本地存档时间：2026-10-27（正文与图片为原文完整还原，图片直链来自原文）

---

## 本文诉求

此前我们基于 Playwright CLI + Test 搭建 UI 自动化方案，但落地过程中遇到不少边界场景：Canvas/WebGL 图表、封闭 Shadow DOM、图形验证码等难以定位的页面元素。

针对这类问题，我们选择降级方案：引入 midscene.js，依托它的视觉识别能力编写自动化脚本。

有人会疑惑：为什么不直接使用本地 AI Agent 多模态能力，还要额外接入 midscene？

核心原因是：我们需要脚本能够在 CI 流水线、云端环境稳定运行，本地 AI Agent 多模态方案并不适配这类执行环境。

因此本文融合两种方案，对 Skill 进行优化。

这里对于 playwright cli、playwright test、midscene 的基础介绍就不再讲解了，大家可以在星球里面查看往期文章：

<https://t.zsxq.com/D1OwN>、<https://t.zsxq.com/rYZYo>

## Skill 介绍与获取

### Skill 包下载

下载地址：<https://my.feishu.cn/wiki/BCDywprPZiuZ5RkXnn3c2w7Fn2d>

### Skill 作用

![Skill 作用](https://article-images.zsxq.com/FiCRLgzR_5p1GY9n__SDd8S58VVH)

### Skill 使用步骤

![Skill 使用步骤](https://article-images.zsxq.com/FgTnp4cpE_61-9RmAnUlN3XvgVlp)

## 实操案例

### 1、探索 & 计划生成

这里大家也可以直接提供更详细的用例，AI 则会基于用例去探索界面，如果没有提供的话，它就会直接去探索页面信息，生成用例

输入案例：

![探索计划-输入案例](https://article-images.zsxq.com/FjectiFgm3dipFIVhnVte_H7iQjJ)

之后会使用 playwright cli（默认使用无头的方式），进行页面的探索，然后产出一份探索报告（md 文件），

主要需要查看的内容如下：

**测试用例矩阵**

![探索报告-测试用例矩阵](https://article-images.zsxq.com/FtNMAMIWXD-YjCos4LloesHHv65a)

**代码映射表**

![探索报告-代码映射表](https://article-images.zsxq.com/Fh2tz6o2wMmyvqV5kR6Q5flyVVkZ)

这里大家可以简单预览一下，看看生成的约束是否正确，如下：

对于验证码，采用的是 midscene，因为这类图形类验证码，Playwright 无法直接识别

![验证码采用midscene](https://article-images.zsxq.com/Fgz4UvuLeFoyPe6QbtPt92dEo_7h)

**定位和驱动的逐步分析**

如果大家担心 AI 的质量问题，且具备一定 UI 自动化基础的话，则可以直接预览这个判定，对有误的部分做调整，从而可保证输出代码质量；当然也可以不看，在后面执行的时候出现问题的时候再修复也是 OK 的。

![定位和驱动的逐步分析](https://article-images.zsxq.com/FkgX92BAeBHGV4do4CEn7RVYSoYg)

### 2、生成代码

在计划没问题之后，就可以产出代码了

执行下面的 Skill

![执行生成代码Skill](https://article-images.zsxq.com/FkjbDIi8Yw7Pk7jkb7YYZsJ28-8U)

产出代码，会根据不同的代码模块封装不同的 page

![Page封装](https://article-images.zsxq.com/FsbB2gIR46RGWwPL_Fd6IVjmDhUr)

编写 UI 自动化脚本

![UI自动化脚本](https://article-images.zsxq.com/FlgA9UGyKDjsmeDlEtXXSynllAYe)

也生成了一个环境配置文件模板，内部需要对参数进行配置，如 midscene 的环境变量

![环境配置文件模板](https://article-images.zsxq.com/ForNxUBg4EYP222M0G_RWMxGqQv_)

### 3、环境配置

复制一份 .env.example，然后文件名称修改为 .env

填写 midscene 的变量，如：下面我用的多模态是 qwen3.7-plus

**记住 midscene 配置多模态的模型**

![midscene环境变量配置](https://article-images.zsxq.com/Fh940XhNxyqpnPvVq1gMPdxb2bur)

```bash
MIDSCENE_MODEL_API_KEY=环境变量
MIDSCENE_MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MIDSCENE_MODEL_NAME=qwen3.7-plus
MIDSCENE_MODEL_FAMILY=qwen3
```

### 4、执行脚本

这个主要是用于本地调试的 Skill，如果在流水线中执行的话，一般就直接使用命令去执行

输入：

![执行脚本-输入](https://article-images.zsxq.com/Frq__daCM9BXHC1JGrgkrH__qlro)

输出案例：

例如我第一次执行，是有存在失败的

![执行脚本-输出（存在失败）](https://article-images.zsxq.com/Fo6mGFoo5XJyTEMr2fYsr5OnlRfy)

### 5、脚本修复

这里我们对代码进行修复，可以在上面的同个会话中，回复："是" 或者执行

![修复-对话](https://article-images.zsxq.com/FoxXMHKbrRH8eiqYCzJnvuPfl-gs)

之后 AI 会根据上面的信息，对脚本进行修复，并重新调试

调试完之后，我们可以看下结果

![修复后调试结果](https://article-images.zsxq.com/Fn5APalrIQu_MrJ9MtdgM0-clpbp)

### 6、查看报告

默认访问：

<http://localhost:9323>

即可，采用的依旧是 playwright test 的报告

![Playwright HTML报告](https://article-images.zsxq.com/FvY3bbzhX-XZHdBTI7Tobu_V-y6s)

支持查看视频

![报告-视频](https://article-images.zsxq.com/FrhteVYC0yrkWg9cW83tdkUQHgpk)

记录 trace，执行步骤等

![报告-trace](https://article-images.zsxq.com/FumSRHT5EVbkHMyzg-AwyQtC1x6x)

也可以打开 midscene 的执行报告

![Midscene执行报告入口](https://article-images.zsxq.com/FgMmV31QiqXDda0qla50BsFpVxfc)

效果如下

![Midscene报告效果](https://article-images.zsxq.com/FjnPGoYAFw0paXKH7tw2TReIJf0E)

当然，这里多模态的执行也不是十分准确的，不是一次性识别成功，像我上面这个，使用 qwen3.7-plus，识别了 3 次才将图片中的验证码识别出来

### 7、如何通过脚本执行呢？

我们编写脚本有个目的，就是期望能够复用，那么如果复用脚本的基础上，要如何去执行脚本呢？

执行用例

```bash
# 跑全部
npm test

# 或只跑某个 spec
npx playwright test tests/login-apartment.spec.ts
```

查看报告

```bash
npm run show-report
```

如果端口被占用的话，则先清除端口：9323

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为本目录技能版本与文章所述版本的差异/补充，供对照：

- **探索模式**：文章写「默认使用无头的方式」探索；本地 00 技能明确**探索有头**（`open --headed`，便于人工观察与截图），**跑测无头**（02 执行阶段）。
- 本地技能补充了文章未展开的工程化约束：验证码**分层重试**（读码格式不合格默认 3 次、提交后验证码错误默认 5 次）、验证码逻辑集中 `tests/helpers/captcha.ts`、01 对**存量 Playwright 项目的硬约束**（只补缺不覆盖、不建平行文件）、03 修复**最多 2 轮**。
- 环境变量与文章一致（`MIDSCENE_MODEL_*` 四项），本地技能强调模型**必须支持视觉/多模态**，且缺 key/无视觉能力时**阻塞**而非走 locator 修复。
- 详见同目录 [使用说明.md](使用说明.md)。
