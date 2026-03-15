"""
Конвертация видеофайла с записью партии Го в файл SGF.
Использование: python main.py <путь_к_видео> [путь_к_выходному_sgf]
"""
import argparse
import sys
import traceback

import cv2
from ultralytics import YOLO

from GoBoard import GoBoard
from GoGame import GoGame
from GoVisual import GoVisual
import sente


def video_to_sgf(video_path: str, output_path: str, model_path: str = "model.pt") -> None:
    """
    Читает видео, распознаёт доску и ходы, записывает партию в SGF.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть видео: {video_path}")

    model = YOLO(model_path)
    game = sente.Game()
    go_visual = GoVisual(game)
    go_board = GoBoard(model)
    pipeline = GoGame(game, go_board, go_visual, transparent_mode=False)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    initialized = False
    frame_index = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_index += 1
            if total_frames > 0 and frame_index % 50 == 0:
                print(f"Обработано кадров: {frame_index}/{total_frames}")

            try:
                if not initialized:
                    pipeline.initialize_game(frame)
                    initialized = True
                else:
                    pipeline.main_loop(frame)
            except Exception as e:
                # Пропуск кадров, где доска не распознаётся
                if frame_index <= 1:
                    raise
                continue

        sgf_text = pipeline.get_sgf()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sgf_text)
        print(f"SGF сохранён: {output_path}")

    finally:
        cap.release()


def main():
    parser = argparse.ArgumentParser(description="Конвертация видео партии Го в SGF")
    parser.add_argument("video", help="Путь к видеофайлу")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Путь к выходному SGF (по умолчанию: имя видео с расширением .sgf)",
    )
    parser.add_argument("--model", default="model.pt", help="Путь к модели YOLO (по умолчанию: model.pt)")
    args = parser.parse_args()

    if args.output is None:
        base = args.video.rsplit(".", 1)[0] if "." in args.video else args.video
        args.output = base + ".sgf"

    try:
        video_to_sgf(args.video, args.output, args.model)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
