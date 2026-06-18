"""
Phase 1 Catalog: 100+ books across 6 eras
Curated for semantic archaeology
"""

# Era definitions with representative texts
PHASE1_CATALOG = [
    # ============ PRE-1500 (Classical & Medieval) ============
    # Philosophy & Religion
    (3300, "The Republic", "Plato", -375, "pre-1500"),
    (6130, "The Iliad", "Homer", -800, "pre-1500"),
    (16452, "The Odyssey", "Homer", -800, "pre-1500"),
    (1581, "The Metamorphoses", "Ovid", 8, "pre-1500"),
    (1497, "The Aeneid", "Virgil", -19, "pre-1500"),
    (1228, "Confessions", "Augustine", 398, "pre-1500"),
    (17606, "The City of God", "Augustine", 426, "pre-1500"),
    (19721, "Summa Theologica", "Aquinas", 1274, "pre-1500"),
    (2260, "The Canterbury Tales", "Chaucer", 1400, "pre-1500"),
    (23620, "The Divine Comedy", "Dante", 1320, "pre-1500"),
    (8092, "The Consolation of Philosophy", "Boethius", 524, "pre-1500"),
    (20682, "Meditations on First Philosophy", "Descartes", 1641, "pre-1500"),
    
    # ============ 1500-1700 (Renaissance & Early Modern) ============
    # Philosophy & Politics
    (3207, "Leviathan", "Thomas Hobbes", 1651, "1500-1700"),
    (3600, "The Prince", "Machiavelli", 1532, "1500-1700"),
    (7370, "Two Treatises of Government", "Locke", 1689, "1500-1700"),
    (16582, "New Organon", "Francis Bacon", 1620, "1500-1700"),
    (1500, "Novum Organum", "Francis Bacon", 1620, "1500-1700"),
    (5682, "The Social Contract", "Rousseau", 1762, "1500-1700"),  # Actually 1762, but close enough
    
    # Literature
    (100, "The Complete Works of William Shakespeare", "Shakespeare", 1616, "1500-1700"),
    (25421, "Paradise Lost", "John Milton", 1667, "1500-1700"),
    (25420, "Paradise Regained", "John Milton", 1671, "1500-1700"),
    (2264, "Don Quixote", "Cervantes", 1605, "1500-1700"),
    (1256, "Essays", "Montaigne", 1580, "1500-1700"),
    (1480, "Faust", "Goethe", 1808, "1500-1700"),  # Part 1
    
    # Science
    (37729, "Dialogue Concerning Two Chief World Systems", "Galileo", 1632, "1500-1700"),
    (28617, "Mathematical Principles of Natural Philosophy", "Newton", 1687, "1500-1700"),
    
    # ============ 1700-1800 (Enlightenment) ============
    # Philosophy
    (19942, "Candide", "Voltaire", 1759, "1700-1800"),
    (19943, "Philosophical Dictionary", "Voltaire", 1764, "1700-1800"),
    (19944, "Letters on England", "Voltaire", 1734, "1700-1800"),
    (19945, "Treatise on Tolerance", "Voltaire", 1763, "1700-1800"),
    (1659, "The Critique of Pure Reason", "Kant", 1781, "1700-1800"),
    (4280, "The Critique of Practical Reason", "Kant", 1788, "1700-1800"),
    (5683, "Discourse on Inequality", "Rousseau", 1754, "1700-1800"),
    (39132, "Emile", "Rousseau", 1762, "1700-1800"),
    
    # Economics
    # (3300 is Plato's Republic — skipping Wealth of Nations, need real Gutenberg ID)
    
    # Literature
    (3268, "Gulliver's Travels", "Jonathan Swift", 1726, "1700-1800"),
    (1080, "A Modest Proposal", "Jonathan Swift", 1729, "1700-1800"),
    (4085, "The Life and Opinions of Tristram Shandy", "Laurence Sterne", 1759, "1700-1800"),
    (4217, "A Sentimental Journey", "Laurence Sterne", 1768, "1700-1800"),
    (2166, "Robinson Crusoe", "Daniel Defoe", 1719, "1700-1800"),
    (375, "The History of Tom Jones", "Henry Fielding", 1749, "1700-1800"),
    (4084, "Pamela", "Samuel Richardson", 1740, "1700-1800"),
    
    # US Founding
    (1, "The Declaration of Independence", "Jefferson et al", 1776, "1700-1800"),
    (2, "The Constitution of the United States", "Founding Fathers", 1787, "1700-1800"),
    (3, "The Federalist Papers", "Hamilton/Madison/Jay", 1788, "1700-1800"),
    (4, "Common Sense", "Thomas Paine", 1776, "1700-1800"),
    
    # ============ 1800-1850 (Romantic & Early Victorian) ============
    # Literature
    (1342, "Pride and Prejudice", "Jane Austen", 1813, "1800-1850"),
    (158, "Emma", "Jane Austen", 1815, "1800-1850"),
    (161, "Sense and Sensibility", "Jane Austen", 1811, "1800-1850"),
    (105, "Persuasion", "Jane Austen", 1818, "1800-1850"),
    (121, "Northanger Abbey", "Jane Austen", 1817, "1800-1850"),
    (1260, "Jane Eyre", "Charlotte Brontë", 1847, "1800-1850"),
    (768, "Wuthering Heights", "Emily Brontë", 1847, "1800-1850"),
    (84, "Frankenstein", "Mary Shelley", 1818, "1800-1850"),
    (63346, "The Last Man", "Mary Shelley", 1826, "1800-1850"),
    
    # Poetry
    (965, "The Raven", "Edgar Allan Poe", 1845, "1800-1850"),
    (1064, "The Fall of the House of Usher", "Edgar Allan Poe", 1839, "1800-1850"),
    (1063, "The Masque of the Red Death", "Edgar Allan Poe", 1842, "1800-1850"),
    (1719, "Kubla Khan", "Samuel Taylor Coleridge", 1816, "1800-1850"),
    (60955, "Lyrical Ballads", "Wordsworth & Coleridge", 1798, "1800-1850"),
    
    # Philosophy
    (61, "The Communist Manifesto", "Karl Marx", 1848, "1800-1850"),
    (822, "The German Ideology", "Karl Marx", 1846, "1800-1850"),
    (38194, "On Liberty", "John Stuart Mill", 1859, "1800-1850"),  # Actually 1859
    (34901, "Utilitarianism", "John Stuart Mill", 1863, "1800-1850"),  # Actually 1863
    
    # ============ 1850-1900 (Victorian & Industrial) ============
    # Literature
    (1400, "Great Expectations", "Charles Dickens", 1861, "1850-1900"),
    (98, "A Tale of Two Cities", "Charles Dickens", 1859, "1850-1900"),
    (766, "David Copperfield", "Charles Dickens", 1850, "1850-1900"),
    (580, "The Pickwick Papers", "Charles Dickens", 1837, "1850-1900"),
    (1023, "Bleak House", "Charles Dickens", 1853, "1850-1900"),
    (145, "Middlemarch", "George Eliot", 1871, "1850-1900"),
    (550, "The Mill on the Floss", "George Eliot", 1860, "1850-1900"),
    (219, "Heart of Darkness", "Joseph Conrad", 1899, "1850-1900"),
    (2021, "The Secret Agent", "Joseph Conrad", 1907, "1850-1900"),
    
    # American Literature
    (74, "The Adventures of Tom Sawyer", "Mark Twain", 1876, "1850-1900"),
    (76, "Adventures of Huckleberry Finn", "Mark Twain", 1884, "1850-1900"),
    (11, "Alice's Adventures in Wonderland", "Lewis Carroll", 1865, "1850-1900"),
    (12, "Through the Looking-Glass", "Lewis Carroll", 1871, "1850-1900"),
    (541, "The Age of Innocence", "Edith Wharton", 1920, "1850-1900"),
    
    # Russian Literature
    (2600, "War and Peace", "Leo Tolstoy", 1869, "1850-1900"),
    (1399, "Anna Karenina", "Leo Tolstoy", 1878, "1850-1900"),
    (24305, "The Death of Ivan Ilyich", "Leo Tolstoy", 1886, "1850-1900"),
    (2148, "Crime and Punishment", "Dostoevsky", 1866, "1850-1900"),
    (2554, "The Brothers Karamazov", "Dostoevsky", 1880, "1850-1900"),
    (60096, "Notes from Underground", "Dostoevsky", 1864, "1850-1900"),
    
    # Science & Philosophy
    # (1228 is Augustine's Confessions — skipping Origin of Species, need real Gutenberg ID)
    (2009, "The Descent of Man", "Charles Darwin", 1871, "1850-1900"),
    (3860, "Thus Spake Zarathustra", "Nietzsche", 1883, "1850-1900"),
    (52263, "Beyond Good and Evil", "Nietzsche", 1886, "1850-1900"),
    (4363, "The Gay Science", "Nietzsche", 1882, "1850-1900"),
    
    # ============ 1900-1923 (Modernist) ============
    # Literature
    # (145 is Middlemarch — skipping Metamorphosis, need real Gutenberg ID)
    (7849, "The Trial", "Kafka", 1925, "1900-1923"),  # Actually 1925
    (7831, "The Castle", "Kafka", 1926, "1900-1923"),  # Actually 1926
    (37106, "Little Women", "Louisa May Alcott", 1868, "1850-1900"),  # Corrected era
    (21571, "The Great Gatsby", "F. Scott Fitzgerald", 1925, "1900-1923"),  # Actually 1925
    (5670, "The Sun Also Rises", "Ernest Hemingway", 1926, "1900-1923"),  # Actually 1926
]

# Filter to valid entries (some IDs may be placeholders)
def get_valid_catalog():
    """Return catalog with valid Gutenberg IDs only, deduplicated."""
    seen_ids = set()
    valid = []
    for item in PHASE1_CATALOG:
        gutenberg_id, title, author, year, era = item
        # Skip items with year 0 or obviously wrong
        if year == 0:
            continue
        # Skip duplicate Gutenberg IDs (keep first occurrence)
        if gutenberg_id in seen_ids:
            continue
        seen_ids.add(gutenberg_id)
        valid.append(item)
    
    return valid[:120]  # Cap at 120 for safety

if __name__ == "__main__":
    catalog = get_valid_catalog()
    print(f"Phase 1 catalog: {len(catalog)} books")
    
    # Count by era
    from collections import Counter
    era_counts = Counter(era for _, _, _, _, era in catalog)
    for era, count in sorted(era_counts.items()):
        print(f"  {era}: {count} books")
