#!/usr/bin/env python3
"""
Zotero Library Query Tool
Read literature metadata and locate PDF files from a local Zotero installation.
"""

import argparse
import json
import os
import sqlite3
import sys


def find_zotero_dir():
    """Auto-detect Zotero data directory."""
    candidates = []
    if sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', '')
        user_profile = os.environ.get('USERPROFILE', '')
        # Known full library locations (checked first)
        candidates = [
            r'E:\2-学习文件\1-——学术研究——\Zotero',
            os.path.join(user_profile, 'Zotero'),
            os.path.join(app_data, 'Zotero', 'Zotero', 'Profiles'),
        ]
        if app_data:
            profiles_dir = os.path.join(app_data, 'Zotero', 'Zotero', 'Profiles')
            if os.path.isdir(profiles_dir):
                for p in os.listdir(profiles_dir):
                    candidates.append(os.path.join(profiles_dir, p, 'zotero'))
    elif sys.platform == 'darwin':
        home = os.path.expanduser('~')
        candidates = [
            os.path.join(home, 'Zotero'),
            os.path.join(home, 'Library', 'Application Support', 'Zotero'),
        ]
    else:
        home = os.path.expanduser('~')
        candidates = [
            os.path.join(home, 'Zotero'),
            os.path.join(home, '.zotero'),
        ]
    for c in candidates:
        if os.path.isfile(os.path.join(c, 'zotero.sqlite')):
            return c
    return None


def get_db_path(zotero_dir=None):
    if zotero_dir:
        return os.path.join(zotero_dir, 'zotero.sqlite')
    found = find_zotero_dir()
    if found:
        return os.path.join(found, 'zotero.sqlite')
    return None


def get_storage_path(zotero_dir=None):
    if zotero_dir:
        return os.path.join(zotero_dir, 'storage')
    found = find_zotero_dir()
    if found:
        return os.path.join(found, 'storage')
    return None


def get_connection(db_path):
    uri = f'file:{db_path}?mode=ro&immutable=1'
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_item_basic(conn, item_id):
    cur = conn.execute("""
        SELECT v.value FROM itemData d
        JOIN itemDataValues v ON d.valueID = v.valueID
        WHERE d.itemID = ? AND d.fieldID = 1
    """, (item_id,))
    row = cur.fetchone()
    title = row['value'] if row else '(no title)'

    cur = conn.execute("""
        SELECT v.value FROM itemData d
        JOIN itemDataValues v ON d.valueID = v.valueID
        WHERE d.itemID = ? AND d.fieldID = 6
    """, (item_id,))
    row = cur.fetchone()
    date = row['value'] if row else ''

    cur = conn.execute("""
        SELECT v.value FROM itemData d
        JOIN itemDataValues v ON d.valueID = v.valueID
        WHERE d.itemID = ? AND d.fieldID = 2
    """, (item_id,))
    row = cur.fetchone()
    abstract = row['value'] if row else ''

    cur = conn.execute("""
        SELECT c.lastName, c.firstName, ic.orderIndex
        FROM itemCreators ic
        JOIN creators c ON ic.creatorID = c.creatorID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
    """, (item_id,))
    authors = []
    for r in cur.fetchall():
        name = r['lastName'] or ''
        if r['firstName']:
            name += ', ' + r['firstName']
        authors.append(name)

    cur = conn.execute("SELECT key, itemTypeID FROM items WHERE itemID = ?", (item_id,))
    row = cur.fetchone()
    item_key = row['key'] if row else ''
    type_id = row['itemTypeID'] if row else None
    item_type = 'unknown'
    if type_id is not None:
        cur = conn.execute("SELECT typeName FROM itemTypes WHERE itemTypeID = ?", (type_id,))
        r = cur.fetchone()
        if r:
            item_type = r['typeName']

    return {
        'itemID': item_id,
        'key': item_key,
        'title': title,
        'date': date,
        'abstract': abstract,
        'authors': authors,
        'item_type': item_type,
    }


