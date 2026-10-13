# Xincheng AI Skills

**实用 AI Skills 与自动化工作流合集 | Practical AI Skills & Workflows**

专注于 AI 辅助 PPT 制作、工程咨询、文档处理与效率提升。

A collection of practical AI skills for presentation creation, engineering consulting, document processing, and productivity automation.

## 项目介绍 | About

本项目用于分享个人开发和持续优化的 AI Skills，帮助用户通过 Codex 等支持 Skills 的 AI Agent 完成复杂任务。

重点关注：

- PPT 设计、重建与自动化
- AI 辅助文档处理
- 工程技术咨询工作流
- AI Agent 与办公效率提升

欢迎提出问题、分享使用经验和贡献改进建议。

## 已发布 Skills

### 1. image-to-ppt：图片转可编辑 PPT

[查看 Skill 详细说明](https://github.com/xincheng-ai-cq/xincheng-ai-skills/blob/main/image-to-ppt/SKILL.md)

**主要功能**

- 图片、截图重建为可编辑 PPT 页面
- PDF 中的文本、矢量对象和图片提取与重建
- 混合 PPT 中指定图片页面的原位替换
- 尽可能保留原始文字、版式、色彩、字体和布局
- 使用原生文本框、形状、表格和图表，提高编辑能力
- 支持 PPTX 结构检查与重建结果验证

**适用场景**

- 将已有 PPT 截图恢复为可编辑页面
- 将 PDF 演示文稿转换为可修改的 PPT
- 修改只有图片版本的历史汇报材料
- 重建复杂的技术汇报、工程咨询和商务演示页面

注意：本 Skill 是供 AI Agent 使用的任务指令与辅助脚本，并非独立的一键转换软件。实际运行需要具备相应的文档读取、PowerPoint 生成及验证工具，效果受输入质量和执行环境影响。

## 安装方法 | Installation

**方式一：手动安装**

1. 在 GitHub 项目主页点击 `Code` → `Download ZIP`。
2. 解压下载的文件。
3. 找到其中的 `image-to-ppt` 文件夹。
4. 将完整文件夹复制到你所使用的 AI Agent 的 Skills 安装目录。

例如，使用 Windows 上已配置共享 Skills 目录的 Codex 环境，可安装到：

`C:\Users\你的用户名\.agents\skills\image-to-ppt`

具体安装路径以你的 AI Agent 配置为准。

**方式二：使用 Git 工具**

也可以通过 Git 克隆整个仓库，再将需要的 Skill 安装到对应目录。

## 如何使用 | Usage

安装完成并确认 AI Agent 能够识别该 Skill 后，可以尝试输入：

> 请使用 image-to-ppt Skill，将我提供的 PPT 截图重建为可编辑的 PowerPoint，尽可能保留原有文字、配色和版式。

或者：

> 请检查这个 PPT，把其中整页为图片的幻灯片恢复为可编辑对象，保留其他幻灯片不变。

实际执行前，请确保 AI Agent 可以读取输入文件，并能够使用所需的 PPT 制作工具。

## 反馈与交流 | Feedback

欢迎反馈使用问题和改进建议！

- [提交 Bug 或功能建议（Issues）](https://github.com/xincheng-ai-cq/xincheng-ai-skills/issues)
- [查看项目源代码](https://github.com/xincheng-ai-cq/xincheng-ai-skills)
- 欢迎通过 Pull Request 提交改进

反馈时建议提供使用环境、操作步骤、预期效果和实际结果。请勿上传客户保密资料、个人敏感信息或 API 密钥。

## 后续计划 | Roadmap

- [x] 发布第一个 image-to-ppt Skill
- [ ] 补充实际使用案例与效果展示
- [ ] 完善跨平台安装说明
- [ ] 持续优化图片转 PPT 的重建流程
- [ ] 发布更多 PPT、文档处理和工程咨询类 Skills

## 许可证 | License

本项目采用 [MIT License](LICENSE) 开源许可证。

在遵守许可证条款的前提下，你可以自由使用、复制、修改、分发本项目，并将其用于个人或商业用途，但须保留原始版权和许可证声明。

项目中如包含第三方资源或依赖，其使用仍须遵守各自的许可证要求。

This project is licensed under the MIT License. You are free to use, modify, distribute, and use the project commercially, subject to the license terms.

## 支持项目 | Support

如果这个项目对你有帮助，欢迎点击 GitHub 页面右上角的 **Star ⭐** 收藏支持。

你的反馈将帮助项目持续改进。
