import os
import re
import shutil
import subprocess
import uuid
from typing import List

import scripts.params
from modules.shared import opts
from scripts.ext_logging import logger


def init_params(source_video, keep_target_fps, skip_target_audio, temp_frame_format,
                temp_frame_quality,
                output_video_encoder,
                output_video_quality):
    if source_video is None:
        return

    file_name = source_video.split("/")[-1]

    target_path = os.path.join(opts.videogen_result_dir, str(uuid.uuid4()))
    os.makedirs(target_path, exist_ok=True)
    target_path = os.path.join(target_path, file_name)

    shutil.move(source_video, target_path)

    logger.info("Source path: %s, %s", source_video, target_path)
    scripts.params.target_path = target_path
    scripts.params.keep_fps = keep_target_fps
    logger.info("Source path: %s", scripts.params.source_path)
    scripts.params.skip_audio = skip_target_audio
    scripts.params.temp_frame_format = temp_frame_format
    scripts.params.temp_frame_quality = temp_frame_quality
    scripts.params.output_video_encoder = output_video_encoder
    scripts.params.output_video_quality = output_video_quality
    scripts.params.log_level = "info"


def splitVideo(source_video, keep_target_fps, skip_target_audio, temp_frame_format,
               temp_frame_quality,
               output_video_encoder,
               output_video_quality):
    init_params(source_video, keep_target_fps, skip_target_audio, temp_frame_format,
                temp_frame_quality,
                output_video_encoder,
                output_video_quality)

    # extract frames
    if scripts.params.keep_fps:
        fps = detect_fps(scripts.params.target_path)
        logger.info('Extracting frames with %s FPS...', fps)
        extract_frames(scripts.params.target_path, fps)
    else:
        logger.info('Extracting frames with 30 FPS...')
        extract_frames(scripts.params.target_path)

    return get_temp_directory_path(scripts.params.target_path)


def detect_fps(target_path: str) -> float:
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of',
               'default=noprint_wrappers=1:nokey=1', target_path]
    output = subprocess.check_output(command).decode().strip().split('/')
    try:
        numerator, denominator = map(int, output)
        return numerator / denominator
    except Exception:
        pass
    return 30


def extract_frames(target_path: str, fps: float = 30) -> bool:
    temp_directory_path = get_temp_directory_path(target_path)
    temp_frame_quality = scripts.params.temp_frame_quality * 31 // 100
    os.makedirs(temp_directory_path, exist_ok=True)
    logger.info("temp_directory_path %s, temp_frame_quality %d", temp_directory_path, temp_frame_quality)
    return run_ffmpeg(
        ['-hwaccel', 'auto', '-i', target_path, '-q:v', str(temp_frame_quality), '-pix_fmt', 'rgb24', '-vf',
         'fps=' + str(fps), os.path.join(temp_directory_path, '%07d.' + scripts.params.temp_frame_format)])


def get_temp_directory_path(target_path: str) -> str:
    target_directory_path = os.path.dirname(target_path)
    return os.path.join(target_directory_path, "images")


def run_ffmpeg(args: List[str]) -> bool:
    commands = ['ffmpeg', '-hide_banner', '-loglevel', scripts.params.log_level]
    commands.extend(args)
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
        return True
    except Exception:
        pass
    return False


def mergeVideo():
    if scripts.params.keep_fps:
        fps = detect_fps(scripts.params.target_path)
        logger.info('Creating video with %s FPS...', fps)
        create_video(scripts.params.target_path, fps)
    else:
        logger.info('Creating video with 30 FPS...')
        create_video(scripts.params.target_path)

    # handle audio
    output_path = get_output_path()
    logger.info('skip_audio %s', scripts.params.skip_audio)
    if scripts.params.skip_audio:
        move_temp(scripts.params.target_path, output_path)
        logger.info('Skipping audio...')
    else:
        if scripts.params.keep_fps:
            logger.info('Restoring audio...')
        else:
            logger.info('Restoring audio might cause issues as fps are not kept...')
        restore_audio(scripts.params.target_path, output_path)
    # clean temp
    logger.info('Cleaning temporary resources...')
    clean_temp(scripts.params.target_path)

    return output_path


def get_temp_output_path(target_path: str, createPath=False) -> str:
    temp_directory_path = os.path.dirname(target_path)
    temp_directory_path = os.path.join(temp_directory_path, "video")
    if createPath:
        os.makedirs(temp_directory_path, exist_ok=True)
    return os.path.join(temp_directory_path, "temp.mp4")


def get_output_path():
    return os.path.join(opts.videogen_result_dir, str(uuid.uuid4()) + ".mp4")


def clean_temp(target_path: str) -> None:
    temp_directory_path = get_temp_directory_path(target_path)
    parent_directory_path = os.path.dirname(temp_directory_path)
    logger.info("temp_directory_path %s, parent_directory_path %s", temp_directory_path, parent_directory_path)
    if os.path.isdir(parent_directory_path):
        shutil.rmtree(parent_directory_path)


def move_temp(target_path: str, output_path: str) -> None:
    temp_output_path = get_temp_output_path(target_path)
    if os.path.isfile(temp_output_path):
        if os.path.isfile(output_path):
            os.remove(output_path)
        shutil.move(temp_output_path, output_path)


def rename_temp_image(folder_path: str):
    file_list = os.listdir(folder_path)
    file_list.sort()
    pattern = r'^\d{7}\.png$'
    for index, file_name in enumerate(file_list):
        if re.match(pattern, file_name):
            return
        new_filename = '{:07d}.png'.format(index + 1)
        src_path = os.path.join(folder_path, file_name)
        dst_path = os.path.join(folder_path, new_filename)
        shutil.move(src_path, dst_path)


def create_video(target_path: str, fps: float = 30) -> bool:
    temp_output_path = get_temp_output_path(target_path, True)
    temp_directory_path = get_temp_directory_path(target_path)
    rename_temp_image(temp_directory_path)
    output_video_quality = (scripts.params.output_video_quality + 1) * 51 // 100
    logger.info('temp_output_path: %s', temp_output_path)
    commands = ['-hwaccel', 'auto', '-r', str(fps), '-i',
                os.path.join(temp_directory_path, '%07d.' + scripts.params.temp_frame_format), '-c:v',
                scripts.params.output_video_encoder]
    if scripts.params.output_video_encoder in ['libx264', 'libx265', 'libvpx']:
        commands.extend(['-crf', str(output_video_quality)])
    if scripts.params.output_video_encoder in ['h264_nvenc', 'hevc_nvenc']:
        commands.extend(['-cq', str(output_video_quality)])
    commands.extend(['-pix_fmt', 'yuv420p', '-vf', 'colorspace=bt709:iall=bt601-6-625:fast=1', '-y', temp_output_path])
    return run_ffmpeg(commands)


def restore_audio(target_path: str, output_path: str) -> None:
    temp_output_path = get_temp_output_path(target_path)
    done = run_ffmpeg(
        ['-hwaccel', 'auto', '-i', temp_output_path, '-i', target_path, '-c:v', 'copy', '-map', '0:v:0', '-map',
         '1:a:0', '-y', output_path])
    if not done:
        move_temp(target_path, output_path)
