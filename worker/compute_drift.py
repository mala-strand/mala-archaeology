#!/usr/bin/env python3
"""
Semantic drift computation for Phase 1.
Computes cosine similarity between word vectors across eras.
Writes results to drift_scores table.
Zero tokens — pure Python/numpy.
"""
import sqlite3
import json
import numpy as np
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, DRIFT_TOP_K

# Gutenberg boilerplate words to exclude from drift analysis
# These appear in every text's header/footer and distort semantic drift
GUTENBERG_BOILERPLATE = {
    'project', 'gutenberg', 'electronic', 'distributing', 'exporting',
    'license', 'redistributing', 'copying', 'providing', 'distribution',
    'distribute', 'permission', 'copy', 'complying', 'fee', 'archive',
    'comply', 'copyright', 'holder', 'donations', 'donate', 'fund',
    'funding', 'volunteers', 'volunteer', 'hosting', 'server', 'servers',
    'files', 'foundation', 'effort', 'efforts', 'scanned', 'scanner',
    'scanners', 'ocr', 'digitized', 'digitize', 'digitizing',
    'digitisation', 'digitise', 'digitising', 'transcriber',
    'transcribers', 'proofread', 'proofreading', 'proofreader',
    'proofreaders', 'pg', 'gutenbergtm', 'tm', 'trademark', 'trademarks',
    'ip', 'legal', 'laws', 'law', 'attorney', 'attorneys', 'sue',
    'suing', 'lawsuit', 'lawsuits', 'litigation', 'dmca', 'cease',
    'desist', 'infringement', 'infringe', 'infringing', 'violation',
    'violate', 'violating', 'violations', 'permissions', 'permitted',
    'permits', 'allow', 'allows', 'allowed', 'allowing', 'grant',
    'grants', 'granted', 'granting', 'authorization', 'authorize',
    'authorized', 'authorizing', 'unauthorized', 'unlicensed',
    'unlawful', 'illegal', 'prohibited', 'prohibit', 'prohibits',
    'prohibiting', 'restrict', 'restricts', 'restricted', 'restricting',
    'restriction', 'restrictions', 'limitation', 'limitations',
    'limited', 'limit', 'limits', 'excluding', 'exclude', 'excluded',
    'exclusion', 'warranty', 'warranties', 'disclaimer', 'disclaimers',
    'disclaim', 'disclaimed', 'disclaiming', 'liability', 'liable',
    'indemnify', 'indemnification', 'indemnity', 'damages', 'damage',
    'harm', 'harmful', 'harmless', 'arising', 'arise', 'arises',
    'arose', 'result', 'results', 'resulted', 'resulting',
    'consequential', 'incidental', 'special', 'punitive', 'exemplary',
    'indirect', 'direct', 'fitness', 'merchantability',
    'noninfringement', 'non', 'infringers', 'infringer',
    'literary', 'owns', 'paragraph', 'copies', 'including',
    'associated', 'displaying', 'entity', 'collection', 'redistribution',
    'formats', 'fees', 'access', 'derivative', 'terms', 'readable',
    'widest', 'org', 'protected', 'copied', 'format', 'distributed',
    'ebooks', 'consequently', 'performing', 'paragraphs', 'posted',
    'online', 'web', 'website', 'page', 'pages', 'link', 'links',
    'linked', 'linking', 'browser', 'browsers', 'download',
    'downloaded', 'downloading', 'upload', 'uploaded', 'uploading',
    'software', 'hardware', 'computer', 'computers', 'computing',
    'digital', 'network', 'networks', 'networking', 'internet',
    'website', 'websites', 'www', 'http', 'https', 'html', 'url',
    'email', 'emails', 'mail', 'newsletter', 'newsletters',
    'subscribe', 'subscription', 'subscriptions', 'user', 'users',
    'username', 'password', 'login', 'log', 'logged', 'logging',
    'register', 'registered', 'registration', 'sign', 'signed',
    'signing', 'agree', 'agrees', 'agreed', 'agreeing', 'agreement',
    'agreements', 'accept', 'accepts', 'accepted', 'accepting',
    'acceptance', 'terms', 'conditions', 'policy', 'policies',
    'privacy', 'cookie', 'cookies', 'tracking', 'analytics',
    'advertising', 'advertisement', 'advertisements', 'ads', 'ad',
    'sponsor', 'sponsors', 'sponsored', 'sponsorship', 'partner',
    'partners', 'partnership', 'partnerships', 'affiliate',
    'affiliates', 'affiliated', 'commission', 'commissions',
    'royalty', 'royalties', 'revenue', 'revenues', 'income',
    'profit', 'profits', 'profitable', 'business', 'businesses',
    'commercial', 'commerce', 'merchant', 'merchants', 'merchandise',
    'purchase', 'purchases', 'purchased', 'purchasing', 'buy',
    'buys', 'bought', 'buying', 'sell', 'sells', 'sold', 'selling',
    'sale', 'sales', 'seller', 'sellers', 'buyer', 'buyers',
    'customer', 'customers', 'client', 'clients', 'vendor', 'vendors',
    'supplier', 'suppliers', 'provider', 'providers', 'service',
    'services', 'product', 'products', 'goods', 'item', 'items',
    'order', 'orders', 'ordered', 'ordering', 'payment', 'payments',
    'pay', 'paid', 'paying', 'price', 'prices', 'pricing', 'cost',
    'costs', 'costing', 'fee', 'fees', 'charge', 'charges',
    'charged', 'charging', 'tax', 'taxes', 'taxable', 'invoice',
    'invoices', 'receipt', 'receipts', 'refund', 'refunds',
    'refunded', 'refunding', 'return', 'returns', 'returned',
    'returning', 'exchange', 'exchanges', 'exchanged', 'exchanging',
    'shipping', 'delivery', 'deliveries', 'delivered', 'delivering',
    'track', 'tracks', 'tracked', 'tracking', 'ship', 'ships',
    'shipped', 'shipping', 'carrier', 'carriers', 'warehouse',
    'warehouses', 'inventory', 'stock', 'stocks', 'supply',
    'supplies', 'supplied', 'supplying', 'demand', 'demands',
    'demanded', 'demanding', 'market', 'markets', 'marketing',
    'marketed', 'economy', 'economies', 'economic', 'financial',
    'finance', 'finances', 'financed', 'financing', 'bank', 'banks',
    'banking', 'account', 'accounts', 'accounting', 'audit', 'audits',
    'audited', 'auditing', 'compliance', 'regulatory', 'regulation',
    'regulations', 'regulate', 'regulates', 'regulated', 'regulating',
    'govern', 'governs', 'governed', 'governing', 'government',
    'governments', 'governmental', 'authority', 'authorities',
    'agency', 'agencies', 'official', 'officials', 'bureau',
    'bureaus', 'department', 'departments', 'division', 'divisions',
    'section', 'sections', 'subsection', 'subsections', 'paragraph',
    'paragraphs', 'clause', 'clauses', 'subsection', 'subsections',
    'article', 'articles', 'section', 'sections', 'chapter',
    'chapters', 'appendix', 'appendices', 'index', 'indexes',
    'glossary', 'bibliography', 'bibliographies', 'reference',
    'references', 'referenced', 'referencing', 'citation', 'citations',
    'cited', 'citing', 'footnote', 'footnotes', 'endnote', 'endnotes',
    'note', 'notes', 'noted', 'noting', 'remark', 'remarks',
    'remarked', 'remarking', 'comment', 'comments', 'commented',
    'commenting', 'annotation', 'annotations', 'annotated',
    'annotating', 'translation', 'translations', 'translated',
    'translating', 'translator', 'translators', 'edition', 'editions',
    'editor', 'editors', 'editorial', 'publisher', 'publishers',
    'publishing', 'publication', 'publications', 'published',
    'publish', 'publishes', 'printing', 'printed', 'print', 'prints',
    'reprint', 'reprints', 'reprinted', 'reprinting', 'reproduction',
    'reproductions', 'reproduce', 'reproduces', 'reproduced',
    'reproducing', 'republish', 'republishes', 'republished',
    'republishing', 'reissue', 'reissues', 'reissued', 'reissuing',
    'renew', 'renews', 'renewed', 'renewing', 'renewal', 'renewals',
    'extend', 'extends', 'extended', 'extending', 'extension',
    'extensions', 'expire', 'expires', 'expired', 'expiring',
    'expiration', 'expiry', 'terminate', 'terminates', 'terminated',
    'terminating', 'termination', 'terminations', 'cancel', 'cancels',
    'cancelled', 'cancelling', 'cancellation', 'cancellations',
    'revoke', 'revokes', 'revoked', 'revoking', 'revocation',
    'suspend', 'suspends', 'suspended', 'suspending', 'suspension',
    'suspensions', 'modify', 'modifies', 'modified', 'modifying',
    'modification', 'modifications', 'amend', 'amends', 'amended',
    'amending', 'amendment', 'amendments', 'update', 'updates',
    'updated', 'updating', 'upgrade', 'upgrades', 'upgraded',
    'upgrading', 'version', 'versions', 'release', 'releases',
    'released', 'releasing', 'build', 'builds', 'built', 'building',
    'compile', 'compiles', 'compiled', 'compiling', 'compilation',
    'compilations', 'configure', 'configures', 'configured',
    'configuring', 'configuration', 'configurations', 'install',
    'installs', 'installed', 'installing', 'installation',
    'installations', 'uninstall', 'uninstalls', 'uninstalled',
    'uninstalling', 'setup', 'setups', 'setting', 'settings',
    'default', 'defaults', 'custom', 'customs', 'customize',
    'customizes', 'customized', 'customizing', 'customization',
    'customizations', 'option', 'options', 'optional', 'feature',
    'features', 'function', 'functions', 'functional', 'functionality',
    'functionalities', 'utility', 'utilities', 'tool', 'tools',
    'module', 'modules', 'modular', 'component', 'components',
    'compatible', 'compatibility', 'incompatible', 'incompatibility',
    'integrate', 'integrates', 'integrated', 'integrating',
    'integration', 'integrations', 'interface', 'interfaces',
    'protocol', 'protocols', 'standard', 'standards', 'standardize',
    'standardizes', 'standardized', 'standardizing', 'specification',
    'specifications', 'specify', 'specifies', 'specified', 'specifying',
    'implement', 'implements', 'implemented', 'implementing',
    'implementation', 'implementations', 'deploy', 'deploys',
    'deployed', 'deploying', 'deployment', 'deployments', 'migrate',
    'migrates', 'migrated', 'migrating', 'migration', 'migrations',
    'backup', 'backups', 'backed', 'backing', 'restore', 'restores',
    'restored', 'restoring', 'restoration', 'recover', 'recovers',
    'recovered', 'recovering', 'recovery', 'fail', 'fails', 'failed',
    'failing', 'failure', 'failures', 'error', 'errors', 'erroneous',
    'bug', 'bugs', 'debug', 'debugs', 'debugged', 'debugging',
    'fix', 'fixes', 'fixed', 'fixing', 'patch', 'patches', 'patched',
    'patching', 'workaround', 'workarounds', 'troubleshoot',
    'troubleshooting', 'troubleshoots', 'troubleshot',
    'troubleshooter', 'troubleshooters',
    'electronically', 'ascii', 'credits', 'ebook', 'additional',
    'located',
}

