# resource_loader.jar 反编译结果

本目录包含 `resource_loader.jar` 的反编译结果，使用 `javap` 工具反编译得到。

## 文件结构

```
resource_loader_decompiled/
├── ai/guiji/duix/sdk/client/loader/
│   ├── ModelInfoLoader.java      # 主要的模型加载逻辑（1319行）
│   ├── ModelInfo.java            # 模型信息类（284行）
│   ├── ModelInfo$Frame.java     # 帧信息类
│   ├── ModelInfo$Region.java    # 区域信息类
│   └── VersionInfo.java          # 版本信息类
└── a/                            # 混淆的类
    ├── a.java                    # 文件读取工具类（64行）
    └── b.java                    # 统计上报类（420行）
```

## 核心代码逻辑分析

### 1. ModelInfoLoader - 模型加载器

#### 1.1 静态初始化（第 1241-1304 行）

在类加载时初始化两个 HashMap：

- **HashMap `a`**: 存储第一类文件的映射关系（从第一个路径加载）
  - `alpha_model.b` → `ab`
  - `alpha_model.p` → `ap`
  - `cacert.p` → `cp`

- **HashMap `b`**: 存储第二类文件的映射关系（从第二个路径加载）
  - `weight_168u.b` → `wb`
  - `wenet.o` → `wo` ⭐ **WeNet ONNX 模型**
  - `dh_model.b` → `db` ⭐ **NCNN bin 文件**
  - `dh_model.p` → `dp` ⭐ **NCNN param 文件**
  - `bbox.j` → `bj`
  - `config.j` → `cj`

#### 1.2 load() 方法（第 15-24 行）

**入口方法**：
```java
public static ModelInfo load(Context context, Object decryptor, String path1, String path2)
```

参数说明：
- `context`: Android 上下文
- `decryptor`: 解密器对象（通过反射调用 `processmd5` 方法）
- `path1`: 第一类文件的目录路径
- `path2`: 第二类文件的目录路径

#### 1.3 核心加载流程 `a()` 方法（第 36-2018 行）

**第一阶段：处理第一类文件（HashMap `a`，第 70-255 行）**

1. 遍历 HashMap `a` 中的每个文件映射
2. 检查解密后的文件（如 `ab`, `ap`, `cp`）是否已存在
3. 如果不存在，检查加密文件（如 `alpha_model.b`）是否存在
4. 如果加密文件存在：
   - 通过反射调用 `decryptor.processmd5()` 方法解密
   - 解密后的文件先保存为 `.tmp` 临时文件
   - 解密完成后重命名为最终文件名
5. 如果任何必需文件缺失，返回 `null`

**第二阶段：处理第二类文件（HashMap `b`，第 256-465 行）**

1. 遍历 HashMap `b` 中的每个文件映射
2. 同样的解密流程，但文件路径使用 `path2`
3. 特殊处理：`weight_168u.b` 文件如果不存在不会导致失败

**第三阶段：读取配置文件（第 466-505 行）**

1. 读取 `bbox.j` 文件（通过 `a/a.a()` 方法读取文件内容）
2. 解析为 JSONObject
3. 读取 `config.j` 文件并解析
4. 从 `config.j` 中提取：
   - `need_png`: 是否需要 PNG 文件
   - `modelkind`: 模型类型
   - `width`: 默认 540
   - `height`: 默认 960

**第四阶段：加载帧数据（第 506-940 行）**

1. 扫描 `raw_jpgs` 目录下的所有图片文件
2. 为每个图片文件创建 `ModelInfo$Frame` 对象：
   - `index`: 从文件名提取（去掉扩展名）
   - `rawPath`: 原始图片路径
   - `maskPath`: 如果 `hasMask=true`，从 `pha` 目录查找对应的 mask 文件
   - `sgPath`: 如果 `hasMask=true`，从 `raw_sg` 目录查找对应的文件
   - `rect`: 从 `bbox.j` JSON 中根据 index 获取边界框 `[x1, x2, y1, y2]`

3. **人脸处理流程**（从Frame到模型输入）：
   - **Step 1**: 使用 `rect` 从原始图像中裁剪人脸区域（约276×276px）
   - **Step 2**: 将裁剪的人脸 `resize` 到 168×168 像素
   - **Step 3**: 从168×168图像中心裁剪160×160区域（坐标(4,4)到(164,164)）
   - **Step 4**: 创建mask图像（在160×160基础上绘制黑色矩形遮挡部分区域）
   - **Step 5**: 合并真实图像和mask为6通道输入，送入模型推理
3. 验证每个 Frame（调用 `check()` 方法）：
   - 必须有 `rawPath`
   - 必须有 `rect`
4. 按 `index` 排序所有 Frame

**第五阶段：解析动作区域（第 941-1737 行）**

1. 读取 `SpecialAction.json` 文件（如果存在）
2. 解析 `duixAppointInterval` 配置：
   - **静音区域（silences）**：
     - 从 JSON 中读取 `silences` 数组
     - 每个静音区域包含 `name` 和 `action`（帧范围 `[start, end]`）
     - 创建 `TYPE_SILENCE` 类型的 Region
     - 将范围内的 Frame 添加到 Region
   - **动作区域（actions）**：
     - 从 JSON 中读取 `actions` 数组
     - 创建 `TYPE_MOTION` 类型的 Region
     - 标记起始帧（`startFlag=true`）和结束帧（`endFlag=true`）
     - 设置 `actionName`
   - **范围区域（ranges）**：
     - 从 `config.j` 中读取 `ranges` 数组
     - 根据 `type` 字段创建对应的 Region（0=静音，1=动作）

**第六阶段：设置模型文件路径（第 1738-2003 行）**

