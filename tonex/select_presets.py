#!/usr/bin/env python3
"""
Tonex Preset Selector
Parses filter criteria from an input file and generates SQL queries to select matching presets.

Input file format:
    [ColumnName]
    value1
    value2
    {CONTAINS} partial_value {/CONTAINS}

    AND/OR [AnotherColumn]
    value3
"""

import re
import sqlite3
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ColumnFilter:
    """Represents a filter for a single column"""
    column_name: str
    values: List[str]
    partial_matches: List[str]
    operator: str  # 'AND' or 'OR' (applies to next filter)


class PresetSelector:
    def __init__(self, db_path: str = None):
        """
        Initialize the preset selector

        Args:
            db_path: Path to SQLite database (optional, for actual queries)
        """
        self.db_path = db_path
        self.filters: List[ColumnFilter] = []

    def parse_filter_file(self, file_path: str) -> None:
        """
        Parse the filter criteria file

        Args:
            file_path: Path to the filter file
        """
        self.filters = []

        with open(file_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]

        current_column = None
        current_values = []
        current_partial = []
        next_operator = 'AND'  # Default operator

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check for column definition with optional leading operator
            column_match = re.match(r'^(AND|OR)?\s*\[([^\]]+)\]', line, re.IGNORECASE)
            if column_match:
                # Save previous filter if exists
                if current_column:
                    self.filters.append(ColumnFilter(
                        column_name=current_column,
                        values=current_values,
                        partial_matches=current_partial,
                        operator=next_operator
                    ))

                # Start new filter
                operator = column_match.group(1)
                if operator:
                    next_operator = operator.upper()
                else:
                    next_operator = 'AND'  # Default for first column or when not specified

                current_column = column_match.group(2)
                current_values = []
                current_partial = []
                i += 1
                continue

            # Check for CONTAINS markup
            contains_match = re.match(r'\{CONTAINS\}\s*(.+?)\s*\{/CONTAINS\}', line, re.IGNORECASE)
            if contains_match:
                if current_column:
                    current_partial.append(contains_match.group(1))
                i += 1
                continue

            # Check for standalone AND/OR (applies to next column)
            if line.upper() in ['AND', 'OR']:
                next_operator = line.upper()
                i += 1
                continue

            # Regular value
            if current_column and line:
                # Add the value as-is (including * if present)
                current_values.append(line)

            i += 1

        # Add the last filter
        if current_column:
            self.filters.append(ColumnFilter(
                column_name=current_column,
                values=current_values,
                partial_matches=current_partial,
                operator=next_operator
            ))

    def build_sql_query(self, table_name: str = 'Presets') -> Tuple[str, List]:
        """
        Build SQL query from parsed filters

        Args:
            table_name: Name of the table to query

        Returns:
            Tuple of (sql_query, parameters)
        """
        if not self.filters:
            return f"SELECT * FROM {table_name}", []

        where_clauses = []
        parameters = []

        for i, filter_obj in enumerate(self.filters):
            column_conditions = []

            # Add exact match conditions
            for value in filter_obj.values:
                column_conditions.append(f"[{filter_obj.column_name}] = ?")
                parameters.append(value)

            # Add partial match conditions (LIKE)
            for partial in filter_obj.partial_matches:
                column_conditions.append(f"[{filter_obj.column_name}] LIKE ?")
                parameters.append(f"%{partial}%")

            # Combine conditions for this column with OR
            if column_conditions:
                column_clause = "(" + " OR ".join(column_conditions) + ")"
                where_clauses.append(column_clause)

        # Combine all column clauses with their operators
        if len(where_clauses) == 1:
            where_clause = where_clauses[0]
        else:
            # Build the WHERE clause respecting operators
            combined = where_clauses[0]
            for i in range(1, len(where_clauses)):
                operator = self.filters[i].operator
                combined = f"{combined} {operator} {where_clauses[i]}"
            where_clause = combined

        sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
        return sql, parameters

    def execute_query(self) -> List[Dict]:
        """
        Execute the query against the database

        Returns:
            List of matching records as dictionaries
        """
        if not self.db_path:
            raise ValueError("Database path not set")

        sql, params = self.build_sql_query()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            conn.close()

    def print_query(self) -> None:
        """Print the generated SQL query (for debugging)"""
        sql, params = self.build_sql_query()
        print("Generated SQL Query:")
        print("-" * 60)
        print(sql)
        print("\nParameters:")
        for i, param in enumerate(params, 1):
            print(f"  {i}. {param}")
        print("-" * 60)


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Select Tonex Presets based on filter criteria'
    )
    parser.add_argument(
        'filter_file',
        help='Path to filter criteria file (e.g., select_these_tags.lst)'
    )
    parser.add_argument(
        '--database', '-d',
        help='Path to SQLite database file (optional, for actual execution)'
    )
    parser.add_argument(
        '--show-query', '-q',
        action='store_true',
        help='Show the generated SQL query'
    )
    parser.add_argument(
        '--execute', '-e',
        action='store_true',
        help='Execute the query (requires --database)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of results'
    )

    args = parser.parse_args()

    # Create selector and parse file
    selector = PresetSelector(args.database)
    selector.parse_filter_file(args.filter_file)

    print(f"Parsed {len(selector.filters)} filter(s):")
    for i, f in enumerate(selector.filters, 1):
        print(f"\n{i}. Column: [{f.column_name}]")
        if f.values:
            print(f"   Exact matches: {f.values}")
        if f.partial_matches:
            print(f"   Partial matches: {f.partial_matches}")
        if i < len(selector.filters):
            print(f"   Operator to next filter: {f.operator}")
    print()

    # Show query if requested
    if args.show_query or not args.execute:
        selector.print_query()

    # Execute query if requested
    if args.execute:
        if not args.database:
            print("\nError: --database required for execution")
            return

        try:
            results = selector.execute_query()
            print(f"\nFound {len(results)} matching preset(s)")

            # Display results
            if results:
                display_limit = args.limit if args.limit else len(results)
                for i, record in enumerate(results[:display_limit], 1):
                    print(f"\n{i}. {record.get('Tag_PresetName', 'N/A')}")
                    if 'Tag_Artist' in record:
                        print(f"   Artist: {record['Tag_Artist']}")
                    if 'Tag_Album' in record:
                        print(f"   Album: {record['Tag_Album']}")
                    if 'Tag_Song' in record:
                        print(f"   Song: {record['Tag_Song']}")

                if args.limit and len(results) > args.limit:
                    print(f"\n... and {len(results) - args.limit} more")

        except Exception as e:
            print(f"\nError executing query: {e}")


if __name__ == '__main__':
    main()