# Chronological era ordering
ERA_ORDER = ["pre-1500", "1500-1700", "1700-1800", "1800-1850", "1850-1900", "1900-1923"]


def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


def compute_drift():
    """Compute semantic drift between consecutive eras."""
    db_path = DB_PATH
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get eras in chronological order
    cursor.execute("SELECT DISTINCT era FROM word_vectors")
    db_eras = set(row[0] for row in cursor.fetchall())
    eras = [e for e in ERA_ORDER if e in db_eras]
    print(f"Eras (chronological): {eras}")

    # Get all words that appear in at least one era (excluding Gutenberg boilerplate)
    cursor.execute("SELECT DISTINCT word FROM word_vectors")
    all_words = [row[0] for row in cursor.fetchall() if row[0] not in GUTENBERG_BOILERPLATE]
    print(f"Total words (excl. boilerplate): {len(all_words)}")

    # Load all vectors into memory (word -> era -> vector)
    cursor.execute("SELECT word, era, vector_json FROM word_vectors")
    vectors = {}
    for word, era, vec_json in cursor.fetchall():
        if word not in vectors:
            vectors[word] = {}
        vectors[word][era] = json.loads(vec_json)

    print(f"Loaded vectors for {len(vectors)} words")

    # Clear existing drift scores
    cursor.execute("DELETE FROM drift_scores")
    conn.commit()

    # Compute drift between consecutive eras
    total_drifts = 0
    for i in range(len(eras) - 1):
        era_from = eras[i]
        era_to = eras[i + 1]
        print(f"\nDrift: {era_from} -> {era_to}")

        batch = []
        for word in all_words:
            if word in vectors and era_from in vectors[word] and era_to in vectors[word]:
                sim = cosine_similarity(vectors[word][era_from], vectors[word][era_to])
                drift = 1.0 - sim  # 0 = no drift, 1 = complete drift
                batch.append((word, era_from, era_to, float(drift), float(sim)))

        # Sort by drift descending and keep top K (or all if None)
        batch.sort(key=lambda x: x[3], reverse=True)
        top_batch = batch[:DRIFT_TOP_K] if DRIFT_TOP_K else batch

        cursor.executemany(
            "INSERT OR IGNORE INTO drift_scores (word, era_from, era_to, drift_score, cosine_sim) VALUES (?, ?, ?, ?, ?)",
            top_batch
        )
        conn.commit()
        total_drifts += len(top_batch)

        print(f"  {len(batch)} words with vectors in both eras")
        if DRIFT_TOP_K:
            print(f"  Top {len(top_batch)} drift scores saved")
        else:
            print(f"  All {len(top_batch)} drift scores saved")
        if top_batch:
            print(f"  Most drifted: {top_batch[0][0]} (drift={top_batch[0][3]:.4f})")
            print(f"  Least drifted: {top_batch[-1][0]} (drift={top_batch[-1][3]:.4f})")

    conn.close()
    print(f"\nTotal drift scores computed: {total_drifts}")
    return total_drifts


if __name__ == "__main__":
    t0 = time.time()
    count = compute_drift()
    t1 = time.time()
    print(f"Drift computation took {t1-t0:.1f}s for {count} scores")