def get_pdf_paths(conn, item_id, storage_path):
    cur = conn.execute("""
        SELECT att.path, att_item.key as att_key
        FROM itemAttachments att
        JOIN items att_item ON att.itemID = att_item.itemID
        WHERE att.parentItemID = ? AND att.contentType = 'application/pdf'
    """, (item_id,))
    results = []
    for row in cur.fetchall():
        rel_path = row['path']
        att_key = row['att_key']
        if rel_path and rel_path.startswith('storage:'):
            filename = rel_path[8:]
            full_path = os.path.join(storage_path, att_key, filename)
            results.append({
                'relative_path': rel_path,
                'full_path': full_path,
                'exists': os.path.exists(full_path),
            })
    return results


def get_tags(conn, item_id):
    cur = conn.execute("""
        SELECT t.name FROM tags t
        JOIN itemTags it ON t.tagID = it.tagID
        WHERE it.itemID = ?
    """, (item_id,))
    return [r['name'] for r in cur.fetchall()]


def _load_items(conn, storage_path, item_ids):
    results = []
    for item_id in item_ids:
        info = get_item_basic(conn, item_id)
        info['tags'] = get_tags(conn, item_id)
        info['pdfs'] = get_pdf_paths(conn, item_id, storage_path)
        results.append(info)
    return results


def _print_item_list(results, keyword=None):
    if keyword:
        print(f"Found {len(results)} item(s) matching '{keyword}':\n")
    else:
        print(f"Total: {len(results)} item(s)\n")
    for i, item in enumerate(results, 1):
        authors_str = '; '.join(item['authors'][:3])
        if len(item['authors']) > 3:
            authors_str += ' et al.'
        print(f"[{i}] {item['title']}")
        print(f"    Authors: {authors_str or '(unknown)'}")
        print(f"    Date: {item['date'] or '(unknown)'}")
        print(f"    Type: {item['item_type']}")
        if item['tags']:
            print(f"    Tags: {', '.join(item['tags'])}")
        if item['pdfs']:
            print(f"    PDF: {item['pdfs'][0]['full_path']}")
        print()


def cmd_list(args):
    db_path = get_db_path(args.zotero_dir)
    storage_path = get_storage_path(args.zotero_dir)
    if not db_path:
        print("ERROR: Zotero data directory not found.", file=sys.stderr)
        sys.exit(1)
    conn = get_connection(db_path)
    cur = conn.execute("""
        SELECT DISTINCT i.itemID
        FROM items i
        WHERE i.itemID IN (
            SELECT parentItemID FROM itemAttachments
            WHERE contentType = 'application/pdf' AND parentItemID IS NOT NULL
        )
        ORDER BY i.dateAdded DESC
    """)
    items = [r['itemID'] for r in cur.fetchall()]
    if args.limit:
        items = items[:args.limit]
    results = _load_items(conn, storage_path, items)
    conn.close()
    if args.format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        _print_item_list(results)


def cmd_search(args):
    db_path = get_db_path(args.zotero_dir)
    storage_path = get_storage_path(args.zotero_dir)
    if not db_path:
        print("ERROR: Zotero data directory not found.", file=sys.stderr)
        sys.exit(1)
    conn = get_connection(db_path)
    keyword = f'%{args.keyword}%'
    cur = conn.execute("""
        SELECT DISTINCT i.itemID
        FROM items i
        JOIN itemData d ON i.itemID = d.itemID AND d.fieldID = 1
        JOIN itemDataValues v ON d.valueID = v.valueID
        WHERE v.value LIKE ? COLLATE NOCASE
        AND i.itemID IN (
            SELECT parentItemID FROM itemAttachments
            WHERE contentType = 'application/pdf' AND parentItemID IS NOT NULL
        )
        ORDER BY i.dateAdded DESC
    """, (keyword,))
    items = [r['itemID'] for r in cur.fetchall()]
    if args.limit:
        items = items[:args.limit]
    results = _load_items(conn, storage_path, items)
    conn.close()
    if args.format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        _print_item_list(results, keyword=args.keyword)


