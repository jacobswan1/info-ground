export HDF5_USE_FILE_LOCKING=FALSE

python -m exp.pretrain_coco_noun_negs.run.eval_flickr_phrase_loc \
    --exp_name 'loss_wts_neg_noun_1_self_sup_1_lang_sup_1_no_context_self_sup_feat' \
    --model_num -100 \
    --no_context \
    --self_sup_feat