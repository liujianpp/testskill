# 【基于Skills方案】4.方案升级：基于skill的接口自动化测试--新增多接口串联、自然语言场景用例

> - 来源：知识星球 · Raina的AI&测试实战圈 · Raina
> - 发布时间：2026年04月27日 11:51
> - 原文链接：<https://articles.zsxq.com/id_nh5dg1bqmwpg.html>
> - 本地存档时间：2026-10-28（正文与图片为原文完整还原，图片直链来自原文；代码块按原文样式收录）

---

## 本章诉求

此前我们已分享基于 Skill 实现的 ApiAutoTest 1.0 版本，完成了基础的 API 接口自动化测试落地。

相关见文章：<https://t.zsxq.com/FeT1s>

但在实际项目落地使用过程中，还有一些需要优化的问题：

- 接口用例全量录入 Excel，内容繁杂冗余，人工查看、维护效率低，需精简用例内容，提升可读性与维护性；
- 仅支持单接口独立测试，无法满足业务流程下多接口串联的测试场景；
- 断言能力单一，暂不支持 MySQL 数据库校验，无法覆盖数据层结果验证需求。

针对以上问题，本次在 ApiAutoTest 1.0 的基础上进行迭代升级，推出 **ApiAutoTest 2.0**。新增了自然语言场景案例、多接口串联以及 mysql 断言的方式，流程图大概如下：