1. 设置 WeNet 模型路径：
   ```java
   setWenetfn(path1 + File.separator + "wo")
   ```
   - 解密后的 `wenet.o` 文件重命名为 `wo`

2. 设置 NCNN 模型路径：
   ```java
   setUnetbin(path2 + File.separator + "db")  // dh_model.b → db
   setUnetparam(path2 + File.separator + "dp") // dh_model.p → dp
   ```

3. 设置权重文件路径：
   ```java
   setUnetmsk(path2 + File.separator + "wb")   // weight_168u.b → wb
   ```
   - 优先从 `path2` 查找，如果不存在则从 `path1` 查找

### 2. ModelInfo - 数据模型类

存储模型的所有配置信息：

- **基础信息**：
  - `width`, `height`: 模型输入尺寸（默认 540x960）
  - `hasMask`: 是否有 mask 通道
  - `modelkind`: 模型类型

- **文件路径**：
  - `wenetfn`: WeNet ONNX 模型路径
  - `unetbin`: NCNN bin 文件路径
  - `unetparam`: NCNN param 文件路径
  - `unetmsk`: 权重文件路径

- **帧和区域信息**：
  - `frames`: List<Frame> - 所有帧的列表
  - `silenceRegion`: Region - 静音区域
  - `motionRegions`: List<Region> - 动作区域列表

### 3. ModelInfo$Frame - 帧信息类

表示一帧图像的信息：

- `index`: 帧索引
- `rawPath`: 原始图片路径
- `maskPath`: Mask 图片路径（可选）
- `sgPath`: SG 图片路径（可选）
- `rect`: 边界框 `[x, y, w, h]`
- `startFlag`: 是否为动作起始帧
- `endFlag`: 是否为动作结束帧
- `actionName`: 动作名称

**check() 方法**：验证 Frame 是否有效（必须有 rawPath 和 rect）

### 4. ModelInfo$Region - 区域信息类

表示一个动作或静音区域：

- `type`: 区域类型（`TYPE_SILENCE=0` 或 `TYPE_MOTION=1`）
- `name`: 区域名称
- `frames`: 该区域包含的帧列表

### 5. a/a - 文件读取工具类

**a() 方法**（第 3-44 行）：
- 功能：读取文件内容为字符串
- 实现：使用 `BufferedReader` 逐行读取文件
- 用途：读取 JSON 配置文件（`config.j`, `bbox.j`, `SpecialAction.json`）

### 6. a/b - 统计上报类

**run() 方法**（第 17-420 行）：
- 功能：异步上报设备信息到服务器
- 上报内容：
  - 屏幕尺寸
  - 设备信息（制造商、型号、Android 版本）
  - 应用信息（包名、版本号）
  - SDK 版本
- 上报地址：`https://vshow.guiji.ai/duix-guiji-cn/sysEventReport/report`

## 关键发现

### 文件映射关系

从 `ModelInfoLoader.java` 的静态初始化代码中（第 1280-1281 行），可以看到加密文件到解密后文件的映射：

- `wenet.o` → `wo` (WeNet ONNX 模型)
- `dh_model.p` → `dp` (NCNN param 文件)
- `dh_model.b` → `db` (NCNN bin 文件)
- `weight_168u.b` → `wb` (权重文件)
- `config.j` → `cj` (配置文件)
- `bbox.j` → `bj` (边界框文件)
- `alpha_model.p` → `ap`
- `alpha_model.b` → `ab`
- `cacert.p` → `cp`

### 解密机制

1. **解密方法**：通过反射调用 `decryptor.processmd5(File outputFile, File inputFile, int mode)` 方法
2. **解密流程**：
   - 输入：加密文件（如 `wenet.o`）
   - 输出：临时文件（如 `wo.tmp`）
   - 解密完成后重命名为最终文件名（如 `wo`）
3. **解密模式**：`mode` 参数为 `0`（从字节码中可以看到）

### 配置文件结构

#### config.j
```json
{
  "need_png": 0,
  "modelkind": 0,
  "width": 540,
  "height": 960,
  "ranges": [
    {
      "min": 0,
      "max": 100,
      "type": 0  // 0=静音, 1=动作
    }
  ]
}
```

#### bbox.j
```json
{
  "0": [x1, x2, y1, y2],  // 帧索引 -> 边界框 [水平边界, 垂直边界]
  "1": [x1, x2, y1, y2],   // ⚠️ 注意: 非标准的坐标格式
  ...
}
```

**格式说明**:
- `x1, x2`: 水平方向的边界坐标
- `y1, y2`: 垂直方向的边界坐标
- **⚠️ 重要**: 这不是标准的 `[x, y, w, h]` 或 `[x1, y1, x2, y2]` 格式

#### SpecialAction.json
```json
{
  "duixAppointInterval": {
    "silences": [
      {
        "name": "静音区域名称",
        "action": [start_frame, end_frame]
      }
    ],
    "actions": [
      {
        "name": "动作名称",
        "action": [start_frame, end_frame]
      }
    ]
  }
}
```

## 反编译工具

使用 `tools/decompile_resource_loader.py` 可以重新反编译：

```bash
python tools/decompile_resource_loader.py \
    ../duix-android/dh_aigc_android/duix-sdk/libs/resource_loader.jar \
    resource_loader_decompiled
```

## 注意事项

- 这些是反编译的字节码，不是原始源代码
- 类名 `a/a` 和 `a/b` 是经过 R8 混淆的
- 代码逻辑完整，但变量名和方法名可能不是原始的
- 反编译结果仅供参考，用于理解 SDK 的文件加载机制
- 解密方法 `processmd5` 的具体实现不在这个 JAR 中，需要通过其他方式获取

