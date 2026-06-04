# ComfyUI-YUAN 整合包
Bernini功能是 `ComfyUI-RH-Bernini` 的增强复刻版，集成了 `ComfyUI-WanAnimatePlus` 的多参考图（Multi-Reference）功能，并保留了 `ComfyUI-YUAN` 的 Qwen-VL 推理节点。

## 主要功能

1.  **Bernini Conditioning (Plus)**:
    *   支持多张参考图输入（Multi-Reference Images）。
    *   自动任务推理（t2v, v2v, rv2v, r2v 等）。
    *   集成了 Bernini 核心补丁，支持 Wan2.2-A14B 模型。
2.  **Bernini Prompt Enhancer**:
    *   官方 Bernini 提示词增强逻辑，支持多种任务类型。
    *   输出系统提示词和用户提示词，可对接外部 LLM 节点。
3.  **Qwen-VL 集成**:
    *   保留了原有的 Qwen-VL 模型加载与推理节点。
    *   支持图片、视频抽帧、纯文本等多种推理模式。

## 安装方法

1.  将本项目文件夹放入 `ComfyUI/custom_nodes/` 目录下。
2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
3.  重启 ComfyUI。

## 节点说明

*   **Bernini Conditioning (Plus)**: 用于构建 Bernini 任务的条件。
*   **Qwen VL 图像推理**: 可用于辅助生成 Bernini 所需的增强提示词。



## 插件列表

- **Qwen VL 模型加载器**: 加载 Qwen3-VL, Qwen3.5-VL 或 Qwen3.6-VL GGUF 模型
- **Qwen VL 图像推理**: 进行图片/视频理解推理
- **Qwen VL 卸载模型**: 手动释放显存

### 1. Qwen VL 图像推理 (QwenVL)

#### 主要特性

- **支持模型**: Qwen3-VL, Qwen3.5-VL, **Qwen3.6-VL** (GGUF 格式)。
- **多模态能力**: 支持加载视觉投影模型 (mmproj)，实现图文混合输入。
- **灵活模式**:
  - **图片模式**: 分析单张图片。
  - **逐帧模式**: 对视频序列的每一帧单独进行描述。
  - **视频模式**: 抽取关键帧，作为整体上下文进行视频内容理解。
  - **纯文本模式**: 仅进行文本聊天，无需图片输入。
- **智能显存管理**:
  - 提供独立的"卸载模型"节点，手动释放显存。
  - **自动重加载机制**: 模型卸载后，再次运行推理节点时，会自动检测并重新加载模型。
- **参数微调**: 支持温度 (Temperature), Top-P, Top-K, 重复惩罚等完整生成参数控制。

#### 安装步骤

1. 将本插件文件夹复制到 ComfyUI 的自定义节点目录：`ComfyUI/custom_nodes/ComfyUI-YUAN_ALL/`
2. 进入插件目录，安装必要的 Python 库：
   ```bash
   cd ComfyUI/custom_nodes/ComfyUI-YUAN_ALL
   pip install -r requirements.txt
   ```

#### 节点列表

- **Qwen VL 模型加载器**: 加载 Qwen3-VL, Qwen3.5-VL 或 Qwen3.6-VL GGUF 模型 (默认加载 Qwen3.6-VL)
- **Qwen VL 图像推理**: 进行图片/视频理解推理
- **Qwen VL 卸载模型**: 手动释放显存

---

### 2. 文本段落分割 (YUAN_TXT)

文本段落分割 - 复刻终极修复版 V9

#### 主要功能

##### 1. 核心分段逻辑
- **端口**：严格按输入端口 (any_x) 分割文本。
- **空行**：识别双换行符进行分割。
- **序号**：识别 1. / (1) / A. / 一、 等列表标记进行分割。
- **段落**：每一行算一段。
- **标题**：智能识别章节标题（如"第一章"、"# 标题"）。
- **数字**：仅提取文本中的纯数字。
- **地址**：智能从字符串中提取 Windows 文件路径（如 `D:\Data\img.png`）并自动清洗。
- **手动**：识别 `|||` 分隔符进行自定义分割。

##### 2. 文本清洗 (段落优化)
- **开启**：自动删除每段文本开头和结尾的空格、换行符，防止拼接出现多余空行。
- **关闭**：完全保留原始文本的格式和缩进。

##### 3. 输出模式 (主输出控制)
- **关闭**：`总段` 端口输出处理并拼接好的完整文本（受 `选取段落` 规则影响）。
- **开启**：`总段` 端口输出一个列表，包含由 `选取段落` 和 `筛选段落` 规则处理后的所有段落。

##### 4. 动态端口扩展
- **输入端口**：设置 `any_x` 的数量，用于按顺序拼合多个文本源。
- **输出段落**：设置右侧 `段落x` 端口的数量，将分段后的内容独立输出。
- *注意：修改数值后需点击节点上的"更新端口"按钮生效。*

##### 5. 高级选取与筛选
- **选取段落**：输入例如 `1,3,5` 仅保留特定段落，输入 `0` 或留空保留所有。
- **筛选段落**：在 `输出模式` 开启时，指定提取第几段内容。如果 `筛选段落` 为 `0`，则输出所有选取的段落。

#### 节点列表

- **文本段落分割**: 多种分段模式的文本处理工具

---

## 鸣谢

*   [ComfyUI-RH-Bernini](https://github.com/RH-RunningHub/ComfyUI-RH-Bernini)
*   [ComfyUI-WanAnimatePlus](https://github.com/wuwukaka/ComfyUI-WanAnimatePlus)
整合了 QwenVL 图像推理和 YUAN_TXT 文本处理两大功能。
