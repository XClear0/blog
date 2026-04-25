---
title: "Hugo 博客搭建记录"
date: 2026-04-25
draft: false
tags: ["Hugo", "VPS", "建站"]
categories: ["折腾记录"]
description: "记录从零搭建 Hugo 静态博客的完整过程，包括主题配置、自动部署和备案信息展示。"
---

## 为什么选择 Hugo

折腾博客一直是程序员的保留节目。这次选择 Hugo，理由很简单：

- **快**：Go 编写，千篇文章秒级构建
- **轻**：生成纯静态文件，VPS 上只需 Nginx 伺服，内存占用不到 10MB
- **省心**：配合 GitHub Actions，推送即部署，不用手动上传

## 技术栈

```
Hugo + PaperMod 主题
GitHub Actions 自动构建
SCP 推送到 VPS
Nginx 伺服静态文件
Certbot 管理 HTTPS 证书
```

## 部署流程

整个流程跑通之后，写博客只剩一件事：

```bash
# 新建文章
hugo new posts/my-post.md

# 写完推送，剩下的交给 CI
git add . && git commit -m "new post" && git push
```

GitHub Actions 大约 30 秒后完成构建和部署，刷新页面即可看到新文章。

## 备案

博客部署在国内 VPS，按要求完成了工信部 ICP 备案和公安网安备案，信息显示在页脚。

---

> 工欲善其事，必先利其器。博客搭好了，接下来就是好好写文章了。
