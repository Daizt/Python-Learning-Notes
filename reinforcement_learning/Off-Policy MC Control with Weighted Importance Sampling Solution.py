import gym
import matplotlib
import numpy as np
import sys

from collections import defaultdict
if "../" not in sys.path:
  sys.path.append("../") 
from lib.envs.blackjack import BlackjackEnv
from lib import plotting

matplotlib.style.use('ggplot')

env = BlackjackEnv()

def create_random_policy(nA):
	"""
	Creates a random policy function.
	
	Args:
		nA: Number of actions in the environment.
	
	Returns:
		A function that takes an observation as input and returns a vector
		of action probabilities
	"""
	A = np.ones(nA, dtype=float)/nA
	def policy_fn(observation):
		return A
	return policy_fn
	
def create_greedy_policy(Q):
	"""
	Creates a greedy policy based on Q values.
	
	Args:
		Q: A dictionary that maps from state -> action values
		
	Returns:
		A function that takes an observation as input and returns a vector
		of action probabilities.
	"""
	
	def policy_fn(state):
		A = np.zeros_like(Q[state], dtype=float)
		best_action = np.argmax(Q[state])
		A[best_action] = 1.0
		return A
	return policy_fn
	
def mc_control_importance_sampling(env, num_episodes, behavior_policy, discount_factor=1.0):
	"""
	Monte Carlo Control Off-Policy Control using Weighted Importance Sampling.
	Finds an optimal greedy policy.
	
	Args:
		env: OpenAI gym environment.
		num_episodes: Number of episodes to sample.
		behavior_policy: The behavior to follow while generating episodes.
			A function that given an observation returns a vector of probabilities for each action.
		discount_factor: Gamma discount factor.
	
	Returns:
		A tuple (Q, policy).
		Q is a dictionary mapping state -> action values.
		policy is a function that takes an observation as an argument and returns
		action probabilities. This is the optimal greedy policy.
	"""
	
	# The final action-value function.
	# A dictionary that maps state -> action values
	Q = defaultdict(lambda: np.zeros(env.action_space.n))
	
	# Our greedily policy we want to learn
	target_policy = create_greedy_policy(Q)
	
	# Another initialization C that maps (s,a) pair to cumulative factor
	C = defaultdict(float)
	
	# for each episode
	for i_episode in range(1, num_episodes+1):
		if i_episode%1000 == 0:
			print("\rEpisode {}/{}.".format(i_episode, num_episodes),end="")
			sys.stdout.flush()
			
		# Generate an episode
		episode = []
		state = env.reset()
		for t in range(100):
			action = np.random.choice(range(env.action_space.n), p=behavior_policy(state))
			next_state, reward, done, _ = env.step(action)
			episode.append((state, action, reward))
			if done:
				break
			state = next_state
			
		# for every (s,a) pair visited, perform weigted importance sampling
		G, W = 0.0, 1.0
		for s_a_pair in episode[::-1]:
			state, action, reward = s_a_pair
			G = discount_factor*G + reward
			C[(state, action)] += W
			Q[state][action] += W/C[(state, action)]*(G - Q[state][action])
			if np.argmax(target_policy(state)) != action:
				break
			W *= 1/behavior_policy(state)[action]
			
	return Q, target_policy
	
random_policy = create_random_policy(env.action_space.n)
Q, policy = mc_control_importance_sampling(env, num_episodes=500000, behavior_policy=random_policy)

with open('result2.txt', 'w') as fp:
	for k,v in Q.items():
		a,b,c = k
		d,e = v
		line = list(map(str, [a,b,c,d,e]))
		seperator = ','
		fp.write(seperator.join(line))
		fp.write('\n')

# For plotting: Create value function from action-value function
# by picking the best action at each state
V = defaultdict(float)
for state, action_values in Q.items():
	action_value = np.max(action_values)
	V[state] = action_value
plotting.plot_value_function(V, title="Optimal Value Function")

