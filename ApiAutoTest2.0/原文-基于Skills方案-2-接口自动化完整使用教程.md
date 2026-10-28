# 【基于Skills方案】2.使用教程：基于skill的接口自动化测试方案完整使用教程

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年03月23日 08:00
> - 原文链接：<https://articles.zsxq.com/id_gdrpppzz21uq.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文）

---

今天给大家分享下，**基于 skill 的接口自动化测试方案完整使用教程以及相关 skill 包提供**。

在开始之前先说说几点学习建议：

1、接口自动化整套流程生成下来涉及较多代码与框架逻辑，建议借助能力较强的大模型辅助完成（我在实操中使用 Cursor 的 Auto 模式，整体流程走下来还算顺畅）。另外完全零基础，没有接触过接口自动化测试的小伙伴，建议先去学习一些基础内容，不然可能会看不太懂。

2、建议先用我提供的 Python 后端项目完整走一遍流程，先理解整套 Skill 的工作原理和执行思路，熟练后再迁移到自己公司的真实项目中；有一定代码基础或接口自动化经验的同学，也可以直接在公司项目上尝试落地。

3、ApiAutoTest 主要是提供一个流程化的思路和案例给大家，实际工作环境中，可能会有更复杂的需求，例如接入 sql 结果校验，或者将报告直接同步到公司内部的缺陷系统等，都是可以去适配的，因此大家可以基于 ApiAutoTest 作为基础模板，不断的去优化，让它成为真正适用于团队内部企业的 skill pro～

4、本案例在执行的过程中，由于不同的环境以及大模型能力的强弱，可能会有不一样的输出结果，因此大家在遇到问题的时候，优先对照日志和结合 ai 辅助排查；多记录踩坑点，后续复用在自己项目时会更加顺畅。

## 操作步骤

### 一、Skill & 项目 & 依赖 安装

先在自己电脑本地新建了一个 apiauto-demo 的空文件夹，在 Cursor 中打开（这里大家可以用其他的工具都 ok）

