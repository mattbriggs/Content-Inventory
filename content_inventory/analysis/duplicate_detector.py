from datasketch import MinHash, MinHashLSH
from itertools import combinations
import hashlib

class DuplicateDetector:
    """Detects near-duplicate documents using MinHash and LSH for fast text reuse detection."""

    def __init__(self, logger, threshold=0.8):
        self.logger = logger
        self.threshold = threshold

    def _get_fingerprint(self, text):
        m = MinHash(num_perm=128)
        for token in set(text.lower().split()):
            m.update(token.encode('utf8'))
        return m

    def find_duplicates(self, corpus):
        self.logger.info("Detecting near-duplicate content using MinHash...")
        lsh = MinHashLSH(threshold=self.threshold, num_perm=128)
        fingerprints = {}

        # Build fingerprints
        for doc in corpus:
            m = self._get_fingerprint(doc["text"])
            fingerprints[doc["filename"]] = m
            lsh.insert(doc["filename"], m)

        # Compare documents through LSH
        duplicates = []
        for fname, m in fingerprints.items():
            matches = lsh.query(m)
            for match in matches:
                if match != fname:
                    duplicates.append({
                        "doc1": fname,
                        "doc2": match,
                        "similarity": round(m.jaccard(fingerprints[match]), 3)
                    })

        self.logger.success(f"Detected {len(duplicates)} duplicate pairs.")
        return duplicates