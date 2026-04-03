# CDISC Library API 完整文档

> **文档生成日期**: 2026-04-03
> **数据来源**: https://api.developer.library.cdisc.org/api-details

---

## 目录

- [API 总览](#api-总览)
- [认证与使用说明](#认证与使用说明)
- [1. CDISC Library API](#1-cdisc-library-api)
  - [QRS (问卷/评分)](#qrs-问卷评分)
  - [Diff (差异比较)](#diff-差异比较)
  - [CDASH](#cdash)
  - [CDASHIG](#cdashig)
  - [ADaM](#adam)
  - [SDTM](#sdtm)
  - [SDTMIG](#sdtmig)
  - [SENDIG](#sendig)
  - [Controlled Terminology (CT)](#controlled-terminology-ct)
  - [Integrated Standards](#integrated-standards)
  - [Rules](#rules)
  - [Documents](#documents)
  - [Search](#search)
  - [Products & Info](#products--info)
  - [Root Endpoints](#root-endpoints)
- [2. v1 Biomedical Concept Endpoints](#2-v1-biomedical-concept-endpoints)
- [3. v1 SDTM Dataset Specialization Endpoints](#3-v1-sdtm-dataset-specialization-endpoints)
- [4. v2 Biomedical Concept Endpoints](#4-v2-biomedical-concept-endpoints)
- [5. v2 Dataset Specialization Endpoints](#5-v2-dataset-specialization-endpoints)
- [参考资源](#参考资源)

---

## API 总览

| API 名称 | ID | 操作数量 | 描述 |
|----------|-----|---------|------|
| **CDISC Library API** | `cdisc-library-api` | **144** | CDISC Library 公共 API |
| **v1 Biomedical Concept Endpoints** | `cdisc-cosmos-bc-proxy-v1` | **3** | 生物医学概念端点 (v1) |
| **v1 SDTM Dataset Specialization Endpoints** | `cdisc-cosmos-specializations-proxy-v1` | **3** | SDTM 数据集特化端点 (v1) |
| **v2 Biomedical Concept Endpoints** | `cdisc-cosmos-bc-proxy-v2` | **6** | 生物医学概念端点 (v2) |
| **v2 Dataset Specialization Endpoints** | `cdisc-cosmos-base-specializations-proxy-v2` | **7** | 数据集特化端点 (v2) |

**总计：163 个 API 操作**

---

## 认证与使用说明

### Base URL

```
https://library.cdisc.org/api
```

### 认证方式

- 需要 **API Key** 进行认证
- API Key 可在 [Profile 页面](https://api.developer.library.cdisc.org/profile) 获取
- 请求头添加：`Authorization: Bearer {your-api-key}`

### 响应格式

支持以下格式：

- JSON
- XML
- ODM
- CSV
- Excel

### 重要注意事项

| 规则 | 示例 |
|------|------|
| 版本号用 `-` 而非 `.` | `/mdr/sdtm/1-6` ✅ (不是 `/mdr/sdtm/1.6`) |
| 路径参数区分大小写 | `/mdr/sdtm/1-6` ✅ (不是 `/mdr/SDTM/1-6`) |
| 不要在 URL 末尾加 `/` | `/mdr/sdtm/1-6/classes` ✅ (不是 `/mdr/sdtm/1-6/classes/`) |

---

## 1. CDISC Library API

### QRS (问卷/评分)

Questionnaires, Ratings & Scales 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/qrs/instruments/{instrument}/versions/{version}` | Get QRS Instrument Product |
| GET | `/mdr/qrs/instruments/{instrument}/versions/{version}/items` | Get QRS Instrument Items |
| GET | `/mdr/qrs/instruments/{instrument}/versions/{version}/items/{item}` | Get QRS Instrument Item |
| GET | `/mdr/qrs/instruments/{instrument}/versions/{version}/responseGroups` | Get QRS Instrument Response Groups |
| GET | `/mdr/qrs/instruments/{instrument}/versions/{version}/responseGroups/{responseGroup}` | Get QRS Instrument Response Group |
| GET | `/mdr/root/qrs/instruments/{instrument}` | Get Root QRS Instrument Product |

**示例请求**:
```
GET /mdr/qrs/instruments/CGI/versions/2-1
```

---

### Diff (差异比较)

用于比较不同版本标准之间的差异。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/diff/{product}/{version}/{previous}` | Compare a product with another version |
| GET | `/mdr/diff/{product}/{version}` | Compare a product with its immediately preceding version |

**示例请求**:
```
GET /mdr/diff/sdtm/1-8/1-7
```

---

### CDASH

Clinical Data Acquisition Standards Harmonization 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/cdash/{version}` | Get CDASH Product |
| GET | `/mdr/cdash/{version}/domains/{domain}` | Get a CDASH Model Domain |
| GET | `/mdr/cdash/{version}/domains/{domain}/fields/{field}` | Get a CDASH Model Domain Field |
| GET | `/mdr/cdash/{version}/domains/{domain}/fields` | Get CDASH Model Domain Fields |
| GET | `/mdr/cdash/{version}/domains` | Get CDASH Model Domains |
| GET | `/mdr/cdash/{version}/classes/{className}` | Get CDASH Class |
| GET | `/mdr/cdash/{version}/classes` | Get CDASH Class List |
| GET | `/mdr/cdash/{version}/classes/{className}/domains` | Get CDASH Model Class Domain List |
| GET | `/mdr/cdash/{version}/classes/{className}/fields/{field}` | Get CDASH Model Field |

**可用版本**: v1.0, v1.1, v1.2, v1.3

**示例请求**:
```
GET /mdr/cdash/1-3/domains
GET /mdr/cdash/1-3/classes
```

---

### CDASHIG

CDASH Implementation Guide 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/cdashig/{version}` | Get CDASHIG Product |
| GET | `/mdr/cdashig/{version}/domains/{domain}` | Get CDASHIG Domain |
| GET | `/mdr/cdashig/{version}/domains/{domain}/fields/{field}` | Get CDASHIG Domain Field |
| GET | `/mdr/cdashig/{version}/domains/{domain}/fields` | Get CDASHIG Domain Variable List |
| GET | `/mdr/cdashig/{version}/domains` | Get CDASHIG Domain List |
| GET | `/mdr/cdashig/{version}/classes/{className}` | Get CDASHIG Class |
| GET | `/mdr/cdashig/{version}/classes` | Get CDASHIG Class List |
| GET | `/mdr/cdashig/{version}/classes/{className}/domains` | Get CDASHIG Class Domain List |
| GET | `/mdr/cdashig/{version}/classes/{className}/scenarios` | Get CDASHIG Class Scenario List |
| GET | `/mdr/cdashig/{version}/scenarios` | Get CDASHIG Scenario List |
| GET | `/mdr/cdashig/{version}/scenarios/{scenario}` | Get CDASHIG Scenario |
| GET | `/mdr/cdashig/{version}/scenarios/{scenario}/fields/{field}` | Get CDASHIG Scenario Field |
| GET | `/mdr/cdashig/{version}/scenarios/{scenario}/fields` | Get CDASHIG Scenario Variable List |

**可用版本**: v2.0, v2.1, v2.2, v2.3

**示例请求**:
```
GET /mdr/cdashig/2-3/domains
GET /mdr/cdashig/2-3/scenarios
```

---

### ADaM

Analysis Data Model 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/adam/{product}` | Get ADaM Product |
| GET | `/mdr/adam/{product}/datastructures` | Get Analysis Datastructures |
| GET | `/mdr/adam/{product}/datastructures/{datastructure}` | Get ADaM Datastructure |
| GET | `/mdr/adam/{product}/datastructures/{datastructure}/variables` | Get ADaM Variable List |
| GET | `/mdr/adam/{product}/datastructures/{datastructure}/variables/{var}` | Get ADaM Datastructure Variable |
| GET | `/mdr/adam/{product}/datastructures/{datastructure}/varsets` | Get ADaM Variable Set List |
| GET | `/mdr/adam/{product}/datastructures/{datastructure}/varsets/{varset}` | Get ADaM Variable Set |

**可用产品**:
- ADaMIG v1.0, v1.1, v1.2, v1.3
- ADaM ADAE v1.0
- ADaM BDS for TTE v1.0
- ADaM OCCDS v1.0, v1.1
- ADaMIG NCA v1.0
- ADaMIG MD v1.0
- ADaM popPK v1.0

**示例请求**:
```
GET /mdr/adam/adamig-1-3
GET /mdr/adam/adamig-1-3/datastructures
```

---

### SDTM

Study Data Tabulation Model 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/sdtm/{version}` | Get SDTM Product |
| GET | `/mdr/sdtm/{version}/classes` | Get SDTM Class List |
| GET | `/mdr/sdtm/{version}/classes/{className}` | Get SDTM Class |
| GET | `/mdr/sdtm/{version}/classes/{className}/datasets` | Get SDTM Class Dataset List |
| GET | `/mdr/sdtm/{version}/classes/{className}/variables` | Get SDTM Class Variable List |
| GET | `/mdr/sdtm/{version}/classes/{className}/variables/{var}` | Get SDTM Class Variable |
| GET | `/mdr/sdtm/{version}/datasets` | Get SDTM Dataset List |
| GET | `/mdr/sdtm/{version}/datasets/{dataset}` | Get SDTM Dataset |
| GET | `/mdr/sdtm/{version}/datasets/{dataset}/variables` | Get SDTM Dataset Variable List |
| GET | `/mdr/sdtm/{version}/datasets/{dataset}/variables/{var}` | Get SDTM Dataset Variable |

**可用版本**: v1.2, v1.3, v1.4, v1.5, v1.6, v1.7, v1.8, v2.0

**示例请求**:
```
GET /mdr/sdtm/1-8/classes
GET /mdr/sdtm/1-8/datasets
```

---

### SDTMIG

SDTM Implementation Guide 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/sdtmig/{version}` | Get SDTMIG Product |
| GET | `/mdr/sdtmig/{version}/classes` | Get SDTMIG Class List |
| GET | `/mdr/sdtmig/{version}/classes/{className}` | Get SDTMIG Class |
| GET | `/mdr/sdtmig/{version}/classes/{className}/datasets` | Get SDTMIG Class Dataset List |
| GET | `/mdr/sdtmig/{version}/datasets` | Get SDTMIG Dataset List |
| GET | `/mdr/sdtmig/{version}/datasets/{dataset}` | Get SDTMIG Dataset |
| GET | `/mdr/sdtmig/{version}/datasets/{dataset}/variables` | Get SDTMIG Dataset Variable List |
| GET | `/mdr/sdtmig/{version}/datasets/{dataset}/variables/{var}` | Get SDTMIG Dataset Variable |

**可用版本**:
- SDTMIG v3.1.2, v3.1.3, v3.2, v3.3, v3.4
- SDTMIG-AP v1.0
- SDTMIG-MD v1.0, v1.1
- SDTMIG-PGx v1.0

**示例请求**:
```
GET /mdr/sdtmig/3-4/datasets
GET /mdr/sdtmig/3-4/datasets/DM/variables
```

---

### SENDIG

SEND Implementation Guide 相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/sendig/{version}` | Get SENDIG Product |
| GET | `/mdr/sendig/{version}/classes` | Get SENDIG Class List |
| GET | `/mdr/sendig/{version}/classes/{className}` | Get SENDIG Class |
| GET | `/mdr/sendig/{version}/classes/{className}/datasets` | Get SENDIG Class Dataset List |
| GET | `/mdr/sendig/{version}/datasets` | Get SENDIG Dataset List |
| GET | `/mdr/sendig/{version}/datasets/{dataset}` | Get SENDIG Dataset |
| GET | `/mdr/sendig/{version}/datasets/{dataset}/variables` | Get SENDIG Dataset Variable List |
| GET | `/mdr/sendig/{version}/datasets/{dataset}/variables/{var}` | Get SENDIG Dataset Variable |

**可用版本**:
- SENDIG v3.0, v3.1, v3.1.1
- SENDIG-DART v1.1
- SENDIG-AR v1.0

**示例请求**:
```
GET /mdr/sendig/3-1-1/datasets
```

---

### Controlled Terminology (CT)

控制术语相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/ct/packages` | Get CT Package List |
| GET | `/mdr/ct/packages/{package}` | Get CT Package |
| GET | `/mdr/ct/packages/{package}/codelists` | Get CT Package Codelist List |
| GET | `/mdr/ct/packages/{package}/codelists/{codelist}` | Get CT Package Codelist |
| GET | `/mdr/ct/packages/{package}/codelists/{codelist}/terms` | Get CT Package Codelist Term List |
| GET | `/mdr/ct/packages/{package}/codelists/{codelist}/terms/{term}` | Get CT Package Codelist Term |

**可用包**: P19 (2014-09-26) 到 P60 (2025-09-26)，共 42 个版本

**示例请求**:
```
GET /mdr/ct/packages
GET /mdr/ct/packages/p60/codelists
GET /mdr/ct/packages/p60/codelists/C667/terms
```

---

### Integrated Standards

集成标准相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/integrated/{standard}/{version}` | Get Integrated Standard |
| GET | `/mdr/integrated/{standard}/{version}/adam` | Get Integrated ADaM Product |
| GET | `/mdr/integrated/{standard}/{version}/adam/datastructures` | Get Integrated Analysis Datastructures |
| GET | `/mdr/integrated/{standard}/{version}/adam/datastructures/{datastructure}` | Get Integrated ADaM Datastructure |
| GET | `/mdr/integrated/{standard}/{version}/adam/datastructures/{datastructure}/variables` | Get Integrated ADaM Variable List |
| GET | `/mdr/integrated/{standard}/{version}/adam/datastructures/{datastructure}/variables/{var}` | Get Integrated ADaM Datastructure Variable |
| GET | `/mdr/integrated/{standard}/{version}/adam/datastructures/{datastructure}/varsets` | Get Integrated ADaM Variable Set List |
| GET | `/mdr/integrated/{standard}/{version}/adam/datastructures/{datastructure}/varsets/{varset}` | Get Integrated ADaM Variable Set |
| GET | `/mdr/integrated/{standard}/{version}/cdash` | Get Integrated CDASH Product |
| GET | `/mdr/integrated/{standard}/{version}/cdash/classes` | Get Integrated CDASH Class List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/classes/{className}` | Get Integrated CDASH Class |
| GET | `/mdr/integrated/{standard}/{version}/cdash/classes/{className}/domains` | Get Integrated CDASH Class Domain List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/classes/{className}/scenarios` | Get Integrated CDASH Class Scenario List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/domains` | Get Integrated CDASH Domain List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/domains/{domain}` | Get Integrated CDASH Domain |
| GET | `/mdr/integrated/{standard}/{version}/cdash/domains/{domain}/fields` | Get Integrated CDASH Domain Variable List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/domains/{domain}/fields/{field}` | Get Integrated CDASH Domain Field |
| GET | `/mdr/integrated/{standard}/{version}/cdash/scenarios` | Get Integrated CDASH Scenario List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/scenarios/{scenario}` | Get Integrated CDASH Scenario |
| GET | `/mdr/integrated/{standard}/{version}/cdash/scenarios/{scenario}/fields` | Get Integrated CDASH Scenario Variable List |
| GET | `/mdr/integrated/{standard}/{version}/cdash/scenarios/{scenario}/fields/{field}` | Get Integrated CDASH Scenario Field |
| GET | `/mdr/integrated/{standard}/{version}/sdtm` | Get Integrated SDTM Product |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/classes` | Get Integrated SDTM Class List |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/classes/{className}` | Get Integrated SDTM Class |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/classes/{className}/datasets` | Get Integrated SDTM Class Dataset List |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/datasets` | Get Integrated SDTM Dataset List |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/datasets/{dataset}` | Get Integrated SDTM Dataset |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/datasets/{dataset}/variables` | Get Integrated SDTM Dataset Variable List |
| GET | `/mdr/integrated/{standard}/{version}/sdtm/datasets/{dataset}/variables/{var}` | Get Integrated SDTM Dataset Variable |
| GET | `/mdr/integrated/{standard}/{version}/send` | Get Integrated SEND Product |
| GET | `/mdr/integrated/{standard}/{version}/send/classes` | Get Integrated SEND Class List |
| GET | `/mdr/integrated/{standard}/{version}/send/classes/{className}` | Get Integrated SEND Class |
| GET | `/mdr/integrated/{standard}/{version}/send/classes/{className}/datasets` | Get Integrated SEND Class Dataset List |
| GET | `/mdr/integrated/{standard}/{version}/send/datasets` | Get Integrated SEND Dataset List |
| GET | `/mdr/integrated/{standard}/{version}/send/datasets/{dataset}` | Get Integrated SEND Dataset |
| GET | `/mdr/integrated/{standard}/{version}/send/datasets/{dataset}/variables` | Get Integrated SEND Dataset Variable List |
| GET | `/mdr/integrated/{standard}/{version}/send/datasets/{dataset}/variables/{var}` | Get Integrated SEND Dataset Variable |

**示例请求**:
```
GET /mdr/integrated/tig/1-0/sdtm/datasets
```

---

### Rules

规则相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/rules` | Get all rule catalogs and standards they apply to |
| GET | `/mdr/rules/{standard}/{version}` | Get all rules from a rule type release |
| GET | `/mdr/rules/{standard}/{version}/rule/{rule_id}` | Get specific rule |

**示例请求**:
```
GET /mdr/rules
GET /mdr/rules/sdtmig/3-4
GET /mdr/rules/sdtmig/3-4/rule/SD0030
```

---

### Documents

文档相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/documents/{document_id}` | Get a document given a document id |
| GET | `/mdr/documents/{standard}/{version}/sections` | Get all documents sections for a given IG document |
| GET | `/mdr/documents/{standard}/{version}/usecases` | Get all documents usecases for a given IG document |
| GET | `/mdr/documents/{standard}/{version}/{structure}/sections` | Get all documents sections for a given IG document and structure |
| GET | `/mdr/documents/{standard}/{version}/usecases/{usecase}/sections` | Get all documents sections for a given IG document and use case |
| GET | `/mdr/documents/{standard}/{version}/{structure}/sections/{section}` | Get all documents associated with a given section and structure |
| GET | `/mdr/documents/{standard}/{version}/usecases/{usecase}/sections/{section}` | Get all documents for a given IG document, use case, and section |
| GET | `/mdr/documents/integrated/{standard}/{version}/{standard_subtype}/sections` | Get all documents sections for a given IG document (integrated) |
| GET | `/mdr/documents/integrated/{standard}/{version}/{standard_subtype}/{structure}/sections` | Get all documents sections for a given IG document and structure |
| GET | `/mdr/documents/integrated/{standard}/{version}/{standard_subtype}/usecases` | Get use cases (integrated) |
| GET | `/mdr/documents/integrated/{standard}/{version}/{standard_subtype}/{structure}/sections/{section}` | Get documents by section and structure (integrated) |
| GET | `/mdr/documents/integrated/{standard}/{version}/{standard_subtype}/usecases/{usecase}/sections` | Get sections by use case (integrated) |
| GET | `/mdr/documents/integrated/{standard}/{version}/{standard_subtype}/usecases/{usecase}/sections/{section}` | Get documents by use case and section (integrated) |

**示例请求**:
```
GET /mdr/documents/sdtmig/3-4/sections
```

---

### Search

搜索相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/search?q={q}` | Get Search Results Across CDISC Library |
| GET | `/mdr/search/scopes` | Get a list of Search Scopes |
| GET | `/mdr/search/scopes/{scope}` | Get Search Results Limited to Scope |
| GET | `/mdr/suggest?q={q}` | Get Search Query Suggestion Results |
| GET | `/mdr/search/implementedBy?href={href}` | Get products that implement href |

**示例请求**:
```
GET /mdr/search?q=AE
GET /mdr/search/scopes
GET /mdr/suggest?q=adverse
```

---

### Products & Info

产品与信息相关端点。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/products` | Get CDISC Library Product List |
| GET | `/mdr/products/{product-group}` | Get CDISC Library Product List by Product Group |
| GET | `/mdr/about` | Get Information About CDISC Library Product |
| GET | `/mdr/lastupdated` | Get CDISC Library Product Last Updated Dates |
| GET | `/mdr/maintenance` | Get CDISC Library maintenance status |

**示例请求**:
```
GET /mdr/products
GET /mdr/products/sdtm
GET /mdr/about
```

---

### Root Endpoints

根端点，用于获取最新版本的数据。

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/mdr/root/cdash/classes/{className}/fields/{field}` | Get Root CDASH Model Class Field |
| GET | `/mdr/root/cdash/domains/{domain}/fields/{field}` | Get Root CDASH Model Domain Field |
| GET | `/mdr/root/cdashig/domains/{domain}/fields/{field}` | Get Root CDASHIG Domain Field |
| GET | `/mdr/root/cdashig/scenarios/{scenario}/fields/{field}` | Get Root CDASHIG Scenario Field |
| GET | `/mdr/root/ct/{package-type}/codelists/{codelist}` | Get Root CT Codelist |
| GET | `/mdr/root/ct/{package-type}/codelists/{codelist}/terms/{term}` | Get Root CT Codelist Term |
| GET | `/mdr/root/integrated/{standard}/cdash/domains/{domain}/fields/{field}` | Get Root Integrated CDASH Domain Field |
| GET | `/mdr/root/integrated/{standard}/cdash/scenarios/{scenario}/fields/{field}` | Get Root Integrated CDASH Scenario Field |
| GET | `/mdr/root/integrated/{standard}/sdtm/datasets/{dataset}/variables/{var}` | Get Root Integrated SDTM Dataset Variable |
| GET | `/mdr/root/integrated/{standard}/send/datasets/{dataset}/variables/{var}` | Get Root Integrated SEND Dataset Variable |
| GET | `/mdr/root/sdtm/classes/{className}/variables/{var}` | Get Root SDTM Class Variable |
| GET | `/mdr/root/sdtm/datasets/{dataset}/variables/{var}` | Get Root SDTM Dataset Variable |
| GET | `/mdr/root/sdtmig/datasets/{dataset}/variables/{var}` | Get Root SDTMIG Dataset Variable |
| GET | `/mdr/root/sendig/datasets/{dataset}/variables/{var}` | Get Root SENDIG Dataset Variable |

---

## 2. v1 Biomedical Concept Endpoints

**API ID**: `cdisc-cosmos-bc-proxy-v1`

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/packages` | Get Biomedical Concept Package List |
| GET | `/packages/{package}/biomedicalconcepts` | Get Biomedical Concept List for Package |
| GET | `/packages/{package}/biomedicalconcepts/{biomedicalconcept}` | Get Biomedical Concept for Package |

**示例请求**:
```
GET /packages
GET /packages/2024-12-16/biomedicalconcepts
```

---

## 3. v1 SDTM Dataset Specialization Endpoints

**API ID**: `cdisc-cosmos-specializations-proxy-v1`

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/packages` | Get SDTM Dataset Specialization Package List |
| GET | `/packages/{package}/datasetspecializations` | Get SDTM Dataset Specializations List for Package |
| GET | `/packages/{package}/datasetspecializations/{datasetspecialization}` | Get SDTM Dataset Specialization for Package |

**示例请求**:
```
GET /packages
GET /packages/2024-12-16/datasetspecializations
```

---

## 4. v2 Biomedical Concept Endpoints

**API ID**: `cdisc-cosmos-bc-proxy-v2`

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/packages` | Get Biomedical Concept Package List |
| GET | `/packages/{package}/biomedicalconcepts` | Get Biomedical Concept List for Package |
| GET | `/packages/{package}/biomedicalconcepts/{biomedicalconcept}` | Get Biomedical Concept for Package |
| GET | `/biomedicalconcepts` | Get Biomedical Concepts List (latest) |
| GET | `/biomedicalconcepts/{biomedicalconcept}` | Get latest Biomedical Concept |
| GET | `/categories` | Get Latest Biomedical Concept Categories |

**示例请求**:
```
GET /biomedicalconcepts
GET /categories
GET /biomedicalconcepts/HEART_RATE
```

---

## 5. v2 Dataset Specialization Endpoints

**API ID**: `cdisc-cosmos-base-specializations-proxy-v2`

| Method | URL Template | Description |
|--------|--------------|-------------|
| GET | `/sdtm/packages` | Get SDTM Dataset Specialization Package List |
| GET | `/sdtm/packages/{package}/datasetspecializations` | Get SDTM Dataset Specializations List for Package |
| GET | `/sdtm/packages/{package}/datasetspecializations/{datasetspecialization}` | Get SDTM Dataset Specialization for Package |
| GET | `/sdtm/datasetspecializations` | Get Latest SDTM Dataset Specializations List |
| GET | `/sdtm/datasetspecializations/{dataset_specialization_id}` | Get Latest SDTM Specialization |
| GET | `/sdtm/domains` | Get SDTM Dataset Specialization Domain List |
| GET | `/datasetspecializations` | Get latest Biomedical Concept Dataset Specializations List |

**示例请求**:
```
GET /sdtm/datasetspecializations
GET /sdtm/domains
GET /sdtm/datasetspecializations/HEART_RATE_1
```

---

## 参考资源

- [CDISC Library Browser](https://library.cdisc.org/browser)
- [CDISC Library API Portal](https://api.developer.library.cdisc.org)
- [CDISC 官网](https://www.cdisc.org)
- [CDISC Library Service Desk](https://wiki.cdisc.org/display/LIBSUPRT)
- [HTTP Status Codes](https://wiki.cdisc.org/display/LIBSUPRT/HTTP+Status+Codes)

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-03 | 初始版本，包含 163 个 API 操作 |