# Android端数据流向分析

## 📱 整体架构

Android DUIX SDK采用多线程架构，核心组件包括：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DUIX.java     │───▶│  RenderThread   │───▶│   DuixNcnn      │
│ (Java API层)    │    │ (渲染线程)      │    │ (Native层)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  AudioPlayer    │    │   RenderSink    │    │   NCNN推理      │
│ (音频播放)      │    │ (视频渲染)      │    │ (C++实现)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 数据流向

### 1. 初始化阶段

```java
// DUIX.java - 主入口
public void init() {
    // 1. 检查模型文件完整性
    File duixDir = mContext.getExternalFilesDir("duix");
    File baseConfigDir = new File(duixDir + "/model/gj_dh_res");
    File modelDir = new File(duixDir + "/model", modelName);

    // 2. 创建RenderThread
    mRenderThread = new RenderThread(mContext, modelDir, renderSink, mVolume, callback);

    // 3. RenderThread初始化NCNN模型
    // 调用 DuixNcnn.initMunet() 或 initMunetex()
}
```

### 2. 模型加载流程

**Java层 (RenderThread.java):**
```java
// 加载模型信息
ModelInfo info = ModelInfoLoader.load(mContext, scrfdncnn, duixDir + "/model/gj_dh_res", modelDir);

// 初始化NCNN
scrfdncnn.alloc(0, 20, info.getWidth(), info.getHeight());
scrfdncnn.initPcmex(0,10,20,50,0);

// 使用自定义路径或默认路径
String paramPath = customParamPath != null ? customParamPath : info.getUnetparam();
String binPath = customBinPath != null ? customBinPath : info.getUnetbin();

// 初始化U-Net模型
if (info.getModelkind() > 0){
    scrfdncnn.initMunetex(paramPath, binPath, info.getUnetmsk(), info.getModelkind());
} else {
    scrfdncnn.initMunet(paramPath, binPath, info.getUnetmsk());
}

// 初始化Wenet语音模型
scrfdncnn.initWenet(info.getWenetfn());
```

**Native层 (DuixNcnn.java):**
```java
// JNI接口
public native int initMunet(String fnparam, String fnbin, String fnmask);
public native int initMunetex(String fnparam, String fnbin, String fnmask, int kind);
public native int initWenet(String fnwenet);
public native int initDirect(String fnparam, String fnbin, String fnmask, String fnwenet,
                           int width, int height, int kind);
```

### 3. 推理流程

#### 音频处理流程

```java
// 1. 创建会话
long sessionId = scrfdncnn.newsession();

// 2. 推送音频数据
scrfdncnn.pushpcm(sessionId, audioData, size, kind);

// 3. 查询推理结果数量
int readyCnt = scrfdncnn.readycnt(sessionId);

// 4. 获取推理结果
int result = scrfdncnn.filerst(sessionId, imagePath, maskPath, bbox, "",
                              index, rawBuffer, maskBuffer, bufferSize);
```

#### 图像处理流程

```java
// 1. 读取图像文件
int result = scrfdncnn.fileload(imagePath, maskPath, width, height,
                               rawBuffer, maskBuffer, bufferSize);

// 2. 或直接处理缓冲区数据
int result = scrfdncnn.bufrst(sessionId, bbox, index, imageBuffer, bufferSize);
```

### 4. 数据格式

#### BBox坐标格式
```json
{
  "frame_id": [x1, x2, y1, y2]
}
```

- **x1, x2**: 水平方向的边界坐标
- **y1, y2**: 垂直方向的边界坐标
- **坐标系**: 图像左上角为原点，右下为正方向
- **⚠️ 注意**: 这是一个**非标准的格式**，不是常见的[x1, y1, x2, y2]

#### 图像处理流程
```
原始图像 (540×960)
    ↓ 读取bbox坐标 [x1, x2, y1, y2]
人脸区域 (276×276) *
    ↓ resize到168×168
中心裁剪 (160×160) **
    ↓ 创建mask图像并合并
模型输入 (160×160×6)
    ↓ NCNN推理
生成结果 (160×160×3)
    ↓ resize回原人脸尺寸
    ↓ 融合到原始图像
最终输出 (540×960)
```

*注: 基于正确解析的bbox格式，人脸区域约为276×276像素  
**注: 从168×168图像中心裁剪160×160区域，实际输入模型的尺寸

#### 音频数据格式
- **格式**: PCM数据
- **采样率**: 16kHz
- **处理**: 20帧滑动窗口，步长1帧
- **输出**: 256维特征向量

### 5. 线程模型

#### RenderThread (主渲染线程)
```java
public class RenderThread extends Thread {
    // 消息队列处理
    private static final int MSG_RENDER_STEP = 1;
    private static final int MSG_STOP_RENDER = 2;
    private static final int MSG_PUSH_AUDIO = 12;

    // 核心方法
    private long renderStep() {
        // 处理一帧渲染
        ModelInfo.Frame frame = mPreviewQueue.poll();

        if (frame != null) {
            // 调用NCNN推理
            scrfRst = scrfdncnn.filerst(...);

            // 发送渲染结果
            mRenderSink.onVideoFrame(new ImageFrame(...));
        }
    }
}
```

#### AudioPlayer (音频播放线程)
```java
// 音频播放回调
public interface AudioPlayerCallback {
    void onPlayStart();
    void onPlayEnd();
    void onPlayError(int code, String message);
}
```

### 6. 关键接口

#### DuixNcnn JNI接口
```java
// 模型管理
int alloc(int taskid, int mincalc, int width, int height);
int free(int taskid);
int initMunet(String param, String bin, String mask);
int initWenet(String wenet);

// 会话管理
long newsession();
int finsession(long sessid);
int pushpcm(long sessid, byte[] data, int size, int kind);

// 推理接口
int filerst(long sessid, String imgPath, String maskPath,
           int[] bbox, String outPath, int index,
           byte[] rawBuf, byte[] maskBuf, int bufSize);
int bufrst(long sessid, int[] bbox, int index,
          byte[] imgBuf, int bufSize);
```

### 7. 数据流总结

```
输入数据流:
音频文件 → AudioPlayer → NCNN音频编码 → 特征向量
视频帧 → 读取bbox → 裁剪人脸 → resize → NCNN图像编码

推理过程:
音频特征 + 人脸图像 → U-Net推理 → 生成结果

输出数据流:
生成结果 → resize回原尺寸 → 融合到原图 → RenderSink → 显示
```

### 8. 性能优化

#### 内存管理
- 使用ByteBuffer进行零拷贝数据传递
- 预分配固定大小的缓冲区
- 复用会话对象避免重复创建

#### 多线程
- 音频播放和视频渲染分离
- 使用ConcurrentLinkedQueue线程安全通信
- 消息队列处理异步事件

#### 资源管理
- 按需加载模型文件
- 支持模型热切换
- 自动释放资源防止泄漏

### 9. 错误处理

#### 回调机制
```java
public interface Callback {
    void onEvent(int eventType, String message, Object data);
}

// 事件类型常量
Constant.CALLBACK_EVENT_INIT_READY
Constant.CALLBACK_EVENT_INIT_ERROR
Constant.CALLBACK_EVENT_AUDIO_PLAY_START
```

#### 日志系统
```java
// 详细的错误日志
Logger.i("scrfdncnn.filerst bnf index: " + bnfIndex + " rst: " + scrfRst);
Logger.e("Model initialization failed: " + errorMessage);
```

这个Android端数据流向分析为逆向工程和跨平台移植提供了重要参考。