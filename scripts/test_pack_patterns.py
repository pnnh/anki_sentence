import unittest

from pack_patterns import passes_en, passes_zh


class CausativePatternTests(unittest.TestCase):
    def test_serviced_with_have_and_get(self):
        for sentence in (
            "He had his car serviced over the weekend.",
            "I have my car serviced every year.",
            "She has her car serviced regularly.",
            "We get our car serviced here.",
            "He gets his car serviced every year.",
            "They got their car serviced yesterday.",
            "I'm getting my car serviced tomorrow.",
            "Can I get it serviced here?",
            "We had them serviced yesterday.",
            "He had the old family car serviced.",
            "HE HAD HIS CAR SERVICED.",
        ):
            with self.subTest(sentence=sentence):
                self.assertTrue(passes_en("causative", sentence))

    def test_serviced_without_causative_object_is_rejected(self):
        for sentence in (
            "He serviced his car over the weekend.",
            "He has serviced his car.",
            "He has already serviced his car.",
            "His car has been serviced.",
            "His car got serviced yesterday.",
            "His car is being serviced.",
            "He asked the mechanic to service his car.",
            "He had his car service yesterday.",
            "He had his car servicing yesterday.",
            "He had his car servicedness yesterday.",
        ):
            with self.subTest(sentence=sentence):
                self.assertFalse(passes_en("causative", sentence))

    def test_existing_causative_examples_remain_valid(self):
        for sentence in (
            "I had my hair cut yesterday.",
            "Can you get it fixed?",
            "He called to have water delivered.",
            "He had his car checked over the weekend.",
        ):
            with self.subTest(sentence=sentence):
                self.assertTrue(passes_en("causative", sentence))

    def test_maintenance_source_remains_valid(self):
        self.assertTrue(passes_zh("causative", "周末他把车送去保养了。"))


if __name__ == "__main__":
    unittest.main()
