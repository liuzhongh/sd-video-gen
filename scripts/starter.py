import os
import sys
from pathlib import Path
import gradio as gr
from modules.shared import opts, OptionInfo
from modules import shared, paths, script_callbacks
from scripts.roop_process import splitVideo, mergeVideo


def init_ui():
    with gr.Blocks(analytics_enabled=False) as videogen_ui:
        with gr.Row().style(equal_height=False):
            with gr.Column(variant='panel'):
                with gr.Tabs(elem_id="videogen_source_video"):
                    with gr.TabItem('Step One'):
                        with gr.Column(variant='panel'):
                            source_video = gr.Video(label="Source Video", source="upload", type="filepath").style(width=256)
                            keep_target_fps = gr.Checkbox(label="Keep target fps", value=True)
                            skip_target_audio = gr.Checkbox(label="Skip target audio", value=False)
                            temp_frame_format = gr.Radio(['jpg', 'png'], value='png', label='Image format used for frame extraction')
                            temp_frame_quality = gr.Slider(label="Image quality used for frame extraction", step=1, maximum=100, value=0)
                            output_video_encoder = gr.Radio(['libx264', 'libx265', 'libvpx-vp9', 'h264_nvenc', 'hevc_nvenc'], value='libx264',
                                                         label='Encoder used for the output video')
                            output_video_quality = gr.Slider(label="Quality used for the output video", step=1,
                                                           maximum=100, value=35)
                            submit = gr.Button("Generate", elem_id="images_generate", variant='primary')
                            images_tmp_path = gr.Textbox(label='Path to split video to generate images', lines=1,
                                                         redonly=True)
                            submit.click(fn=splitVideo,
                                         inputs=[source_video,
                                                 keep_target_fps,
                                                 skip_target_audio,
                                                 temp_frame_format,
                                                 temp_frame_quality,
                                                 output_video_encoder,
                                                 output_video_quality
                                                 ],
                                         outputs=[images_tmp_path])
                    with gr.TabItem('Step Two'):
                        with gr.Column(variant='panel'):
                            gr.Markdown(f"将第一步视频分解的图片放入controlnet中进行批量处理")
                    with gr.TabItem('Step Three'):
                        with gr.Column(variant='panel'):
                            gen_video = gr.Video(label="Generated video", format="mp4").style(width=256)
                            submit = gr.Button("Generate", elem_id="video_generate", variant="second")
                            submit.click(fn=mergeVideo,
                                         outputs=[gen_video])
    return videogen_ui


def on_ui_tabs():
    result_dir = opts.videogen_result_dir
    os.makedirs(result_dir, exist_ok=True)

    video_to_video = init_ui()

    return [(video_to_video, "Video Gen", "videogen_interface")]


def on_ui_settings():
    video_path = Path(paths.script_path) / "outputs"
    section = ('videogen_interface', "VideoGen")
    opts.add_option("videogen_result_dir",
                    OptionInfo(str(video_path / "VideoGen/"), "Path to save results of VideoGen", section=section))


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
