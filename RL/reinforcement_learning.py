import numpy as np
import random
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

class CaroEnv:
    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((self.size, self.size))
        self.done = False

    def reset(self):
        self.board = np.zeros((self.size, self.size))
        self.done = False
        return self.board

    def step(self, action, player):
        x, y = action
        if self.board[x, y] != 0:
            return self.board, -10, True  # Invalid move, penalty
        
        self.board[x, y] = player
        if self.check_win(x, y, player):
            return self.board, 10, True  # Win, reward
        if np.all(self.board != 0):
            return self.board, 0, True  # Draw
        
        return self.board, 0, False  # Continue playing

    def check_win(self, x, y, player):
        directions = [
            [(0, 1), (0, -1)],   # Vertical
            [(1, 0), (-1, 0)],   # Horizontal
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            count = 1
            for dx, dy in dir_pair:
                nx, ny = x, y
                for _ in range(4):
                    nx, ny = nx + dx, ny + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx, ny] == player:
                        count += 1
                    else:
                        break
            if count >= 5:
                return True
        return False

    def render(self):
        print(self.board)

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # Discount factor
        self.epsilon = 1.0   # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randint(0, self.action_size - 1)
        state = np.reshape(state, [1, self.state_size])
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.reshape(next_state, [1, self.state_size]))[0])
            target_f = self.model.predict(np.reshape(state, [1, self.state_size]))
            target_f[0][action] = target
            self.model.fit(np.reshape(state, [1, self.state_size]), target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
