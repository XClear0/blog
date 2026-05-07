# Yet Another Viewpoint

这是一个使用 [Hugo](https://gohugo.io/) 和 [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 搭建的个人博客。

站点地址：<https://yaviewpoint.icu/>

## 技术栈

- 静态站点生成器：Hugo Extended
- 主题：PaperMod，通过 Git submodule 管理
- 配置文件：`hugo.toml`
- 自动部署：GitHub Actions 构建站点，并将 `public/` 上传到 VPS

## 目录结构

```text
.
|-- archetypes/          # Hugo 内容模板
|-- assets/              # Hugo 处理的站点资源
|-- content/             # 文章和页面内容
|-- layouts/             # 本地 Hugo 模板覆盖
|-- public/              # Hugo 构建输出目录
|-- static/              # 原样复制的静态文件
|-- themes/PaperMod/     # PaperMod 主题 submodule
|-- hugo.toml            # Hugo 站点配置
`-- .github/workflows/   # GitHub Actions 部署流程
```

## 环境准备

安装 Hugo Extended：

```powershell
winget install Hugo.Hugo.Extended
```

检查版本：

```powershell
hugo version
```

## 克隆仓库

PaperMod 使用 Git submodule 管理，推荐克隆时带上 `--recurse-submodules`：

```powershell
git clone --recurse-submodules git@github.com:XClear0/blog.git
cd blog
```

如果已经克隆过仓库，但没有拉取 submodule，可以执行：

```powershell
git submodule update --init --recursive
```

## 本地开发

启动 Hugo 本地服务器：

```powershell
hugo server -D
```

默认访问地址：

```text
http://localhost:1313/
```

构建生产版本：

```powershell
hugo --minify
```

构建结果会生成到 `public/` 目录。

## 写文章

创建新文章：

```powershell
hugo new content posts/my-new-post.md
```

常见 front matter 示例：

```toml
+++
title = "My New Post"
date = 2026-05-07T12:00:00+08:00
draft = true
+++
```

文章准备发布时，将 `draft` 改为 `false`。

## 更新 Hugo

更新本地 Hugo：

```powershell
winget upgrade Hugo.Hugo.Extended
hugo version
```

GitHub Actions 当前使用：

```yaml
hugo-version: "latest"
extended: true
```

因此线上部署会使用 action 可安装的最新 Hugo Extended。

## 更新 PaperMod

PaperMod 是 submodule。更新主题时执行：

```powershell
git -C themes/PaperMod fetch --tags origin
git -C themes/PaperMod checkout master
git -C themes/PaperMod pull --ff-only origin master
git add themes/PaperMod
hugo --minify
git commit -m "Update PaperMod theme"
```

## 部署

部署流程位于 `.github/workflows/deploy.yml`。

每次 push 到 `main` 后，GitHub Actions 会：

1. 拉取仓库和 submodule。
2. 安装 Hugo Extended。
3. 执行 `hugo --minify` 构建站点。
4. 将 `public/` 上传到 VPS。

需要在 GitHub 仓库中配置以下 secrets：

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_PORT`

## 常用命令

查看仓库状态：

```powershell
git status --short --branch
```

查看 submodule 状态：

```powershell
git submodule status
```

拉取远端更新：

```powershell
git pull --rebase origin main
git submodule update --init --recursive
```

推送到 GitHub：

```powershell
git push origin main
```
