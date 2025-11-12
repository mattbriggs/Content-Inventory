import nltk
from nltk import pos_tag, word_tokenize
from nltk.chunk import RegexpParser
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from collections import Counter
import string

class EntityExtractor:
    """Extracts single- and multi-word noun phrases, normalizes plurals,
    and removes stopwords inside phrases."""

    def __init__(self, logger):
        self.logger = logger
        self.entities = Counter()
        self.lemmatizer = WordNetLemmatizer()

        # Ensure NLTK resources are available
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        nltk.download('stopwords', quiet=True)
        self.stop_words = set(stopwords.words('english'))

    def _lemmatize_phrase(self, phrase_tokens):
        """Lemmatize tokens in a noun phrase and remove stopwords."""
        normalized = []
        for word, pos in phrase_tokens:
            word = word.lower().strip()
            if word in self.stop_words or word in string.punctuation:
                continue

            # POS mapping for lemmatizer
            wn_pos = (
                wordnet.NOUN if pos.startswith('N') else
                wordnet.ADJ if pos.startswith('J') else
                wordnet.VERB if pos.startswith('V') else
                wordnet.ADV if pos.startswith('R') else
                wordnet.NOUN
            )

            lemma = self.lemmatizer.lemmatize(word, wn_pos)
            normalized.append(lemma)

        # Return joined phrase, skipping empty results
        return " ".join(normalized).strip()

    def process_corpus(self, corpus):
        """Extract noun phrases (multi-word, lemmatized, stopword-filtered)."""
        self.logger.info("Extracting normalized noun phrases (multi-word, no stopwords)...")

        grammar = r"NP: {<JJ>*<NN.*>+}"  # simple but effective noun phrase grammar
        chunker = RegexpParser(grammar)

        for doc in corpus:
            text = doc.get("text", "")
            if not text.strip():
                continue

            for sent in nltk.sent_tokenize(text):
                tokens = word_tokenize(sent)
                tagged = pos_tag(tokens)
                tree = chunker.parse(tagged)

                for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
                    phrase = self._lemmatize_phrase(subtree.leaves())
                    if len(phrase) > 1:  # skip single characters or empty results
                        self.entities[phrase] += 1

        self.logger.success(f"Extracted {len(self.entities)} clean, normalized entities.")
        return self.entities