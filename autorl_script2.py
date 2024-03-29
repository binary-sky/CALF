import numpy as np
import commentjson as json
import logging, os
from functools import lru_cache
from THIRDPARTY.casmopolitan.bo_interface import BayesianOptimizationInterface
from UTIL.file_lock import FileLock

MasterAutoRLKey = 'auto_rl_fuzzy_only_lr_5mf_debug_cache'
os.makedirs(f'AUTORL/{MasterAutoRLKey}', exist_ok=True)
#####################################################################################################################
###################################### 第二部分 ：贝叶斯优化HMAP接口继承父类 ###########################################
#####################################################################################################################

class HmpBayesianOptimizationInterface(BayesianOptimizationInterface):
    # 获取基本的实验配置模板
    def obtain_base_experiment(self):
        return """
{
    "config.py->GlobalConfig": {
        "note": "Run1-Lr-Study",   // 实验存储路径
        "env_name": "dca_multiteam",  // 环境（任务名称）
        "env_path": "MISSION.dca_multiteam", 
        "draw_mode": "Img",
        "num_threads": 32,    // 环境并行数量
        "report_reward_interval": 32,
        "test_interval": 65536,
        "test_epoch": 256,
        "mt_parallel": true,
        "device": "cpu", // 使用哪张显卡
        "fold": "1",        // 使用的进程数量 = 环境并行数量/fold
        "n_parallel_frame": 50000000.0,
        "max_n_episode": 4096.0,
        "seed": 22334, // 随机数种子
        "mt_act_order": "new_method",
        "backup_files": [
            "ALGORITHM/calf_adj_lr",
            "MISSION/dca_multiteam"
        ]
    },
    "MISSION.dca_multiteam.collective_assult_parallel_run.py->ScenarioConfig": {
        "N_TEAM": 2,
        "N_AGENT_EACH_TEAM": [20, 20],
        "introduce_terrain": true,
        "terrain_parameters": [0.15, 0.2],
        "size": "5",
        "random_jam_prob": 0.05,
        "MaxEpisodeStep": 150,     // 时间限制， 胜利条件：尽量摧毁、存活
        "render": false,           // 高效渲染,只有0号线程环境会渲染
        "RewardAsUnity": true,
        "half_death_reward": true,
        "TEAM_NAMES": [
            "ALGORITHM.calf_adj_lr.foundation->ReinforceAlgorithmFoundation",
            "TEMP.TEAM2.ALGORITHM.calf_adj_lr.foundation->ReinforceAlgorithmFoundation",
        ]
    },
    "ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig": {
        "train_traj_needed": 32,
        "n_focus_on": 4,
        "lr": 0.0003,
        "ppo_epoch": 16,
        "lr_descent": false,
        "fuzzy_controller": true,
        "use_policy_resonance": false,
        "gamma": 0.99,
    },
    "TEMP.TEAM2.ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig": {
        "train_traj_needed": 32,
        "n_focus_on": 4,
        "lr": 0.0003,
        "ppo_epoch": 16,
        "lr_descent": false,
        "use_policy_resonance": false,
        "gamma": 0.99,
    },
}
"""


    def get_device_conf(self):
        return {
            ########################################
            "ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig-->device_override":
                [
                    "cuda:0",
                    "cuda:0",
                    "cuda:1",
                    "cuda:1",
                ],
            "ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig-->gpu_party_override":
                [
                    "cuda0_party0", # 各子实验的party可以相同， 但每个实验的子队伍party建议设置为不同值
                    "cuda0_party0",
                    "cuda1_party0", # 各子实验的party可以相同， 但每个实验的子队伍party建议设置为不同值
                    "cuda1_party0",
                ],

            ########################################
            "TEMP.TEAM2.ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig-->device_override":
                [
                    "cuda:1",
                    "cuda:1",
                    "cuda:0",
                    "cuda:0",
                ],
            "TEMP.TEAM2.ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig-->gpu_party_override":
                [
                    "cuda1_party0",
                    "cuda1_party0",
                    "cuda0_party0",
                    "cuda0_party0",
                ],

        }


    def compute_(self, X, normalize=False):
        X = np.array(X)
        batch = X.shape[0]
        y_result_array = np.zeros(shape=(batch, 1))

        for b in range(batch):
            X = X[b]
            # 获取实验配置模板
            # Average among multiple different seeds
            conf_override = {
                "config.py->GlobalConfig-->seed": self.seed_list,
                "config.py->GlobalConfig-->note": self.note_list,
            }
            conf_override.update(self.get_device_conf())

            # AutoRL::learn hyper parameter ---> fuzzy
            p1 = self.convert_categorical(from_x = X[0], to_list=[0, 1, 2, 3, 4], p_index=0)
            p2 = self.convert_categorical(from_x = X[1], to_list=[0, 1, 2, 3, 4], p_index=1)
            p3 = self.convert_categorical(from_x = X[2], to_list=[0, 1, 2, 3, 4], p_index=2)
            p4 = self.convert_categorical(from_x = X[3], to_list=[0, 1, 2, 3, 4], p_index=3)
            p5 = self.convert_categorical(from_x = X[4], to_list=[0, 1, 2, 3, 4], p_index=4)


            conf_override.update({
                "ALGORITHM.calf_adj_lr.foundation.py->AlgorithmConfig-->fuzzy_controller_param": [
                    [p1,p2,p3,p4,p5],
                    [p1,p2,p3,p4,p5],
                    [p1,p2,p3,p4,p5],
                    [p1,p2,p3,p4,p5],
                ]
            })


            self.internal_step_cnt += 1
            try:
                future_list = self.push_experiments_and_execute(conf_override)
                from UTIL.batch_exp import fetch_experiment_conclusion
                conclusion_list = fetch_experiment_conclusion(
                    step = self.internal_step_cnt,
                    future_list = future_list,
                    n_run_mode = self.n_run_mode)
            except:
                print('Experiment result timeout, trying again')
                # 如果失败再尝试一次，还不行就抛出错误
                future_list = self.push_experiments_and_execute(conf_override)
                from UTIL.batch_exp import fetch_experiment_conclusion
                conclusion_list = fetch_experiment_conclusion(
                    step = self.internal_step_cnt,
                    future_list = future_list,
                    n_run_mode = self.n_run_mode)
                

            def get_score(conclusion_list):
                score_list = []
                for c in conclusion_list:
                    conclusion_parsed = {}
                    # parse
                    for name, line, time in zip(c['name_list'],c['line_list'],c['time_list']):
                        conclusion_parsed[name] = line
                    s = conclusion_parsed['acc win ratio of=team-0']
                    score_list.append(s[-1])
                return score_list

            y_array = get_score(conclusion_list)
            y = np.array(y_array).mean()
            self.logger.debug(f'input {X}, [p1,p2,p3,p4,p5] = {[p1,p2,p3,p4,p5]}| output {y_array}, average {y}')
            y_result_array[b] = (y - self.y_offset)
            if self.optimize_direction == 'maximize':
                y_result_array[b] = -y_result_array[b]
            else:
                assert self.optimize_direction == 'minimize'

        return y_result_array



    def __init__(self, MasterAutoRLKey, normalize=False, seed=None):
        super().__init__(MasterAutoRLKey)
        self.problem_type = 'categorical' # 'mixed'
        self.seed = seed if seed is not None else 0
        self.n_run = 4
        self.seed_list = [self.seed + i for i in range(self.n_run)]
        self.note_list = [f'parallel-{i}' for i in range(self.n_run)]
        self.n_run_mode = [
            {   
                # "addr": "172.18.116.149:2266",
                # "addr": "172.18.29.20:20256",
                "addr": "172.18.29.20:20256",
                "usr": "hmp",
                "pwd": "your_hmp_password"
            },
        ]*self.n_run
        self.sum_note = "Bo_AutoRL"
        self.base_conf = json.loads(self.obtain_base_experiment())
        self.internal_step_cnt = 0
        if self.base_conf["config.py->GlobalConfig"]["max_n_episode"] < 1000:
            input('conf_override["config.py->GlobalConfig-->max_n_episode"] < 1000, confirm?')


        self.P_CategoricalDims = np.array([0, 1, 2, 3, 4])
        self.P_NumCategoryList = np.array([5, 5, 5, 5, 5])

        # self.P_ContinuousDims = np.array([2, 3])
        # self.P_ContinuousLowerBound = np.array([-1] * len(self.P_ContinuousDims))
        # self.P_ContinuousUpperBound = np.array([1] * len(self.P_ContinuousDims))

        self.normalize = False
        self.y_offset = 0.5
        self.optimize_direction = 'maximize' # 'minimize'

    def convert_categorical(self, from_x, to_list, p_index):
        assert p_index in self.P_CategoricalDims
        assert len(to_list) == self.P_NumCategoryList[p_index]
        from_x_ = int(from_x)
        assert from_x_-from_x == 0
        return to_list[from_x_]

    def convert_continuous(self, from_x, to_range, p_index):
        assert p_index in self.P_ContinuousDims
        where = np.where(self.P_ContinuousDims==p_index)[0]

        new_range = to_range[1] - to_range[0]
        xx = ((from_x - self.P_ContinuousLowerBound[where]) * new_range / (self.P_ContinuousUpperBound[where] - self.P_ContinuousLowerBound[where])) + to_range[0]

        return float(xx)

    def clean_profile_folder(self):
        import shutil, os
        if os.path.exists('PROFILE'):
            time_mark_only = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            shutil.copytree('PROFILE', f'TEMP/PROFILE-{time_mark_only}')
            shutil.rmtree('PROFILE')


    def push_experiments_and_execute(self, conf_override):
        # copy the experiments
        import shutil, os
        shutil.copyfile(__file__, os.path.join(os.path.dirname(__file__), 'batch_experiment_backup.py'))
        # run experiments remotely
        from UTIL.batch_exp import run_batch_exp, fetch_experiment_conclusion
        print('Execute in server:', self.n_run_mode[0])
        self.clean_profile_folder()
        future = run_batch_exp(self.sum_note, self.n_run, self.n_run_mode, self.base_conf, conf_override, __file__, skip_confirm=True, master_folder='AutoRL')
        return future






