def cmd_get_pdf(args):
    db_path = get_db_path(args.zotero_dir)
    storage_path = get_storage_path(args.zotero_dir)
    if not db_path:
        print("ERROR: Zotero data directory not found.", file=sys.stderr)
        sys.exit(1)
    conn = get_connection(db_path)
    query = args.item_ref
    if query.isdigit():
        cur = conn.execute("SELECT itemID FROM items WHERE itemID = ?", (int(query),))
    else:
        cur = conn.execute("SELECT itemID FROM items WHERE key = ?", (query,))
    row = cur.fetchone()
    if not row:
        print(f"ERROR: Item '{query}' not found.", file=sys.stderr)
        sys.exit(1)
    item_id = row['itemID']
    info = get_item_basic(conn, item_id)
    pdfs = get_pdf_paths(conn, item_id, storage_path)
    conn.close()
    if args.format == 'json':
        info['pdfs'] = pdfs
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(f"Title: {info['title']}")
        print(f"Authors: {'; '.join(info['authors']) or '(unknown)'}")
        print(f"Date: {info['date'] or '(unknown)'}")
        print(f"Type: {info['item_type']}")
        print(f"\nPDF files:")
        for p in pdfs:
            status = "exists" if p['exists'] else "MISSING"
            print(f"  {p['full_path']}  [{status}]")


def cmd_tags(args):
    db_path = get_db_path(args.zotero_dir)
    if not db_path:
        print("ERROR: Zotero data directory not found.", file=sys.stderr)
        sys.exit(1)
    conn = get_connection(db_path)
    cur = conn.execute("""
        SELECT t.name, COUNT(it.itemID) as cnt
        FROM tags t
        JOIN itemTags it ON t.tagID = it.tagID
        GROUP BY t.tagID
        ORDER BY cnt DESC, t.name
    """)
    results = [{'name': r['name'], 'count': r['cnt']} for r in cur.fetchall()]
    conn.close()
    if args.format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"Found {len(results)} tags:\n")
        for r in results:
            print(f"  {r['name']} ({r['count']})")


def cmd_collections(args):
    db_path = get_db_path(args.zotero_dir)
    if not db_path:
        print("ERROR: Zotero data directory not found.", file=sys.stderr)
        sys.exit(1)
    conn = get_connection(db_path)
    cur = conn.execute("""
        SELECT collectionID, collectionName, parentCollectionID, key
        FROM collections
        ORDER BY parentCollectionID, collectionName
    """)
    results = [dict(r) for r in cur.fetchall()]
    conn.close()
    if args.format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"Found {len(results)} collections:\n")
        for r in results:
            indent = "  " if r['parentCollectionID'] else ""
            print(f"{indent}- {r['collectionName']} (key: {r['key']})")


def cmd_info(args):
    db_path = get_db_path(args.zotero_dir)
    storage_path = get_storage_path(args.zotero_dir)
    print(f"Zotero directory: {find_zotero_dir()}")
    print(f"Database path:    {db_path}")
    print(f"Storage path:     {storage_path}")
    if db_path and os.path.isfile(db_path):
        conn = get_connection(db_path)
        cur = conn.execute("SELECT COUNT(*) as cnt FROM items WHERE itemTypeID != 3")
        total = cur.fetchone()['cnt']
        cur = conn.execute("""
            SELECT COUNT(DISTINCT parentItemID) as cnt
            FROM itemAttachments
            WHERE contentType = 'application/pdf' AND parentItemID IS NOT NULL
        """)
        with_pdf = cur.fetchone()['cnt']
        print(f"\nTotal items:      {total}")
        print(f"Items with PDF:   {with_pdf}")
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='Zotero Library Query Tool')
    parser.add_argument('--zotero-dir', help='Path to Zotero data directory (auto-detected if omitted)')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    p_list = subparsers.add_parser('list', help='List all items with PDFs')
    p_list.add_argument('--limit', type=int, help='Max number of items')
    p_list.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    p_search = subparsers.add_parser('search', help='Search items by title keyword')
    p_search.add_argument('keyword', help='Search keyword')
    p_search.add_argument('--limit', type=int, help='Max number of results')
    p_search.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    p_get = subparsers.add_parser('get-pdf', help='Get PDF path for an item by ID or key')
    p_get.add_argument('item_ref', help='Item ID (number) or Item Key (string)')
    p_get.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    p_tags = subparsers.add_parser('tags', help='List all tags')
    p_tags.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    p_coll = subparsers.add_parser('collections', help='List all collections')
    p_coll.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    subparsers.add_parser('info', help='Show Zotero paths and library stats')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    commands = {
        'list': cmd_list,
        'search': cmd_search,
        'get-pdf': cmd_get_pdf,
        'tags': cmd_tags,
        'collections': cmd_collections,
        'info': cmd_info,
    }
    commands[args.command](args)


if __name__ == '__main__':
    main()