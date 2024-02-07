# GetBilibiliVideo：一个用于下载B站视频的开源命令行工具

## 项目简介

GetBilibiliVideo是一款旨在帮助用户从Bilibili网站下载视频或收藏夹内容的开源命令行程序。本项目通过简洁的命令行接口，允许用户灵活指定下载选项，如选择浏览器、硬件加速、编码格式以及缓存设置等。

### 功能特性

1. **链接抓取**：提供必选参数 `--url` 或 `-i` 来指定要下载的单个视频链接或收藏夹地址。

2. **自定义输出路径**：通过可选参数 `--output` 或 `-o` 指定视频保存路径，默认为当前工作目录。

3. **浏览器支持**：在获取cookies时可以选择不同的浏览器（Edge, Chrome, Firefox），默认为Edge。

4. **缓存功能**：启用 cookies 缓存以供后续使用，只需指定 `--cache` 参数。

5. **分页缓存**：对合集视频提供分页缓存功能，可通过 `--page` 或 `-p` 参数指定缓存的页数，默认缓存全部页面。

6. **硬件加速**：查询并支持FFmpeg硬件加速功能，根据系统可用的硬件加速器进行选择，列出可用的加速硬件供用户参考，使用 `--hwaccels` 参数。

7. **编码转换**：为了适配Windows平台播放，添加了将视频编码转换为H.264的功能，通过 `--libx264` 或 `--windows` 参数启用此功能，默认关闭。

### 使用示例

```bash
python gbv.py --url "https://www.bilibili.com/video/BV1UA4m1572K" --output "D:/Videos" --browser chrome --cache --page 2 --hwaccels vaapi --libx264
```

### 参数详解

- `--url` / `-i`: 必须提供，用于指定要下载的B站视频链接。
- `--output` / `-o`: 可选，设置下载视频的保存路径，默认为当前目录。
- `--browser` / `-b`: 可选，指定获取cookies时使用的浏览器（edge, chrome, firefox）。
- `--cache`: 可选，开启cookies缓存功能。
- `--page` / `-p`: 可选，设置下载合集视频的缓存页数，默认下载所有页。
- `--hwaccels`: 可选，启用FFmpeg硬件加速，并从检测到的硬件列表中选择一种。
- `--libx264` / `--windows`: 可选，启用H.264编码转换，便于在Windows平台上播放。

### 注意事项

请确保安装了FFmpeg，并正确配置了所需的硬件加速驱动。对于不支持的硬件加速选项，程序会发出警告信息并保持软件解码。

---

以上就是GetBilibiliVideo项目的简要介绍和使用说明，欢迎参与贡献代码或提出宝贵建议，共同优化和完善此项目。

![firefly](images/firefly.jpg)
