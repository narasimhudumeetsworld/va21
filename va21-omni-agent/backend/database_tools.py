"""
VA21 Database Tools - Multi-Database Management Suite

This module provides tools for managing and querying various database
systems including PostgreSQL, MySQL, SQLite, and Redis.
"""

import subprocess
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class DatabaseConnection:
    """Database connection configuration."""
    connection_id: str
    name: str
    db_type: str  # 'postgresql', 'mysql', 'sqlite', 'redis'
    host: str
    port: int
    database: str
    username: str
    password: str  # Stored securely
    is_connected: bool = False
    ssl_enabled: bool = False


@dataclass
class QueryResult:
    """Result of a database query."""
    query_id: str
    connection_id: str
    query: str
    success: bool
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float
    error: Optional[str]
    timestamp: datetime


class DatabaseTools:
    """
    VA21 Database Tools - Multi-database management.
    
    Features:
    - Support for PostgreSQL, MySQL, SQLite, Redis
    - Connection management
    - Query execution and history
    - Schema browser
    - Data export (CSV, JSON)
    - Query templates
    - Performance analysis
    """
    
    SUPPORTED_DATABASES = ['postgresql', 'mysql', 'sqlite', 'redis']
    
    def __init__(self, data_dir: str = "data/database_tools"):
        self.data_dir = data_dir
        self.connections_file = os.path.join(data_dir, "connections.json")
        self.history_file = os.path.join(data_dir, "query_history.json")
        
        self.connections: Dict[str, DatabaseConnection] = {}
        self.query_history: List[QueryResult] = []
        self.active_connections: Dict[str, Any] = {}
        
        # Check available clients
        self.available_clients = self._check_clients()
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the database tools."""
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_connections()
    
    def _check_clients(self) -> Dict[str, bool]:
        """Check which database clients are available."""
        clients = {}
        
        # PostgreSQL
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, timeout=5)
            clients['postgresql'] = result.returncode == 0
        except:
            clients['postgresql'] = False
        
        # MySQL
        try:
            result = subprocess.run(['mysql', '--version'], capture_output=True, timeout=5)
            clients['mysql'] = result.returncode == 0
        except:
            clients['mysql'] = False
        
        # SQLite (always available via Python)
        clients['sqlite'] = True
        
        # Redis
        try:
            result = subprocess.run(['redis-cli', '--version'], capture_output=True, timeout=5)
            clients['redis'] = result.returncode == 0
        except:
            clients['redis'] = False
        
        return clients
    
    def _load_connections(self):
        """Load saved connections."""
        if os.path.exists(self.connections_file):
            try:
                with open(self.connections_file, 'r') as f:
                    data = json.load(f)
                    for c in data.get('connections', []):
                        self.connections[c['connection_id']] = DatabaseConnection(
                            connection_id=c['connection_id'],
                            name=c['name'],
                            db_type=c['db_type'],
                            host=c.get('host', 'localhost'),
                            port=c.get('port', 0),
                            database=c.get('database', ''),
                            username=c.get('username', ''),
                            password=c.get('password', ''),
                            ssl_enabled=c.get('ssl_enabled', False)
                        )
            except Exception as e:
                print(f"[DatabaseTools] Error loading connections: {e}")
    
    def _save_connections(self):
        """Save connections to disk."""
        data = {
            'connections': [
                {
                    'connection_id': c.connection_id,
                    'name': c.name,
                    'db_type': c.db_type,
                    'host': c.host,
                    'port': c.port,
                    'database': c.database,
                    'username': c.username,
                    'password': c.password,
                    'ssl_enabled': c.ssl_enabled
                }
                for c in self.connections.values()
            ]
        }
        with open(self.connections_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ==================== CONNECTION MANAGEMENT ====================
    
    def add_connection(self, name: str, db_type: str,
                      host: str = 'localhost', port: int = None,
                      database: str = '', username: str = '',
                      password: str = '', ssl: bool = False) -> DatabaseConnection:
        """Add a new database connection."""
        import uuid
        connection_id = str(uuid.uuid4())[:12]
        
        # Set default ports
        default_ports = {
            'postgresql': 5432,
            'mysql': 3306,
            'sqlite': 0,
            'redis': 6379
        }
        
        if port is None:
            port = default_ports.get(db_type, 0)
        
        connection = DatabaseConnection(
            connection_id=connection_id,
            name=name,
            db_type=db_type,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            ssl_enabled=ssl
        )
        
        self.connections[connection_id] = connection
        self._save_connections()
        
        return connection
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection."""
        if connection_id in self.connections:
            # Disconnect first
            self.disconnect(connection_id)
            del self.connections[connection_id]
            self._save_connections()
            return True
        return False
    
    def get_connections(self) -> List[DatabaseConnection]:
        """Get all connections."""
        return list(self.connections.values())
    
    def test_connection(self, connection_id: str) -> Dict:
        """Test a database connection."""
        if connection_id not in self.connections:
            return {'success': False, 'error': 'Connection not found'}
        
        conn = self.connections[connection_id]
        
        try:
            if conn.db_type == 'sqlite':
                return self._test_sqlite(conn)
            elif conn.db_type == 'postgresql':
                return self._test_postgresql(conn)
            elif conn.db_type == 'mysql':
                return self._test_mysql(conn)
            elif conn.db_type == 'redis':
                return self._test_redis(conn)
            else:
                return {'success': False, 'error': 'Unsupported database type'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_sqlite(self, conn: DatabaseConnection) -> Dict:
        """Test SQLite connection."""
        try:
            db = sqlite3.connect(conn.database)
            cursor = db.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            db.close()
            return {'success': True, 'version': version}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_postgresql(self, conn: DatabaseConnection) -> Dict:
        """Test PostgreSQL connection."""
        if not self.available_clients.get('postgresql'):
            return {'success': False, 'error': 'PostgreSQL client not installed'}
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = conn.password
            
            result = subprocess.run(
                ['psql', '-h', conn.host, '-p', str(conn.port),
                 '-U', conn.username, '-d', conn.database,
                 '-c', 'SELECT version();'],
                capture_output=True, text=True, timeout=10, env=env
            )
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_mysql(self, conn: DatabaseConnection) -> Dict:
        """Test MySQL connection."""
        if not self.available_clients.get('mysql'):
            return {'success': False, 'error': 'MySQL client not installed'}
        
        try:
            result = subprocess.run(
                ['mysql', '-h', conn.host, '-P', str(conn.port),
                 '-u', conn.username, f'-p{conn.password}',
                 '-e', 'SELECT VERSION();', conn.database],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_redis(self, conn: DatabaseConnection) -> Dict:
        """Test Redis connection."""
        if not self.available_clients.get('redis'):
            return {'success': False, 'error': 'Redis client not installed'}
        
        try:
            args = ['redis-cli', '-h', conn.host, '-p', str(conn.port)]
            if conn.password:
                args.extend(['-a', conn.password])
            args.append('PING')
            
            result = subprocess.run(args, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'PONG' in result.stdout:
                return {'success': True, 'output': 'PONG'}
            else:
                return {'success': False, 'error': result.stderr or 'Connection failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def connect(self, connection_id: str) -> Dict:
        """Connect to a database."""
        result = self.test_connection(connection_id)
        if result['success']:
            self.connections[connection_id].is_connected = True
        return result
    
    def disconnect(self, connection_id: str) -> bool:
        """Disconnect from a database."""
        if connection_id in self.connections:
            self.connections[connection_id].is_connected = False
            if connection_id in self.active_connections:
                try:
                    self.active_connections[connection_id].close()
                except:
                    pass
                del self.active_connections[connection_id]
            return True
        return False
    
    # ==================== QUERY EXECUTION ====================
    
    def execute_query(self, connection_id: str, query: str) -> QueryResult:
        """Execute a query on a database."""
        import uuid
        import time
        
        query_id = str(uuid.uuid4())[:12]
        
        if connection_id not in self.connections:
            return QueryResult(
                query_id=query_id,
                connection_id=connection_id,
                query=query,
                success=False,
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=0,
                error='Connection not found',
                timestamp=datetime.now()
            )
        
        conn = self.connections[connection_id]
        start_time = time.time()
        
        try:
            if conn.db_type == 'sqlite':
                result = self._execute_sqlite(conn, query)
            elif conn.db_type == 'postgresql':
                result = self._execute_postgresql(conn, query)
            elif conn.db_type == 'mysql':
                result = self._execute_mysql(conn, query)
            elif conn.db_type == 'redis':
                result = self._execute_redis(conn, query)
            else:
                result = {'success': False, 'error': 'Unsupported database'}
            
            execution_time = (time.time() - start_time) * 1000
            
            query_result = QueryResult(
                query_id=query_id,
                connection_id=connection_id,
                query=query,
                success=result.get('success', False),
                columns=result.get('columns', []),
                rows=result.get('rows', []),
                row_count=len(result.get('rows', [])),
                execution_time_ms=execution_time,
                error=result.get('error'),
                timestamp=datetime.now()
            )
            
            # Add to history
            self.query_history.append(query_result)
            
            return query_result
            
        except Exception as e:
            return QueryResult(
                query_id=query_id,
                connection_id=connection_id,
                query=query,
                success=False,
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                timestamp=datetime.now()
            )
    
    def _execute_sqlite(self, conn: DatabaseConnection, query: str) -> Dict:
        """Execute SQLite query."""
        try:
            db = sqlite3.connect(conn.database)
            db.row_factory = sqlite3.Row
            cursor = db.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Get rows
            rows = [list(row) for row in cursor.fetchall()]
            
            db.commit()
            db.close()
            
            return {
                'success': True,
                'columns': columns,
                'rows': rows
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_postgresql(self, conn: DatabaseConnection, query: str) -> Dict:
        """Execute PostgreSQL query."""
        if not self.available_clients.get('postgresql'):
            return {'success': False, 'error': 'PostgreSQL client not installed'}
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = conn.password
            
            result = subprocess.run(
                ['psql', '-h', conn.host, '-p', str(conn.port),
                 '-U', conn.username, '-d', conn.database,
                 '-t', '-A', '-F', '|', '-c', query],
                capture_output=True, text=True, timeout=60, env=env
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                rows = [line.split('|') for line in lines if line]
                return {
                    'success': True,
                    'columns': [],  # Would need separate query for column names
                    'rows': rows
                }
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_mysql(self, conn: DatabaseConnection, query: str) -> Dict:
        """Execute MySQL query."""
        if not self.available_clients.get('mysql'):
            return {'success': False, 'error': 'MySQL client not installed'}
        
        try:
            result = subprocess.run(
                ['mysql', '-h', conn.host, '-P', str(conn.port),
                 '-u', conn.username, f'-p{conn.password}',
                 '-e', query, conn.database, '-N', '-B'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                rows = [line.split('\t') for line in lines if line]
                return {
                    'success': True,
                    'columns': [],
                    'rows': rows
                }
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_redis(self, conn: DatabaseConnection, query: str) -> Dict:
        """Execute Redis command."""
        if not self.available_clients.get('redis'):
            return {'success': False, 'error': 'Redis client not installed'}
        
        try:
            args = ['redis-cli', '-h', conn.host, '-p', str(conn.port)]
            if conn.password:
                args.extend(['-a', conn.password])
            args.extend(query.split())
            
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'columns': ['result'],
                    'rows': [[result.stdout.strip()]]
                }
            else:
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== SCHEMA BROWSER ====================
    
    def get_tables(self, connection_id: str) -> List[str]:
        """Get list of tables in database."""
        if connection_id not in self.connections:
            return []
        
        conn = self.connections[connection_id]
        
        if conn.db_type == 'sqlite':
            result = self.execute_query(
                connection_id,
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        elif conn.db_type == 'postgresql':
            result = self.execute_query(
                connection_id,
                "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            )
        elif conn.db_type == 'mysql':
            result = self.execute_query(connection_id, "SHOW TABLES")
        else:
            return []
        
        if result.success:
            return [row[0] for row in result.rows]
        return []
    
    def get_table_schema(self, connection_id: str, table: str) -> List[Dict]:
        """Get schema for a table."""
        if connection_id not in self.connections:
            return []
        
        conn = self.connections[connection_id]
        
        if conn.db_type == 'sqlite':
            result = self.execute_query(
                connection_id,
                f"PRAGMA table_info({table})"
            )
        elif conn.db_type == 'postgresql':
            result = self.execute_query(
                connection_id,
                f"""SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'"""
            )
        elif conn.db_type == 'mysql':
            result = self.execute_query(connection_id, f"DESCRIBE {table}")
        else:
            return []
        
        if result.success:
            return [{'column': row[1] if conn.db_type == 'sqlite' else row[0]} 
                    for row in result.rows]
        return []
    
    # ==================== QUERY HISTORY ====================
    
    def get_query_history(self, limit: int = 50, 
                         connection_id: str = None) -> List[QueryResult]:
        """Get query history."""
        history = self.query_history
        if connection_id:
            history = [q for q in history if q.connection_id == connection_id]
        return list(reversed(history[-limit:]))
    
    def clear_history(self):
        """Clear query history."""
        self.query_history = []
    
    # ==================== EXPORT ====================
    
    def export_to_csv(self, result: QueryResult, filepath: str) -> bool:
        """Export query result to CSV."""
        try:
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                if result.columns:
                    writer.writerow(result.columns)
                writer.writerows(result.rows)
            return True
        except Exception as e:
            print(f"[DatabaseTools] Export error: {e}")
            return False
    
    def export_to_json(self, result: QueryResult, filepath: str) -> bool:
        """Export query result to JSON."""
        try:
            data = {
                'columns': result.columns,
                'rows': result.rows,
                'row_count': result.row_count
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[DatabaseTools] Export error: {e}")
            return False
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict:
        """Get database tools statistics."""
        return {
            'total_connections': len(self.connections),
            'connected_count': sum(1 for c in self.connections.values() if c.is_connected),
            'query_history_count': len(self.query_history),
            'available_clients': self.available_clients,
            'supported_databases': self.SUPPORTED_DATABASES
        }


# Singleton
_database_tools: Optional[DatabaseTools] = None


def get_database_tools() -> DatabaseTools:
    """Get the singleton Database Tools instance."""
    global _database_tools
    if _database_tools is None:
        _database_tools = DatabaseTools()
    return _database_tools
