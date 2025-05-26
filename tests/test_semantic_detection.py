import unittest

from rag_search.semantic import semantic_detection


class TestClassifier(unittest.TestCase):
    def test_semantic_queries(self):
        classifier = semantic_detection.Classifier()
        semantic_queries = [
            "Quel est le prix de la meuleuse ?",
            "Comment utiliser une perceuse à colonne ?",
            "Pourquoi ma scie sauteuse ne démarre plus ?",
            "Où puis-je trouver une visseuse sans fil ?",
            "Peut-on découper un plan de travail avec cette scie ?"
        ]
        for query in semantic_queries:
            with self.subTest(query=query):
                self.assertEqual(classifier.classify_query(query), "semantic")

    def test_keyword_queries(self):
        classifier = semantic_detection.Classifier()
        keyword_queries = [
            "meuleuse angle",
            "poignée aluminium noire",
            "visseuse sans fil 18V",
            "tableau électrique Legrand",
            "serrure encastrable porte bois"
        ]
        for query in keyword_queries:
            with self.subTest(query=query):
                self.assertEqual(classifier.classify_query(query), "keyword")


if __name__ == '__main__':
    unittest.main()
