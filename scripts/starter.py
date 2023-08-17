import os
import sys
from pathlib import Path
import gradio as gr
from modules.shared import opts, OptionInfo
from modules import shared, paths, script_callbacks


def submit_fn():
    print('hiiii')


def init_ui():
    with gr.Blocks(analytics_enabled=False) as videogen_ui:
        with gr.Row().style(equal_height=False):
            with gr.Column(variant='panel'):
                with gr.Tabs(elem_id="videogen_source_video"):
                    with gr.TabItem('Step One'):
                        with gr.Column(variant='panel'):
                            source_video = gr.Video(label="Source Video", source="upload", type="filepath")
                            keep_target_fps = gr.Checkbox(label="Keep target fps", value=True)
                            skip_target_audio = gr.Checkbox(label="Skip target audio", value=False)
                            keep_temporary_frames = gr.Checkbox(label="Keep temporary frames", value=True)
                            many_faces = gr.Checkbox(label="Many faces", value=False)
                            submit = gr.Button("Generate", elem_id="images_generate", variant='primary')
                            images_tmp_path = gr.Textbox(label='Path to split video to generate images', lines=1,
                                                         redonly=True)
                            submit.click(fn=submit_fn,
                                         inputs=[source_video,
                                                 keep_target_fps,
                                                 skip_target_audio,
                                                 keep_temporary_frames,
                                                 many_faces
                                                 ],
                                         outputs=[images_tmp_path])
                    with gr.TabItem('Step Two'):
                        with gr.Column(variant='panel'):
                            gr.Markdown(f"将第一步由视频分解的图片{images_tmp_path}放入controlnet中进行批量处理")
                    with gr.TabItem('Step Three'):
                        with gr.Column(variant='panel'):
                            gen_video = gr.Video(label="Generated video", format="mp4").style(width=256)
                            submit = gr.Button("Generate", elem_id="video_generate")
                            submit.click(fn=submit_fn,
                                         inputs=[source_video,
                                                 keep_target_fps,
                                                 skip_target_audio,
                                                 keep_temporary_frames,
                                                 many_faces
                                                 ],
                                         outputs=[gen_video])
    return videogen_ui


def on_ui_tabs():
    sys.path.extend([paths.script_path + '/extensions/sd-video-gen'])

    repo_dir = paths.script_path + '/extensions/sd-video-gen/'

    result_dir = opts.videogen_result_dir
    os.makedirs(result_dir, exist_ok=True)

    # from app_sadtalker import sadtalker_demo
    #
    # video_to_video = sadtalker_demo(checkpoint_path=checkpoint_path, config_path=repo_dir + 'src/config',
    #                                 warpfn=wrap_queued_call)
    video_to_video = init_ui()

    return [(video_to_video, "Video Gen", "extension")]


def on_ui_settings():
    video_path = Path(paths.script_path) / "outputs"
    section = ('extension', "VideoGen")
    opts.add_option("videogen_result_dir",
                    OptionInfo(str(video_path / "VideoGen/"), "Path to save results of VideoGen", section=section))


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
