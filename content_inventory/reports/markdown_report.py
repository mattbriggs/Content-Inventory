import os
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class MarkdownReport:
    """Generates Markdown summary and visualizations for duplication and semantic relationships."""

    def __init__(self, output_dir, logger):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logger

    def generate_summary(self, corpus, extractor, duplicates):
        """Generates corpus summary, duplication insight, and visualization."""
        self.logger.info("Generating Markdown summary report...")
        total_words = sum(doc['word_count'] for doc in corpus)
        total_files = len(corpus)

        report_lines = [
            "# Content Inventory Summary",
            f"**Total Files:** {total_files}",
            f"**Total Words:** {total_words}",
            f"**Duplicate Pairs:** {len(duplicates)}",
            "",
            "## Top 50 Entities",
        ]

        # Add top entities
        top_entities = extractor.entities.most_common(50)
        for e, c in top_entities:
            report_lines.append(f"- {e}: {c}")

        # Create and embed graphs
        reuse_graph_path = self._generate_reuse_graph(corpus, duplicates)
        entity_graph_path = self._generate_entity_relationship_graph(corpus, extractor)

        report_lines += [
            "\n## Duplication Network\n",
            f"![Duplication Network]({os.path.basename(reuse_graph_path)})",
            "\n## Semantic Map (Entity Relationships)\n",
            f"![Semantic Map]({os.path.basename(entity_graph_path)})"
        ]

        report_path = os.path.join(self.output_dir, "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        self.logger.success(f"Markdown summary created in {self.output_dir}")

    # ----------------------------------------------------------------
    # REUSE NETWORK GRAPH (DOCUMENT-LEVEL DUPLICATION)
    # ----------------------------------------------------------------
    def _generate_reuse_graph(self, corpus, duplicates):
        """Create a reuse network with document names and similarity weights."""
        if not duplicates:
            return None

        G = nx.DiGraph()

        # Add nodes with metadata
        for idx, doc in enumerate(corpus):
            G.add_node(
                doc["filename"],
                label=doc["filename"],
                document_id=str(idx),
                word_count=doc["word_count"]
            )

        # Add edges between duplicate docs
        for d in duplicates:
            src, tgt = d["doc1"], d["doc2"]
            sim = d.get("similarity", 1.0)
            if G.has_edge(src, tgt):
                G[src][tgt]["weight"] = max(G[src][tgt]["weight"], sim)
            else:
                G.add_edge(src, tgt, weight=sim, label=f"{sim:.2f}")

        # Save .graphml
        graphml_path = os.path.join(self.output_dir, "reuse_network.graphml")
        nx.write_graphml(G, graphml_path)

        # Quick PNG visualization
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=0.3, iterations=50)
        weights = [d["weight"] * 3 for _, _, d in G.edges(data=True)]
        nx.draw(
            G, pos,
            node_size=80,
            edge_color=weights,
            width=1.5,
            edge_cmap=plt.cm.Blues,
            with_labels=False
        )
        plt.title("Reuse Network (Duplicate Documents)", fontsize=12)
        plt.tight_layout()
        png_path = os.path.join(self.output_dir, "reuse_network.png")
        plt.savefig(png_path, dpi=150)
        plt.close()
        return png_path

    # ----------------------------------------------------------------
    # ENTITY RELATIONSHIP GRAPH (SEMANTIC MAP WITH DOCUMENT IDS)
    # ----------------------------------------------------------------
    def _generate_entity_relationship_graph(self, corpus, extractor):
        """Create a semantic network of entities showing co-occurrence relationships,
        annotated with the documents in which each entity appears."""
        self.logger.info("Building entity relationship graph (semantic map with document IDs)...")

        entity_graph = nx.Graph()
        entity_docs = defaultdict(set)
        cooccurrence = defaultdict(lambda: defaultdict(int))

        # Step 1: Map entities to documents
        for idx, doc in enumerate(corpus):
            doc_id = str(idx)
            filename = doc["filename"]
            text = doc["text"].lower()

            for entity, _ in extractor.entities.items():
                if entity in text:
                    entity_docs[entity].add(f"{doc_id}:{filename}")

        # Step 2: Build co-occurrence relationships
        for doc_entities in entity_docs.values():
            entities = list(doc_entities)
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    e1, e2 = sorted([entities[i], entities[j]])
                    cooccurrence[e1][e2] += 1

        # Step 3: Create graph nodes and edges
        for entity, docs in entity_docs.items():
            entity_graph.add_node(
                entity,
                label=entity,
                documents="; ".join(sorted(docs)),
                doc_count=len(docs)
            )

        for e1, targets in cooccurrence.items():
            for e2, count in targets.items():
                entity_graph.add_edge(e1, e2, weight=count, label=str(count))

        # Step 4: Save GraphML
        graphml_path = os.path.join(self.output_dir, "entity_relationship.graphml")
        nx.write_graphml(entity_graph, graphml_path)

        # Step 5: Visualize graph
        plt.figure(figsize=(12, 9))
        pos = nx.spring_layout(entity_graph, k=0.4, iterations=40)
        weights = [d["weight"] for _, _, d in entity_graph.edges(data=True)]
        nx.draw(
            entity_graph, pos,
            node_size=40,
            edge_color=weights,
            width=1.2,
            edge_cmap=plt.cm.Greens,
            with_labels=False
        )
        plt.title("Semantic Map (Entity Relationships with Document Provenance)", fontsize=12)
        plt.tight_layout()
        png_path = os.path.join(self.output_dir, "entity_relationship.png")
        plt.savefig(png_path, dpi=150)
        plt.close()
        return png_path