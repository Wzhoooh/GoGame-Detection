#!/bin/bash
# Скрипт для Google Colab: обход ошибки клонирования и установки sente на Python 3.12.
# Использование: задайте VIDEO_PATH и выполните в ячейке: !bash run_colab.sh

set -e

VIDEO_PATH="${VIDEO_PATH:-/content/drive/MyDrive/Го/video_2026-03-15_21-24-20.mp4}"

# 1) Работа с репозиторием: если папка есть — обновляем, иначе клонируем
if [ -d "GoGame-Detection" ]; then
  echo "Каталог GoGame-Detection уже есть, обновляю..."
  cd GoGame-Detection
  git fetch origin
  git checkout convert-videofile 2>/dev/null || true
  git pull origin convert-videofile 2>/dev/null || true
  cd ..
else
  git clone https://github.com/Wzhoooh/GoGame-Detection.git
  cd GoGame-Detection
  git checkout convert-videofile 2>/dev/null || true
  cd ..
fi

cd GoGame-Detection

# 2) Ставим зависимости без sente (чтобы ultralytics и остальное установилось)
echo "Установка зависимостей без sente..."
grep -v '^sente' requirements.txt > requirements_no_sente.txt || true
pip install -r requirements_no_sente.txt

# 3) Ставим sente отдельно (на Python 3.12 может не собраться — тогда см. README)
echo "Установка sente..."
pip install "sente>=0.4.2,<0.5" || {
  echo "Ошибка установки sente. Попробуйте Runtime -> Change runtime type -> Python 3.11 и перезапустите."
  exit 1
}

# 4) Запуск
echo "----запуск----"
python main.py "$VIDEO_PATH"
