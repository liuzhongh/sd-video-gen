import roop.globals
from roop.utilities import detect_fps, extract_frames, get_temp_frame_paths


def init_params(source_video, keep_target_fps, skip_target_audio, keep_temporary_frames,
                many_faces):
    print(f"{source_video}")
    roop.globals.target_path = source_video
    roop.globals.keep_fps = keep_target_fps
    print(f"{roop.globals.source_path}")
    roop.globals.skip_audio = skip_target_audio
    roop.globals.keep_frames = keep_temporary_frames
    roop.globals.many_faces = many_faces

    # roop.globals.frame_processors = args.frame_processor
    # roop.globals.keep_fps = args.keep_fps
    # roop.globals.keep_frames = args.keep_frames
    # roop.globals.skip_audio = args.skip_audio
    # roop.globals.many_faces = args.many_faces
    # roop.globals.reference_face_position = args.reference_face_position
    # roop.globals.reference_frame_number = args.reference_frame_number
    # roop.globals.similar_face_distance = args.similar_face_distance
    # roop.globals.temp_frame_format = args.temp_frame_format
    # roop.globals.temp_frame_quality = args.temp_frame_quality
    # roop.globals.output_video_encoder = args.output_video_encoder
    # roop.globals.output_video_quality = args.output_video_quality
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
        print(f'Extracting frames with {fps} FPS...')
        extract_frames(roop.globals.target_path, fps)
    else:
        print('Extracting frames with 30 FPS...')
        extract_frames(roop.globals.target_path)

    return get_temp_frame_paths(roop.globals.target_path)