![新建apiauto-demo](https://article-images.zsxq.com/FlEIF3Z8wt9RSnwL2IMSdstPs9vY)

接下来进行下面的步骤

1、导入 skill 安装包

下载地址：<https://mxhjscggz8q.feishu.cn/wiki/XzZ4wMd5Zi1fPjkC7OEciGJQnZg>

密码：526M398&

解压之后将 skill 放在 .cursor/skills 下，如果大家使用的是 claude code，就使用 .claude/skills，trae 就使用 .trae/skills 等等，（参考之前 skills 如何安装的文章）

![skill目录](https://article-images.zsxq.com/FgZprKh7DiQK05TfKXr_LsRi8I7N)

每个 skill 的作用说明：

![每个skill的作用说明](https://article-images.zsxq.com/Fmx5AgNNAFA-N6CeN5FAZNIQ8g4F)

2、python 依赖安装

下载 requirements.txt，并将其放在 apiauto-demo 根目录下：

<https://mxhjscggz8q.feishu.cn/wiki/CjJGwbzaIibSGPkVCkpcPCLxnEg?from=from_copylink>

requirements.txt 文件，这个文件主要是让我们提前安装好 python 依赖，可以提高 skill 的执行速度，否则在使用的时候，在进行下载，可能会比较慢

![requirements文件](https://article-images.zsxq.com/FquZOgQJQ_KfZXqlPvAn--RE91jg)

在命令行，进入根目录后执行以下命令：

```bash
# 先在项目根目录下，安装依赖。如果是python3，则使用pip3哦
pip install -r requirements.txt
```

![安装依赖](https://article-images.zsxq.com/FqQbmim77FMJ2gWjNsbqY9fkeeJe)

3、项目准备

我这里以 demo 项目为案例，大家如果是自己的项目的话，也可以打开自己的项目。

demo 项目拉取教程已经在上篇文章发过了，可自行去查看：<https://t.zsxq.com/e6PoP>

### 二、接口文档生成

对话框输入：

`/api-doc-generator  @项目文件夹/`

![接口文档生成输入](https://article-images.zsxq.com/FtHx3x8zI9I9ldXRfCwxVdzz1i42)

接口文档生成：

![生成的接口文档](https://article-images.zsxq.com/Fu-vhYftGClmMNnLAqKEUcscXkbf)

如果是用了自己项目来实践的小伙伴，可以自行把接口文档导进来

### 三、接口用例生成

这里对比了 csv 和 excel，最终还是选择了 excel，因为如果是 csv 的话，使用 wps 打开项目进行数据变更的时候，会出现格式问题；而 excel 不会有这个问题，而让 skill 能够转成 excel，采用的方式是先生成 json 文件，再将 json 文件转成 excel 文件

![json转excel](https://article-images.zsxq.com/FpSVwNGUPpG9ZfMezxdUeV3nUylI)

生成的 excel 效果：

![生成的excel效果-1](https://article-images.zsxq.com/FlPROMO_Tntjkehr8Gv16Btuhi89)

![生成的excel效果-2](https://article-images.zsxq.com/FnPCTRreMbUUamKiZxcQ4u9mdhTP)

这里的 json，我没有让 skill 删除，因为它是 excel 文件的源数据，ai 可以去更改它，之后来修改 excel 数据，这里各项的列，我们先不展开讲解，之后的文章会进行介绍

当然，生成出来的用例，不是直接就可以用的，还是需要人工检查一下。

### 四、环境配置

这里主要是需要对依赖前置接口，以及环境变量进行配置

如果是以前，我们可能要写 pytest 代码，那么现在，我们通过配置化的方式，将依赖前置写在 yaml 文件中，下面我们看下示例。

对话框输入：

![环境配置输入](https://article-images.zsxq.com/FqwiMLx4SBOUt2CbSVElfKqklH35)

生成了 3 个配置文件

![三个配置文件](https://article-images.zsxq.com/FuSXuAlf3WyB3mgx3fYV0Igc6fAe)

分别是：

**dependencies.yaml 文件**

这里可以看到，对用户登录（user_login) 接口进行了抽取，且该接口作为前置依赖被其他用例所使用

![dependencies.yaml](https://article-images.zsxq.com/FkRumgNdPpbZCmDSe8xBC6Do3n10)

**.env 配置文件：**

用于配置我们后端的 url，以及账号密码等

![.env配置文件](https://article-images.zsxq.com/FpQox4Q0BkRJTvTSN2l1YlJG2ro-)

**env.example:**

示例文件，我们这个不用太过关注

![env.example](https://article-images.zsxq.com/Fvuv__lQc-UoYZTT3UW01Lve4Yfb)

### 五、执行

可以直接输入指令，进行执行

![执行输入](https://article-images.zsxq.com/Fn9a2kGrrdAh3nCeSOVkoEmvMhWT)

可以看到，ai 会执行脚本

![AI执行脚本](https://article-images.zsxq.com/FomN-uqDTZXvQaQKCIANdOFwmFAX)

执行结果

![执行结果](https://article-images.zsxq.com/FohN7VB7IU6qRUN8BNGO8kQflULi)

之后会输出成功用例和失败用例，并且给出失败的原因（这里如果前面有做检查的话，一般是不会出现这些错误的，尤其可能是数据没有准备好之类的，例如前面的用例将后面的用例的数据账号删除了），因此，我们还是要检查一下参数的合理性的～

### 六、查看报告

执行 `/api-test-report`

![查看报告输入](https://article-images.zsxq.com/Fuugd2nLVNqkRUlxIRi8AJSxX3pt)

之后就可以看到，浏览器会弹出 allure 报告网页，如果有报错的话，就可以在此处进行分析了.

当然，如果没有安装 allure 的话，则需要进行安装，这里 ai 也会提示如何进行安装的，按照它的提示进行安装即可。

![allure安装提示](https://article-images.zsxq.com/FkpadjbBt10D5c1fpVcihd90FCQI)

以上就是全部内容，由于文章内容有点长，关于 ApiAutoTest 里面各个 skill 的执行原理会在下一篇进行分享，方便大家能更好的去理解，并按自己的需求去调整优化。

## ©版权保护

知识星球：【Raina的AI&测试实战圈】所有发布内容。依照《中华人民共和国著作权法实施条例》未经原作者允许和书面授权，禁止分享到各类平台进行引流或商用，一旦发现必追究法律责任！

---

## 归档备注（非原文内容）

以下为本目录 2.0 版本与本文（1.0 时期教程）的差异，供对照：

- 本文的**前置依赖载体是 `dependencies.yaml`**；2.0 已演进为 **cases.json 顶层 `dependencies`**（YAML 配置方式已废弃）。
- 本文时期用例由 Excel/JSON 承载单接口；2.0 新增**自然语言场景用例**（scenario.json/xlsx）与**多接口串联**，见系列第 4 篇 [原文-基于Skills方案-4-方案升级多接口串联与自然语言场景用例.md](原文-基于Skills方案-4-方案升级多接口串联与自然语言场景用例.md)。
- 2.0 另新增 **db_assert 数据库断言**（文章学习建议中提到的「接入 sql 结果校验」已落地）。
- skill 命名与职责对应关系见同目录 [使用说明.md](使用说明.md)。
