import os
import shutil
import subprocess
from typing import List

import roop.globals
from modules.shared import opts
from scripts.ext_logging import logger


def init_params(source_video, keep_target_fps, skip_target_audio, keep_temporary_frames,
                many_faces):
    if source_video is None:
        return

    file_name = source_video.split("/")[-1]

    target_path = os.path.join(opts.videogen_result_dir, "tmp")
    os.makedirs(target_path, exist_ok=True)
    target_path = os.path.join(target_path, file_name)

    shutil.move(source_video, target_path)

    logger.info("Source path: %s, %s", source_video, target_path)
    roop.globals.target_path = target_path
    roop.globals.keep_fps = keep_target_fps
    logger.info("Source path: %s", roop.globals.source_path)
    roop.globals.skip_audio = skip_target_audio
    roop.globals.keep_frames = keep_temporary_frames
    roop.globals.many_faces = many_faces

    # program.add_argument('--reference-face-position', help='position of the reference face',
    #                      dest='reference_face_position', type=int, default=0)
    # program.add_argument('--reference-frame-number', help='number of the reference frame',
    #                      dest='reference_frame_number', type=int, default=0)
    # program.add_argument('--similar-face-distance', help='face distance used for recognition',
    #                      dest='similar_face_distance', type=float, default=0.85)
    # program.add_argument('--temp-frame-format', help='image format used for frame extraction', dest='temp_frame_format',
    #                      default='png', choices=['jpg', 'png'])
    # program.add_argument('--temp-frame-quality', help='image quality used for frame extraction',
    #                      dest='temp_frame_quality', type=int, default=0, choices=range(101), metavar='[0-100]')
    # program.add_argument('--output-video-encoder', help='encoder used for the output video',
    #                      dest='output_video_encoder', default='libx264',
    #                      choices=['libx264', 'libx265', 'libvpx-vp9', 'h264_nvenc', 'hevc_nvenc'])
    # program.add_argument('--output-video-quality', help='quality used for the output video',
    #                      dest='output_video_quality', type=int, default=35, choices=range(101), metavar='[0-100]')
    # program.add_argument('--max-memory', help='maximum amount of RAM in GB', dest='max_memory', type=int)
    # program.add_argument('--execution-provider', help='available execution provider (choices: cpu, ...)',
    #                      dest='execution_provider', default=['cpu'], choices=suggest_execution_providers(), nargs='+')
    # program.add_argument('--execution-threads', help='number of execution threads', dest='execution_threads', type=int,
    #                      default=suggest_execution_threads())
    # program.add_argument('-v', '--version', action='version', version=f'{roop.metadata.name} {roop.metadata.version}')

    # roop.globals.frame_processors = args.frame_processor
    # roop.globals.keep_fps = args.keep_fps
    # roop.globals.keep_frames = args.keep_frames
    # roop.globals.skip_audio = args.skip_audio
    # roop.globals.many_faces = args.many_faces
    roop.globals.reference_face_position = 0
    roop.globals.reference_frame_number = 0
    roop.globals.similar_face_distance = 0.85
    roop.globals.temp_frame_format = "png"
    roop.globals.temp_frame_quality = 0
    roop.globals.output_video_encoder = "libx264"
    roop.globals.output_video_quality = 35
    roop.globals.log_level = "info"
    # roop.globals.max_memory = args.max_memory
    # roop.globals.execution_providers = decode_execution_providers(args.execution_provider)
    # roop.globals.execution_threads = args.execution_threads


def splitVideo(source_video, keep_target_fps, skip_target_audio, keep_temporary_frames,
               many_faces):
    init_params(source_video, keep_target_fps, skip_target_audio, keep_temporary_frames,
                many_faces)

    # extract frames
    if roop.globals.keep_fps:
        fps = detect_fps(roop.globals.target_path)
        logger.info('Extracting frames with %s FPS...', fps)
        extract_frames(roop.globals.target_path, fps)
    else:
        logger.info('Extracting frames with 30 FPS...')
        extract_frames(roop.globals.target_path)

    return get_temp_directory_path(roop.globals.target_path)


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
    temp_frame_quality = roop.globals.temp_frame_quality * 31 // 100
    os.makedirs(temp_directory_path, exist_ok=True)
    logger.info("temp_directory_path %s, temp_frame_quality %d", temp_directory_path, temp_frame_quality)
    return run_ffmpeg(
        ['-hwaccel', 'auto', '-i', target_path, '-q:v', str(temp_frame_quality), '-pix_fmt', 'rgb24', '-vf',
         'fps=' + str(fps), os.path.join(temp_directory_path, '%04d.' + roop.globals.temp_frame_format)])