#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
###################################### 第四部分 ：BO参数选择，启动运行 ##############################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

if __name__ == '__main__':

    # from THIRDPARTY.casmopolitan.mixed_test_func import *
    import logging, torch
    import argparse
    import time
    from THIRDPARTY.casmopolitan.test_funcs.random_seed_config import *
    from VISUALIZE.mcom import mcom
    from THIRDPARTY.casmopolitan.bo_interface import BayesianOptimisation

    # Set up the objective function
    parser = argparse.ArgumentParser('Run Experiments')
    parser.add_argument('-p', '--problem', type=str, default='xgboost-mnist')
    parser.add_argument('--max_iters', type=int, default=300, help='Maximum number of BO iterations.')
    parser.add_argument('--lamda', type=float, default=1e-6, help='the noise to inject for some problems')
    parser.add_argument('--batch_size', type=int, default=1, help='batch size for BO.')
    parser.add_argument('--n_trials', type=int, default=20, help='number of trials for the experiment')
    parser.add_argument('--n_init', type=int, default=20, help='number of initialising random points')
    parser.add_argument('--save_path', type=str, default='output/', help='save directory of the log files')
    parser.add_argument('--ard', action='store_true', help='whether to enable automatic relevance determination')
    parser.add_argument('-a', '--acq', type=str, default='ei', help='choice of the acquisition function.')
    parser.add_argument('--random_seed_objective', type=int, default=20, help='The default value of 20 is provided also in COMBO')
    parser.add_argument('-d', '--debug', action='store_true', help='Whether to turn on debugging mode (a lot of output will be generated).')
    parser.add_argument('--no_save', action='store_true', help='If activated, do not save the current run into a log folder.')
    parser.add_argument('--seed', type=int, default=2023, help='**initial** seed setting')
    parser.add_argument('-k', '--kernel_type', type=str, default=None, help='specifies the kernel type')
    parser.add_argument('--infer_noise_var', action='store_true')
    args = parser.parse_args()
    options = vars(args)
    print(options)
    # Set numpy seed
    np.random.seed(args.seed)
    np.set_printoptions(3, suppress=True)
    torch.cuda.manual_seed(args.seed)


    if args.debug: logging.basicConfig(level=logging.INFO)
    # Sanity checks
    assert args.acq in ['ucb', 'ei', 'thompson'], 'Unknown acquisition function choice ' + str(args.acq)
    mcv = mcom(path = 'AUTORL/{MasterAutoRLKey}/', rapid_flush = True, draw_mode = 'Img', image_path = f'AUTORL/{MasterAutoRLKey}/decend.jpg', tag = 'BayesianOptimisation')
    mcv.rec_init(color='g')
    BayesianOptimisation(0, mcv, args, MasterAutoRLKey=MasterAutoRLKey, HmpBayesianOptimizationInterface=HmpBayesianOptimizationInterface)

