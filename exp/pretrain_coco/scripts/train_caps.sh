export HDF5_USE_FILE_LOCKING=FALSE

python -m exp.pretrain_coco.run.train_caps \
    --exp_name 'wo_transformer_noun_factor_lang_sup_train_batch_size_50' \
    --model_num -1 \
    --lr 1e-5 \
    --train_batch_size 50