import k_diffusion.sampling


def init_params(source_path, target_path, output_path, keep_temporary_frames,
                many_faces):
    print(f"{source_path}")
    import roop.globals
    roop.globals.source_path = source_path
    roop.globals.target_path = target_path
    roop.globals.output_path = output_path
    print(f"{roop.globals.source_path}")
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


def splitVideo(source_path, target_path, output_path, keep_temporary_frames,
               many_faces):
    init_params(source_path, target_path, output_path, keep_temporary_frames,
                many_faces)
