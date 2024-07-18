MODEL_KEY= ""
OUTPUT_DIR= ""
DATAFILE_PATHS= ""
accelerate launch --main_process_port=20001 -m magicoder.train \
  --model_key  $MODEL_KEY \
  --model_name_or_path $MODEL_KEY \
  --use_flash_attention True \
  --max_training_seq_length 2048 \
  --datafile_paths $DATAFILE_PATHS \
  --output_dir  $OUTPUT_DIR \
  --bf16 True \
  --num_train_epochs 3 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 64 \
  --group_by_length False \
  --ddp_find_unused_parameters False \
  --logging_steps 1 \
  --save_steps 1000 \
  --log_level info \
  --optim adafactor \
  --max_grad_norm -1 \
  --warmup_steps 15 \
  --learning_rate 5e-5 \
  --lr_scheduler_type linear