def get_temp_directory_path(target_path: str) -> str:
    target_name, _ = os.path.splitext(os.path.basename(target_path))
    target_directory_path = os.path.dirname(target_path)
    return os.path.join(target_directory_path, target_name)


def run_ffmpeg(args: List[str]) -> bool:
    commands = ['ffmpeg', '-hide_banner', '-loglevel', roop.globals.log_level]
    commands.extend(args)
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
        return True
    except Exception:
        pass
    return False


def mergeVideo():
    if roop.globals.keep_fps:
        fps = detect_fps(roop.globals.target_path)
        logger.info('Creating video with %s FPS...', fps)
        create_video(roop.globals.target_path, fps)
    else:
        logger.info('Creating video with 30 FPS...')
        create_video(roop.globals.target_path)

    # handle audio
    output_path = get_output_path()
    if roop.globals.skip_audio:
        move_temp(roop.globals.target_path, output_path)
        logger.info('Skipping audio...')
    else:
        if roop.globals.keep_fps:
            logger.info('Restoring audio...')
        else:
            logger.info('Restoring audio might cause issues as fps are not kept...')
        restore_audio(roop.globals.target_path, output_path)
    # clean temp
    logger.info('Cleaning temporary resources...')
    clean_temp(roop.globals.target_path)

    return output_path


def get_temp_output_path(target_path: str) -> str:
    temp_directory_path = get_temp_directory_path(target_path)
    return os.path.join(temp_directory_path, "video", "temp.mp4")


def get_output_path():
    return os.path.join(opts.videogen_result_dir, "temp.mp4")


def clean_temp(target_path: str) -> None:
    temp_directory_path = get_temp_directory_path(target_path)
    parent_directory_path = os.path.dirname(temp_directory_path)
    if not roop.globals.keep_frames and os.path.isdir(temp_directory_path):
        shutil.rmtree(temp_directory_path)
    if os.path.exists(parent_directory_path) and not os.listdir(parent_directory_path):
        os.rmdir(parent_directory_path)


def move_temp(target_path: str, output_path: str) -> None:
    temp_output_path = get_temp_output_path(target_path)
    if os.path.isfile(temp_output_path):
        if os.path.isfile(output_path):
            os.remove(output_path)
        shutil.move(temp_output_path, output_path)


def create_video(target_path: str, fps: float = 30) -> bool:
    temp_output_path = get_temp_output_path(target_path)
    temp_directory_path = get_temp_directory_path(target_path)
    output_video_quality = (roop.globals.output_video_quality + 1) * 51 // 100
    logger.info('temp_output_path: %s', temp_output_path)
    commands = ['-hwaccel', 'auto', '-r', str(fps), '-i',
                os.path.join(temp_directory_path, '%04d.' + roop.globals.temp_frame_format), '-c:v',
                roop.globals.output_video_encoder]
    if roop.globals.output_video_encoder in ['libx264', 'libx265', 'libvpx']:
        commands.extend(['-crf', str(output_video_quality)])
    if roop.globals.output_video_encoder in ['h264_nvenc', 'hevc_nvenc']:
        commands.extend(['-cq', str(output_video_quality)])
    commands.extend(['-pix_fmt', 'yuv420p', '-vf', 'colorspace=bt709:iall=bt601-6-625:fast=1', '-y', temp_output_path])
    return run_ffmpeg(commands)


def restore_audio(target_path: str, output_path: str) -> None:
    temp_output_path = get_temp_output_path(target_path)
    run_ffmpeg(['-hwaccel', 'auto', '-i', temp_output_path, '-i', target_path, '-c:v', 'copy', '-map', '0:v:0', '-map',
                '1:a:0', '-y', output_path])