![ApiAutoTest 2.0 流程图](https://article-images.zsxq.com/FmyHT95pvF1sCslNZlTUSaB_Wdf-)

接下来我们通过一个常见的电商基础业务流程（商品创建、库存维护、用户下单等）对生成自然语言场景用例和多接口串联这两个问题进行案例讲解。 mysql 断言的使用在下一篇文章进行分享。

## 前置说明

ApiAutoTest 部分步骤中会同时生成 json 和 excel 文件

- json 用于给 AI 解读和分析，在修改内容的时候，建议也是让 AI 直接修改 json
- excel 主要用于给人查看或者评审的。

具体的原因，可以查看文末的问题答疑，这里就不做过多的讲述。

## 操作步骤

### 1、skill 安装

下载后解压到自己的 skills 目录下，如: .cursor/skills 或者 .claude/skills（可以看下其他 skill 的文章教程）

<https://mxhjscggz8q.feishu.cn/wiki/RFKWwFWs2i5Bikkp1rxcSEVDnSb?from=from_copylink>

### 2、生成接口文档（非必要）

如果自己本身有接口文档的话，就不需要执行该 skill，本 skill 的目的是基于已有的项目代码，生成接口文档。

公司有提供接口文档的，直接把接口文档上传到 AI 工具里面，可以直接复制所有接口到 md 文档，也可以通过对应的 mcp 把线上的接口文档读取进来，具体可以参考下这篇文章：

<https://t.zsxq.com/bO1si>

![接口文档生成输入](https://article-images.zsxq.com/FnGbeGTUMwVBDnQH2NV0FenrOqXI)

生成的接口文档如下：

![生成的接口文档](https://article-images.zsxq.com/Fo7hy05uXlAjlNcDqOt_6N_nlZwh)

### 2、生成项目配置

这里主要是对项目中的基础配置进行生成，用于后面用例执行的环境配置

输入：

![项目配置输入](https://article-images.zsxq.com/FuRnEib57J_lCDUZ-GDcQtqqvUib)

之后会生成 config/.env 文件

![生成config/.env](https://article-images.zsxq.com/FhDgetj6PavYZYfuTIMWKJloWY82)

内部文件可以看到，首先是后端基础 URL 配置，之后是 db 断言配置，默认为 false，关于断言这块，我们下一篇文章再详细说，本篇文章主要是多接口串联的实现。

![.env内容](https://article-images.zsxq.com/FsXa6chqIHaIN9IWLp-czlp-_qsO)

### 3、生成自然语言场景用例

操作步骤：

**场景 1：如果需要会对接口文档所有接口进行生成用例**

在对话框输入：@生成自然语言场景用例的 skill + 整个接口文档.md

![生成场景用例-全部接口](https://article-images.zsxq.com/Fsz80d-leU14INuH-BtdRstABPdh)

**场景 2：如果只需要生成对应模块接口的用例**

在对话框输入：@生成自然语言场景用例的 skill + 整个接口文档.md + 指定模块接口

![生成场景用例-指定模块](https://article-images.zsxq.com/FhPEzRKWOaBOQ1kq7_TGMtC7TAKl)

输出：

![场景用例输出](https://article-images.zsxq.com/Fnn3v0aqq_ViMFIMCbypk4epY8pP)

这一步会同时输出两份自然语言用例文件：

第一个是 `api_interface_scenario.json` 文件，这个文件的作用是后续 AI 会基于这个 json 文件，转换生成便于 AI 理解和执行的用例 JSON 脚本用例

文件内容解释：

第一部分是依赖，将相关接口的公用依赖写出来，之后其他需要使用的接口，可以直接获取参数

![scenario.json-依赖部分](https://article-images.zsxq.com/FietYis8gvkGw-NG4nLYbn1KLn82)

后面是 cases，也就是场景用例，这里使用的是偏自然语言的，目的就是为了给人看，而不是 AI，因此尽量追求简化，可以看到场景类型，分为单接口，以及串联

![scenario.json-cases部分](https://article-images.zsxq.com/FhQaCCF869vBTMoojpmXw1M1Pu5f)

如果是串联的话，则会将多接口进行调用，参数传递，结果校验等

![scenario.json-串联用例](https://article-images.zsxq.com/FtJHnyam3CCxP1BM43iv87t9Be3u)

第二个文件是 `api_interface_scenario.xlsx`，作用是输出通俗易懂的自然语言用例，便于人员快速阅读、理解业务场景等。

Excel 用例如下：

![scenario.xlsx用例](https://article-images.zsxq.com/FoP-1OWJkd_2DAwi5KzRTGNcMpr8)

### 4、人工检查

一般而言，AI 生成出来自己会进行首轮的自检，但是毕竟 AI 生成和检阅的结果，不一定是完整正确的，尤其是接口文档给的上下文不一定准确的时候，因此这里我列出一个步骤，就是为了要求人工检查，否则就只能在执行的过程中，报错或者遗漏的时候再去检查了

### 5、生成测试用例脚本

输入：`/api-test-generator` + `api_interface_scenario.json`

`api_interface_scenario.json` 就是我们在前面第 3 步讲到的自然语言用例文件

![生成测试用例脚本输入](https://article-images.zsxq.com/FhpVKvHL5LeJF-NFzVvkaDK9mF2u)

这个的目的，主要转义成 AI 能读懂的，结构化的 json，如下，生成结果如下：

我这里先简单复制几条

```json
{
  "dependencies": [
    {
      "name": "dep_login_admin",
      "depends_on": "",
      "request": {
        "method": "POST",
        "path": "/auth/login",
        "headers": {},
        "path_params": {},
        "body": {
          "username": "admin",
          "password": "admin123"
        }
      },
      "assert": {
        "status": 200,
        "checks": [
          "$.code==200 && $.data.token && $.data.userId"
        ]
      },
      "extract": {
        "token": "$.data.token",
        "userId": "$.data.userId"
      }
    }
  ],
  "cases": [
    {
      "id": "25",
      "name": "商品创建入库后下单并回查",
      "enabled": true,
      "steps": [
        {
          "name": "step_01_post",
          "request": {
            "method": "POST",
            "path": "/api/v1/products",
            "headers": {
              "Authorization": "Bearer DEP:dep_login_admin.token"
            },
            "path_params": {},
            "body": {
              "name": "AutoProd_链路_01",
              "price": 199.0
            }
          },
          "assert": {
            "status": 200,
            "checks": [
              "$.code==200"
            ]
          }
        },
        {
          "name": "step_02_post",
          "request": {
            "method": "POST",
            "path": "/api/v1/inventory/inbound",
            "headers": {
              "Authorization": "Bearer DEP:dep_login_admin.token"
            },
            "path_params": {},
            "body": {
              "productId": "p1001",
              "quantity": 20
            }
          },
          "assert": {
            "status": 200,
            "checks": [
              "$.code==200"
            ]
          }
        },
        {
          "name": "step_03_post",
          "request": {
            "method": "POST",
            "path": "/api/v1/orders/place",
            "headers": {
              "Authorization": "Bearer DEP:dep_login_admin.token"
            },
            "path_params": {},
            "body": {
              "items": [
                {
                  "productId": "p1001",
                  "quantity": 2
                }
              ]
            }
          },
          "assert": {
            "status": 200,
            "checks": [
              "$.code==200"
            ]
          }
        },
        {
          "name": "step_04_get",
          "request": {
            "method": "GET",
            "path": "/api/v1/orders/{orderId}",
            "headers": {
              "Authorization": "Bearer DEP:dep_login_admin.token"
            },
            "path_params": {
              "orderId": "order-uuid"
            }
          },
          "assert": {
            "status": 200,
            "checks": [
              "$.code==200"
            ]
          }
        },
        {
          "name": "step_05_get",
          "request": {
            "method": "GET",
            "path": "/api/v1/inventory/{productId}",
            "headers": {
              "Authorization": "Bearer DEP:dep_login_admin.token"
            },
            "path_params": {
              "productId": "p1001"
            }
          },
          "assert": {
            "status": 200,
            "checks": [
              "$.code==200"
            ]
          }
        }
      ],
      "assert": {
        "status": 200,
        "checks": [
          "$.code==200"
        ]
      }
    }
  ]
}
```

可以看到，AI 使用 steps 将多个接口串联起来，对于公用的接口，则会使用 dependencies 抽取依赖，然后进行响应结果的复用，如：登录态等

前置依赖参数的使用如下：使用 `DEP:依赖名称.提取参数`

![DEP引用示例](https://article-images.zsxq.com/Fkc-wMFJAeg70HcZvHl_-au9vKdH)

当然，这一步也会生成 excel，但是和前置说明说的一样，主要是用于查阅和评审

![生成的cases excel](https://article-images.zsxq.com/Fu2rubsJZb_4Nsu6gScjCXDk7L5i)

### 6、执行

输入： `/api-test-runner` @cases.json 文件

![执行输入](https://article-images.zsxq.com/FjaC2fiAUEus-cZpVr7lOGCE4XC0)

输出：

例如，我首次执行的过程中，可以发现 AI 写的，预期结果都写错了，这里的原因是因为接口文档中，没有将业务异常码进行提供，导致 AI 断言的时候出现问题

![执行失败示例](https://article-images.zsxq.com/FjuEoIwhJ9B-_GLfmowfT-ATc4hR)

AI 会给出修改建议，可以让 AI 进行修改，然后重新执行

输入：

![按建议修改输入](https://article-images.zsxq.com/Fl5PPJmolSf56xGnozjLh_H16MW-)

之后，AI 进行了修改并执行

![修改后执行结果](https://article-images.zsxq.com/FnddyEPpHhs9CvDCpPB3bYA_G7aU)

当然，我们还是需要分辨的，如果对于业务性，或者系统性 bug 的话，则不能让 AI 直接修改断言，例如系统执行本应该是正确，返回 code=200，但是 AI 返回失败 500，然后这个时候 AI 为了执行通过，建议将 200 改为 500，这个就有问题了

### 7、报告查询

输入：

![报告查询输入](https://article-images.zsxq.com/FsxGSooL7eCGOOhf87312n44ctEk)

这里使用的是 allure，如果没有安装的话，则需要安装一下，按照 AI 提供的指示安装即可

AI 会在终端中直接启动，访问地址即可

![allure启动](https://article-images.zsxq.com/FnmnhNi5YHO0GeCl_uWhkGzYrjCn)

查看报告结果如下：

![allure报告](https://article-images.zsxq.com/FlYlfDMpqPeZdOj4ynOgBnD_wrbC)

可以在 suites 中查看详细的执行过程和结果

![allure suites](https://article-images.zsxq.com/FvG4yE-9nvvMxvUzgXQlYH4dHKnh)

## 问题答疑

**为什么给 AI 解析使用 json，而不是 excel**

- **结构化更强**：JSON 天然支持嵌套结构（`dependencies`、`cases`、`steps`、断言对象），表达 A->B->C 串联、变量引用更直接；Excel 多层结构只能"摊平"成列，语义容易丢。
- **更适合自动执行**：runner 直接按字段读 `plan.json`，几乎零歧义；Excel 常有单元格格式、空格、换行、类型被自动转换等问题，执行前还得做兼容处理。
- **版本管理友好**：JSON 在 Git 里 diff 清晰（字段级变化）；Excel 是二进制文件，冲突难合并、审查困难。
- **便于程序生成/校验**：生成器、脚本、CI 可以直接产出和校验 JSON（schema 校验、必填检查、引用合法性检查）；Excel 自动化校验成本更高。
- **跨工具一致性更好**：后续你想接 AI 生成、脚本转换、批量改参、回归编排，JSON 都更标准化。
- **性能和可维护性更优**：大规模用例时，JSON 读写和批处理通常更稳定，排障也更容易定位到具体字段。

**Excel 仍有价值，但更偏人读/评审**：给测试同学做浏览、筛选、评审、手工编辑更直观。

所以现在这套"`plan.json` 执行 + `plan.xlsx` 展示"的双轨是合理的： JSON 做机器执行源，Excel 做人类视图。

因此大家在修改脚本的时候，可以对话让 AI 直接修改，这样子就可以将 json 和 excel 同时修改了，或者直接修改 json，单独修改 excel 在执行脚本的时候是无效的。

## ©版权声明

本文为知识星球【Raina的AI&测试实战圈】所有内容，受《中华人民共和国著作权法》及平台规则保护。

仅限本人学习，严禁搬运、外传、商用、外部引流等行为。

违规者将立即踢出星球、终止服务且不予退款；情节严重将依法追究法律责任

---

## 归档备注（非原文内容）

以下为本目录版本与文章所述版本的对照：

- 文中「AI 会给出修改建议，**可以让 AI 进行修改**，然后重新执行」——本仓库 api-test-runner 已收紧为**只执行不修改**：失败只输出建议（含文章同款提醒：警惕 AI 为凑通过把 200 改成 500），不替用户落地改用例文件。
- 文中场景/用例文件名 `api_interface_scenario.json/xlsx` 对应本仓库 `docs/<name>_scenario.json/xlsx`（api-scenario-generator）；执行输入 cases.json 对应 `docs/<name>_cases.json`。
- 本仓库版本在文章基础上的增量：**db_assert 数据库断言**（先 `export_db_schema.py` 查表结构再组 SQL，占位符禁手工加引号）、登录去重与 DEP 注入强约束、14 项生成自检清单、敏感信息环境变量化。
- 系列第 2 篇（1.0 完整使用教程）见同目录 [原文-基于Skills方案-2-接口自动化完整使用教程.md](原文-基于Skills方案-2-接口自动化完整使用教程.md)；使用说明见 [使用说明.md](使用说明.md)。
