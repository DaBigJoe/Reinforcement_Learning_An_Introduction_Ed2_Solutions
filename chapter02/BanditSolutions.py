from chapter02.BanditTestBed import createBandit
import pickle
import os
import numpy as np
import math


def runAndPlot(axes, repeats, plays, bandit_size, method, config, label, nonStationary=False, show=True):
    if os.path.isfile(label + '_rewards.p'):
        average_rewards = pickle.load(open(label + '_rewards.p', "rb"))
        average_optimals = pickle.load(open(label + '_optimals.p', "rb"))
    else:
        runRewards = []
        runOptimals = []
        for _ in range(repeats):
            bandit = createBandit(bandit_size, nonStationary)
            rewards, optimal_chosen = method(bandit, plays, *config)
            runRewards.append(rewards)
            runOptimals.append(optimal_chosen)
        average_rewards = np.mean(runRewards, axis=0)
        average_optimals = np.mean(runOptimals, axis=0)*100
        pickle.dump(average_rewards, open(label + '_rewards.p', 'wb'))
        pickle.dump(average_optimals, open(label + '_optimals.p', 'wb'))
    if show:
        X = np.arange(0, plays, 1)
        axes[0].plot(X, average_rewards, label=label)
        axes[1].plot(X, average_optimals, label=label)
        axes[2].plot(X, np.cumsum(average_rewards), label=label)
        print("{:^12s}".format(label), "{:1.3f}".format(np.cumsum(average_rewards)[-1]),
              "{:1.3f}".format(average_rewards[-1]), "{:1.3f}".format(average_optimals[-1]))
    return average_rewards, average_optimals

def softmax(l, tau):
    d = 0
    for b in l:
        d += math.exp(b)/tau
    l1 = []
    for a in l:
        l1.append((math.exp(a)/tau)/d)
    return l1


def runEGreedy(bandit, plays, epsilon, initial_estimate, step_constant):
    arm_estimates = [initial_estimate] * bandit.size()
    num_pulls = [0] * bandit.size()
    rewards = []
    optimal_chosen = []
    for _ in range(plays):
        if np.random.uniform(0, 1) < epsilon:
            chosen_arm = np.random.randint(bandit.size())
        else:
            m = max(arm_estimates)
            chosen_arm = np.random.choice([i for i, j in enumerate(arm_estimates) if j == m])
        reward = bandit.pull(chosen_arm)
        num_pulls[chosen_arm] += 1
        if step_constant is None:
            step_size = 1/num_pulls[chosen_arm]
        else:
            step_size = step_constant
        arm_estimates[chosen_arm] += step_size*(reward - arm_estimates[chosen_arm])
        rewards.append(reward)
        optimal_chosen.append(1 if chosen_arm == bandit.getOptimalArmId() else 0)
    return rewards, optimal_chosen

