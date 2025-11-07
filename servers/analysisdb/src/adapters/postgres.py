"""
PostgreSQL adapter for AnalysisDB
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger('analysisdb.postgres')


class PostgresAdapter:
    """PostgreSQL database adapter."""
    
    def __init__(self, connection_url: str, min_conn: int = 1, max_conn: int = 5):
        self.connection_url = connection_url
        self.pool = None
        self.min_conn = min_conn
        self.max_conn = max_conn
    
    async def connect(self):
        """Initialize connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                self.min_conn,
                self.max_conn,
                self.connection_url
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    async def disconnect(self):
        """Close all connections."""
        if self.pool:
            self.pool.closeall()
            logger.info("PostgreSQL connections closed")
    
    def _get_connection(self):
        """Get a connection from the pool."""
        return self.pool.getconn()
    
    def _put_connection(self, conn):
        """Return a connection to the pool."""
        self.pool.putconn(conn)
    
    async def get_publisher_profile(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get publisher profile for domain."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT domain, voice, lix_range, policy, examples
                    FROM publisher_profiles
                    WHERE domain = %s
                    """,
                    (domain,)
                )
                result = cur.fetchone()
                
                if result:
                    # Convert JSON fields
                    result['voice'] = result['voice'] if isinstance(result['voice'], dict) else json.loads(result['voice'])
                    result['policy'] = result['policy'] if isinstance(result['policy'], dict) else json.loads(result['policy'])
                    result['examples'] = result['examples'] if isinstance(result['examples'], list) else json.loads(result['examples'])
                
                return dict(result) if result else None
        finally:
            self._put_connection(conn)
    
    async def get_anchor_portfolio(self, target_domain: str) -> Optional[Dict[str, Any]]:
        """Get anchor portfolio for target domain."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT target_domain, exact, partial, brand, generic, risk
                    FROM anchor_portfolio
                    WHERE target_domain = %s
                    """,
                    (target_domain,)
                )
                result = cur.fetchone()
                
                if result:
                    result = dict(result)
                    result['total'] = result['exact'] + result['partial'] + result['brand'] + result['generic']
                    result['risk'] = float(result['risk']) if result['risk'] else 0.0
                    
                    # Determine risk level
                    if result['risk'] <= 0.3:
                        result['risk_level'] = "low"
                    elif result['risk'] <= 0.6:
                        result['risk_level'] = "medium"
                    else:
                        result['risk_level'] = "high"
                
                return result
        finally:
            self._put_connection(conn)
    
    async def get_pages(
        self, 
        customer_id: Optional[str] = None, 
        page_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get pages with optional filters."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build query dynamically
                query = "SELECT id, url, type, customer_id, metadata FROM pages WHERE 1=1"
                params = []
                
                if customer_id:
                    query += " AND customer_id = %s"
                    params.append(customer_id)
                
                if page_type:
                    query += " AND type = %s"
                    params.append(page_type)
                
                query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = cur.fetchall()
                
                pages = []
                for row in results:
                    page = dict(row)
                    page['id'] = str(page['id'])
                    if page.get('customer_id'):
                        page['customer_id'] = str(page['customer_id'])
                    page['metadata'] = page['metadata'] if isinstance(page['metadata'], dict) else json.loads(page['metadata'] or '{}')
                    pages.append(page)
                
                return pages
        finally:
            self._put_connection(conn)
    
    async def log_event(
        self, 
        event_type: str, 
        order_ref: Optional[str] = None,
        payload: Dict[str, Any] = None
    ) -> UUID:
        """Log an audit event."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                event_id = uuid4()
                cur.execute(
                    """
                    INSERT INTO audit_log (id, order_ref, step, status, payload, ts)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        event_id,
                        UUID(order_ref) if order_ref else None,
                        event_type,
                        'logged',
                        json.dumps(payload or {}),
                        datetime.now(timezone.utc)
                    )
                )
                conn.commit()
                return event_id
        finally:
            self._put_connection(conn)
    
    async def save_anchor_portfolio(
        self,
        target_domain: str,
        exact: int,
        partial: int,
        brand: int,
        generic: int,
        risk: float
    ):
        """Save or update anchor portfolio."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO anchor_portfolio (target_domain, exact, partial, brand, generic, risk, last_calculated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (target_domain) 
                    DO UPDATE SET
                        exact = EXCLUDED.exact,
                        partial = EXCLUDED.partial,
                        brand = EXCLUDED.brand,
                        generic = EXCLUDED.generic,
                        risk = EXCLUDED.risk,
                        last_calculated = EXCLUDED.last_calculated
                    """,
                    (
                        target_domain,
                        exact,
                        partial,
                        brand,
                        generic,
                        risk,
                        datetime.now(timezone.utc)
                    )
                )
                conn.commit()
        finally:
            self._put_connection(conn)
