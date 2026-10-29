# 本地终剪：先验输入，再拼接

检查本机 `ffmpeg` / `ffprobe`，不自动安装。只处理已下载核验的素材，输出到新的工作目录，保留原始媒体。下面是两段视频的最小可执行示例，不是任意输入一键适用的整片脚本；按用户规格设置变量并逐步检查。示例重新编码，不承诺流拷贝、视觉无损或自动高清增强。

## 1. 探测与时间线计划

使用 `ffprobe -v error -show_streams -show_format -of json "$INPUT"` 检查视频/音频流、起始时间、时长、分辨率、帧率和旋转信息。不能把容器总长当成纯视频流时长；流时长未知时进一步检查帧时间或解码结果，不猜数值。

为每段选择完整动作所需的 DURATION，先与实际视频时长核对，不靠 `-t` 无意截掉台词或动作。输入不足不能静默延长或假装完整；需要冻帧、变速、裁剪须说明。按约定填 WIDTH、HEIGHT、FPS；数字不是模型生成默认值。

以下环境变量均由宿主填为已验证的本地路径/数值，路径必须引用；OUTPUT 为新文件。输入与输出不能相同。WIDTH/HEIGHT 用适合目标编码的正偶数，FPS/DURATION 为正数。示例保留宽高比并补黑边，不擅自裁掉画面。

## 2. 逐段规格统一

### 输入有音频

适用条件：INPUT 有可解码的视频和音频，且已验证两流实际起点一致；DURATION 不超出已验证视频长度。若起点不同，不能直接运行本示例：先按视频起点作为基准保留相对偏移，晚起的音轨补等量前置静音，早起的音轨裁去基准之前的部分，再重新探测确认。分别归零会丢失合法起点差，造成对白提前或延后。音频不足补尾部静音，过长则裁到与选定视频段一致。输出从 0 开始，音轨统一为 48 kHz 双声道。

```bash
# example: normalize-audio
if [ -e "$OUTPUT" ] || [ -L "$OUTPUT" ]; then
  printf 'Output already exists: %s\n' "$OUTPUT" >&2
  exit 1
fi
ffmpeg -hide_banner -loglevel error -nostdin -n -i "$INPUT" \
  -filter_complex_threads 1 \
  -filter_complex "[0:v:0]trim=duration=${DURATION},setpts=PTS-STARTPTS,scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS},format=yuv420p[v];[0:a:0]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration=${DURATION}[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -crf 18 -preset medium \
  -c:a aac -ar 48000 -movflags +faststart "$OUTPUT"
```

### 输入没有音频

不能引用不存在的 `0:a`；添加明确的静音轨，之后即可和有声音的片段使用同一剪辑路线。

```bash
# example: normalize-silent
if [ -e "$OUTPUT" ] || [ -L "$OUTPUT" ]; then
  printf 'Output already exists: %s\n' "$OUTPUT" >&2
  exit 1
fi
ffmpeg -hide_banner -loglevel error -nostdin -n -i "$INPUT" \
  -f lavfi -i 'anullsrc=r=48000:cl=stereo' -filter_complex_threads 1 \
  -filter_complex "[0:v:0]trim=duration=${DURATION},setpts=PTS-STARTPTS,scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS},format=yuv420p[v];[1:a:0]atrim=duration=${DURATION},asetpts=PTS-STARTPTS[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -crf 18 -preset medium \
  -c:a aac -ar 48000 -movflags +faststart "$OUTPUT"
```

## 3. 两段溶解转场示例

仅在用户需要溶解时使用；硬切不应强行变成溶解。A/B 是前一步归一化并重新探测的片段，具有相同画幅和帧率、有效音轨。DA/DB 是对齐后的段长，T 为重叠长度，必须满足 `0 < T < min(DA, DB)`。计算 OFFSET=DA−T，EXPECTED=DA+DB−T，然后传入下面变量；不能盲用容器时长计算。

```bash
# example: crossfade
if [ -e "$OUTPUT" ] || [ -L "$OUTPUT" ]; then
  printf 'Output already exists: %s\n' "$OUTPUT" >&2
  exit 1
fi
ffmpeg -hide_banner -loglevel error -nostdin -n -i "$A" -i "$B" \
  -filter_complex_threads 1 \
  -filter_complex "[0:v:0]settb=AVTB,setpts=PTS-STARTPTS[v0];[1:v:0]settb=AVTB,setpts=PTS-STARTPTS[v1];[v0][v1]xfade=transition=fade:duration=${T}:offset=${OFFSET},format=yuv420p[v];[0:a:0]atrim=duration=${DA},asetpts=PTS-STARTPTS[a0];[1:a:0]atrim=duration=${DB},asetpts=PTS-STARTPTS[a1];[a0][a1]acrossfade=d=${T}:c1=tri:c2=tri[a]" \
  -map '[v]' -map '[a]' -c:v libx264 -crf 18 -preset medium \
  -c:a aac -ar 48000 -movflags +faststart "$OUTPUT"
```

多段累计总长为各段长之和减去每次转场重叠之和；下一次 xfade offset 是当前合成长减去下一转场时长。硬切可用已统一规格的 concat filter；只有编码参数/时间戳等满足流拷贝要求时才考虑 concat demuxer，不能把带转场重编码描述为“原片一帧不改”。

## 4. 配乐、字幕、封面与局部修补

- 全片 BGM/旁白建立独立连续时间线，按最终总长裁切/补足，明确淡入淡出位置；需要保留原声时混音而非替换。先听音量和对白可懂度，不机械叠加导致削波。
- 原音轨转场和画面使用相同重叠区，并先对齐各段音视频起点/长度；仅两个 fade 参数相同不足以证明同步。
- 字幕、标题卡、封面按实际授权内容与字体配置制作。静态卡片若进入有声拼接路线，也必须补静音；字幕避免覆盖关键脸/道具。
- 局部尾段修补保留原件，清楚说明接点、重复/缺失帧和重编码范围。需要新的生成尾段时另行获得生成授权。

## 5. 验收

重新 ffprobe 验证视频/音频流、分辨率、帧率和实际总长，按帧时长与编码封装误差设定合理容差。检查镜头数量与顺序，缺镜/重复必须报错，不得打印“通过”。播放首尾和所有接点，听对白/BGM，核验字幕和结尾；只跑探测不能声称主观质量通过。

离线烟雾测试用合成的 2 秒有声片段和 3 秒无声片段，先统一规格，再以 0.5 秒转场连接，预期成片约 4.5 秒。测试不能证明真实生成素材或任意编码都可处理。
