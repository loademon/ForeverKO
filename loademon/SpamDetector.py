import discord
import time
import Levenshtein


class SpamDetector:
    def __init__(self, max_messages, time_window, max_similarity):
        self.max_messages = max_messages
        self.time_window = time_window
        self.max_similarity = max_similarity
        self.user_messages = {}

    def is_spam(self, user_id, message: discord.Message):
        messages = self.user_messages.get(user_id, [])

        current_time = time.time()
        messages = [msg for msg in messages if current_time - msg[0] < self.time_window]

        if any(self.similar(message, msg[1]) for msg in messages):
            return True, True

        if len(messages) >= self.max_messages:
            return True, False

        messages.append((current_time, message))
        self.user_messages[user_id] = messages
        return False, False

    def similar(self, msg1, msg2):
        distance = Levenshtein.distance(msg1, msg2)

        longest_length = max(len(msg1), len(msg2))
        similarity = (longest_length - distance) / longest_length

        return similarity > self.max_similarity


