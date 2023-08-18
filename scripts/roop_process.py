import roop.globals
from roop.utilities import detect_fps, extract_frames, get_temp_frame_paths
from modules.shared import opts
from scripts.ext_logging import logger


def init_params(source_video, keep_target_fps, skip_target_audio, keep_temporary_frames,
                many_faces):
    logger.info("Source path: %s, %s", source_video, opts.videogen_result_dir)
    roop.globals.target_path = source_video
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

    return get_temp_frame_paths(roop.globals.target_path)
