import os
import click

from utils.constants import Constants, ExpConstants
from global_constants import coco_paths, flickr_paths
from ..dataset import DetFeatDatasetConstants as CocoDatasetConstants
from ..dataset_flickr import FlickrDatasetConstants
from ..models.object_encoder import ObjectEncoderConstants
from ..models.cap_encoder import CapEncoderConstants
from ..train import main as train


@click.command()
@click.option(
    '--exp_name',
    default='default_exp',
    help='Experiment name')
@click.option(
    '--dataset',
    default='coco',
    type=click.Choice(['coco','flickr']),
    help='Dataset to use')
@click.option(
    '--model_num',
    default=-1,
    type=int,
    help='Model number. -1 implies begining of training.')
@click.option(
    '--lr',
    default=1e-5,
    type=float,
    help='Learning rate')
@click.option(
    '--train_batch_size',
    default=50,
    type=int,
    help='Training batch size')
@click.option(
    '--neg_noun_loss_wt',
    default=1.0,
    type=float,
    help='Weight for negative verb loss')
@click.option(
    '--self_sup_loss_wt',
    default=0.0,
    type=float,
    help='Weight for self supervision loss')
@click.option(
    '--lang_sup_loss_wt',
    default=1.0,
    type=float,
    help='Weight for language supervision loss')
@click.option(
    '--no_context',
    is_flag=True,
    help='Apply flag to switch off contextualization')
@click.option(
    '--random_lang',
    is_flag=True,
    help='Apply flag to randomly initialize and train BERT')
@click.option(
    '--cap_info_nce_layers',
    default=2,
    type=int,
    help='Number of layers in lang_sup_criterion')
@click.option(
    '--val_frequently',
    is_flag=True,
    help='set for val_step=model_save_step else val_step=2*model_save_step')
def main(**kwargs):
    exp_base_dir = coco_paths['exp_dir']
    if kwargs['dataset']=='flickr':
        exp_base_dir = flickr_paths['exp_dir']
    exp_const = ExpConstants(kwargs['exp_name'],exp_base_dir)
    exp_const.log_dir = os.path.join(exp_const.exp_dir,'logs')
    exp_const.model_dir = os.path.join(exp_const.exp_dir,'models')
    exp_const.vis_dir = os.path.join(exp_const.exp_dir,'vis')
    exp_const.dataset = kwargs['dataset']
    exp_const.optimizer = 'Adam'
    exp_const.lr = kwargs['lr']
    exp_const.momentum = None
    exp_const.num_epochs = 10
    exp_const.log_step = 20
    # Save models approx. twice every epoch
    exp_const.model_save_step = 400000//(2*kwargs['train_batch_size']) # 4000=400000/(2*50)
    if exp_const.dataset=='flickr':
        exp_const.model_save_step = 150000//(2*kwargs['train_batch_size'])
    val_freq_factor=2
    if kwargs['val_frequently'] is True:
        val_freq_factor=1
    exp_const.val_step = val_freq_factor*exp_const.model_save_step # set to 1*model_save_step for plotting mi vs perf
    exp_const.num_val_samples = None
    exp_const.train_batch_size = kwargs['train_batch_size']
    exp_const.val_batch_size = 20
    exp_const.num_workers = 10
    exp_const.seed = 0
    exp_const.neg_noun_loss_wt = kwargs['neg_noun_loss_wt']
    exp_const.self_sup_loss_wt = kwargs['self_sup_loss_wt']
    exp_const.lang_sup_loss_wt = kwargs['lang_sup_loss_wt']
    exp_const.contextualize = not kwargs['no_context']
    exp_const.random_lang = kwargs['random_lang']
    
    DatasetConstants = CocoDatasetConstants
    if exp_const.dataset=='flickr':
        DatasetConstants = FlickrDatasetConstants
    
    data_const = {
        'train': DatasetConstants('train'),
        'val': DatasetConstants('val'),
    }

    model_const = Constants()
    model_const.model_num = kwargs['model_num']
    model_const.object_encoder = ObjectEncoderConstants()
    model_const.object_encoder.context_layer.output_attentions = True
    model_const.object_encoder.object_feature_dim = 2048
    model_const.cap_encoder = CapEncoderConstants()
    model_const.cap_encoder.output_attentions = True
    model_const.cap_info_nce_layers = kwargs['cap_info_nce_layers']
    model_const.object_encoder_path = os.path.join(
        exp_const.model_dir,
        f'object_encoder_{model_const.model_num}')
    model_const.self_sup_criterion_path = os.path.join(
        exp_const.model_dir,
        f'self_sup_criterion_{model_const.model_num}')
    model_const.lang_sup_criterion_path = os.path.join(
        exp_const.model_dir,
        f'lang_sup_criterion_{model_const.model_num}')

    train(exp_const,data_const,model_const)


if __name__=='__main__':
    main()