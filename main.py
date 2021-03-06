import gym
from gym import spaces
import numpy as np
import pandas as pd
from tqdm import tqdm
from ppo_torch import Agent
from matplotlib import pyplot as plt

if __name__ == "__main__":

    # Environment settings
    env = gym.make("LunarLander-v2")
    
    # Trainer's settings
    load_checkpoint = True
    chkpt_dir = 'tmp/trained_model'
    render = True
    n_trials = 1
    n_episodes = 10

    # PPO params
    N = 20
    batch_size = 5
    n_epochs = 10
    alpha = 0.0003 
    gamma = 0.99
    best_score = env.reward_range[0]
    layer_1_dim = 256
    layer_2_dim = 256

    # Final results
    score_book = {}
    actor_loss_book = {}
    critic_loss_book = {}
    total_loss_book = {}

    for trial in range(n_trials):
        print('\nTrial:', trial+1)
        agent = Agent(n_actions=env.action_space.n, batch_size=batch_size, alpha=alpha,
                        n_epochs=n_epochs, input_dims=env.observation_space.shape, gamma=gamma,
                        fc1_dims=layer_1_dim, fc2_dims=layer_2_dim, chkpt_dir=chkpt_dir)
        
        # Initialize storage pointers
        score_history = []
        avg_score_history = []
        loss = []
        actor_loss = []
        critic_loss = []
        total_loss = []

        # Initialize the run
        learn_iters = 0
        avg_score = 0
        n_steps = 0

        if load_checkpoint:
            agent.load_models()

        for i in tqdm(range(n_episodes)):
            observation = env.reset()
            done = False
            score = 0

            while not done:
                if render:
                    env.render(mode='human')
                
                action, prob, val = agent.choose_action(observation)
                observation_, reward, done, info = env.step(action)
                n_steps += 1
                score += reward
                agent.remember(observation, action, prob, val, reward, done)
                
                if not load_checkpoint:
                    if n_steps % N == 0:
                        loss.append(agent.learn())
                        learn_iters += 1

                observation = observation_
            
            if not load_checkpoint:
                avg_loss = np.mean(loss, axis=0)
                actor_loss.append(avg_loss[0])
                critic_loss.append(avg_loss[1])
                total_loss.append(avg_loss[2])

            # score = 100*(score/env.labels.shape[0])
            score_history.append(score)
            avg_score = np.mean(score_history[-100:])
            avg_score_history.append(avg_score)
            
            if avg_score >= best_score:
                best_score = avg_score
                if not load_checkpoint:
                    # print("Saving Model")
                    agent.save_models()
            
            if i%100 == 0:
                agent.save_custom_models(count=i)
        
            # print('episode', i, 'score %.2f' % score, 'avg_score %.2f' % avg_score, 'time_steps', n_steps, 'learning_steps', learn_iters)


        score_book[trial] = score_history
        actor_loss_book[trial] = actor_loss
        critic_loss_book[trial] = critic_loss
        total_loss_book[trial] = total_loss

            
    print("\nStoring rewards data...")
    a = pd.DataFrame(score_book)
    
    if not load_checkpoint:
        a.to_csv('data/PPO-LunarLander-rewards-train.csv')
        print("\nStoring losses...")
        b = pd.DataFrame(actor_loss_book)
        b.to_csv('data/PPO-LunarLander-actor_loss.csv')
        c = pd.DataFrame(critic_loss_book)
        c.to_csv('data/PPO-LunarLander-critic_loss.csv')
        d = pd.DataFrame(total_loss_book)
        d.to_csv('data/PPO-LunarLander-total_loss.csv')
    else:
        a.to_csv('data/PPO-LunarLander-rewards-test.csv')
    print("Experiment finshed")