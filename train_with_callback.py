from stable_baselines3 import PPO, DDPG, TD3
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
from stable_baselines3.common.noise import NormalActionNoise
from opencat_gym_env import OpenCatGymEnv
from callback_save_best_model import SaveBestModelCallback
import numpy as np

RL_ALGORITHM = "DDPG"  # ["PPO", "DDPG", "TD3"]

if __name__ == "__main__":
    # Set up number of parallel environments
    parallel_env = 8
    env = make_vec_env(OpenCatGymEnv, n_envs=parallel_env, vec_env_cls=SubprocVecEnv)

    # Define PPO agent with custom network architecture
    custom_arch = dict(net_arch=[256, 256])

    # Path to save the best model
    save_path = "trained"

    # Create the callback to save the best model
    save_best_callback = SaveBestModelCallback(check_freq=100, save_path=save_path)

    n_actions = env.action_space.shape[0]
    action_noise = NormalActionNoise(
        mean=np.zeros(n_actions), sigma=10.0 * np.ones(n_actions)
    )

    # Initialize the model
    if RL_ALGORITHM == "PPO":
        model = PPO(
            "MlpPolicy",
            env,
            policy_kwargs=custom_arch,
            n_steps=int(2048 * 8 / parallel_env),
            verbose=1,
            tensorboard_log=f"{save_path}/tensorboard_logs",  # Log training data
        )

    elif RL_ALGORITHM == "DDPG":
        model = DDPG(
            "MlpPolicy",
            env,
            action_noise=action_noise,
            policy_kwargs=custom_arch,
            verbose=1,
            tensorboard_log=f"{save_path}/tensorboard_logs",  # Log training data
        )

    elif RL_ALGORITHM == "TD3":
        model = TD3(
            "MlpPolicy",
            env,
            action_noise=action_noise,
            policy_kwargs=custom_arch,
            verbose=1,
            tensorboard_log=f"{save_path}/tensorboard_logs",  # Log training data
        )

    else:
        print("Invalid RL_ALGORITHM, choose from [PPO, DDPG, TD3]")
        exit(0)

    # Train the model, using the callback to record rewards and save the best model
    model.learn(total_timesteps=2e6, callback=save_best_callback)

    # Save the final trained model
    model.save(f"{save_path}/final_model")
