import random
from typing import Dict
import time
from collections import deque, defaultdict
from typing import Deque

class SlidingWindowRateLimiter:

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = int(window_size)
        self.max_requests = int(max_requests)
        self.history: Dict[str, Deque[float]] = defaultdict(deque)

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.history:
            return

        window_start = current_time - self.window_size
        user_deque = self.history[user_id]

        while user_deque and user_deque[0] <= window_start:
            user_deque.popleft()

        if not user_deque:
            del self.history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        now = time.time()
        self._cleanup_window(user_id, now)
        if user_id not in self.history:
            return True
        return len(self.history[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.history:
            self.history[user_id] = deque()

        if len(self.history[user_id]) < self.max_requests:
            self.history[user_id].append(now)
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.history:
            return 0.0

        q = self.history[user_id]
        if len(q) < self.max_requests:
            return 0.0

        idx = len(q) - self.max_requests
        pivot_ts = q[idx]
        wait = self.window_size - (now - pivot_ts)
        return max(0.0, wait)


def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
