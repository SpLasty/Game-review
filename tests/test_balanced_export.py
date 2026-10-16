import unittest
from scripts.export_balanced import capped


class BalancedExportTests(unittest.TestCase):
    def test_caps_each_game_without_forcing_sentiment_balance(self):
        rows = [dict(appid=g, review_id=i, timestamp_created=i, word_count=words,
                     recommended=(g == 1))
                for g in [1, 2] for i, words in [(1, 12), (2, 3), (3, 15), (4, 20)]]
        result = capped(rows, 2, minimum=10)
        self.assertEqual([(r['appid'], r['review_id']) for r in result], [(1, 4), (2, 4), (1, 3), (2, 3)])
        self.assertEqual(sum(r['recommended'] for r in result if r['appid'] == 1), 2)
        self.assertEqual(sum(r['recommended'] for r in result if r['appid'] == 2), 0)
        self.assertEqual(capped(rows[::-1], 2, 10), result)

    def test_shortfalls_do_not_duplicate_or_invent_rows(self):
        rows = [dict(appid=1, review_id=1, timestamp_created=100, word_count=3),
                dict(appid=2, review_id=2, timestamp_created=100, word_count=10)]
        self.assertEqual(len(capped(rows, 100)), 2)
        self.assertEqual(capped(rows, 100, 10), [rows[1]])


if __name__ == '__main__':
    unittest.main()
