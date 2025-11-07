# Batch and Atomicity Guide

## Översikt

Denna guide definierar regler för batchkörning av backlink-produktion och säkerställer atomiska operationer för dataintegritet. Målet är effektiv skalning utan kvalitetsförlust eller datakorruption.

## Grundprinciper

### Atomicitet
Varje operation måste vara:
- **Komplett**: Antingen lyckas helt eller misslyckas helt
- **Isolerad**: Påverkar inte andra operationer
- **Konsistent**: Lämnar systemet i giltigt tillstånd
- **Hållbar**: Ändringar persisteras korrekt

### Idempotens
Alla operationer ska vara idempotenta:
```python
# Exempel på idempotent operation
operation(X) == operation(operation(X))
```

## Batch-arkitektur

### Batch-storlekar

```yaml
optimal_batch_sizes:
  preflight_generation: 10
  content_writing: 5
  qc_validation: 20
  delivery: 50
  
max_batch_sizes:
  preflight_generation: 25
  content_writing: 10
  qc_validation: 100
  delivery: 200
```

### Köhantering

```
┌─────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐
│ PENDING │ -> │ PREFLIGHT│ -> │ WRITING│ -> │ DELIVERY │
└─────────┘    └──────────┘    └────────┘    └──────────┘
                     ↓              ↓              ↓
                ┌─────────┐    ┌────────┐    ┌─────────┐
                │ FAILED  │    │   QC   │    │COMPLETED│
                └─────────┘    └────────┘    └─────────┘
```

## Transaktionshantering

### Database-transaktioner

```python
async def process_batch(batch_id: str, orders: List[Order]):
    """Process batch with full atomicity"""
    
    async with db.transaction() as tx:
        try:
            # 1. Lock batch
            await tx.execute(
                "UPDATE batches SET status = 'PROCESSING', locked_at = NOW() "
                "WHERE id = $1 AND status = 'PENDING'",
                batch_id
            )
            
            # 2. Process each order
            results = []
            for order in orders:
                result = await process_order(order)
                results.append(result)
                
                # 3. Save checkpoint
                await tx.execute(
                    "INSERT INTO batch_checkpoints (batch_id, order_id, status) "
                    "VALUES ($1, $2, $3) ON CONFLICT (batch_id, order_id) "
                    "DO UPDATE SET status = $3",
                    batch_id, order.id, result.status
                )
            
            # 4. Update batch status
            if all(r.success for r in results):
                await tx.execute(
                    "UPDATE batches SET status = 'COMPLETED' WHERE id = $1",
                    batch_id
                )
            else:
                # Partial failure handling
                failed_count = sum(1 for r in results if not r.success)
                await tx.execute(
                    "UPDATE batches SET status = 'PARTIAL', "
                    "failed_count = $2 WHERE id = $1",
                    batch_id, failed_count
                )
            
            # Commit transaction
            await tx.commit()
            
        except Exception as e:
            # Automatic rollback
            await tx.rollback()
            raise BatchProcessingError(f"Batch {batch_id} failed: {e}")
```

### Checkpoint-system

```yaml
checkpoints:
  order_received:
    data: [order_id, timestamp, raw_order]
    retention: 30_days
    
  preflight_complete:
    data: [order_id, preflight_matrix, writer_prompt]
    retention: 90_days
    
  content_written:
    data: [order_id, article_text, metadata]
    retention: 180_days
    
  qc_passed:
    data: [order_id, validation_report, final_text]
    retention: permanent
    
  delivered:
    data: [order_id, delivery_receipt, published_url]
    retention: permanent
```

## Felhantering

### Retry-strategier

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(TransientError),
    before_sleep=log_retry
)
async def process_with_retry(order):
    """Process with automatic retry for transient errors"""
    pass
```

### Felklassificering

```yaml
transient_errors:
  - NetworkTimeout
  - DatabaseLocked  
  - RateLimitExceeded
  - TemporaryUnavailable
  action: retry_with_backoff
  
permanent_errors:
  - InvalidInput
  - PolicyViolation
  - CustomerSuspended
  - DuplicateOrder
  action: mark_failed_notify
  
critical_errors:
  - DataCorruption
  - SecurityBreach
  - SystemCompromised
  action: halt_all_notify_emergency
```

## Parallellisering

### Worker-pools

```python
from asyncio import Queue, gather
from typing import List

class BatchProcessor:
    def __init__(self, worker_count: int = 5):
        self.worker_count = worker_count
        self.queue = Queue()
        
    async def process_batch(self, orders: List[Order]):
        # Add all orders to queue
        for order in orders:
            await self.queue.put(order)
        
        # Create workers
        workers = [
            self.worker(f"worker-{i}") 
            for i in range(self.worker_count)
        ]
        
        # Process in parallel
        await gather(*workers)
    
    async def worker(self, worker_id: str):
        while not self.queue.empty():
            order = await self.queue.get()
            try:
                await self.process_order(order)
                logger.info(f"{worker_id} processed {order.id}")
            except Exception as e:
                logger.error(f"{worker_id} failed {order.id}: {e}")
                await self.handle_failure(order, e)
```

### Concurrency-kontroll

```yaml
concurrency_limits:
  global_max: 50
  per_customer_max: 10
  per_domain_max: 5
  
rate_limits:
  preflight:
    requests_per_minute: 100
    burst_size: 20
  
  external_apis:
    serp_api:
      requests_per_minute: 60
      retry_after_header: respect
    
    ahrefs:
      requests_per_day: 5000
      concurrent_max: 5
```

## Monitoring och observability

### Metrics att spåra

```yaml
batch_metrics:
  - batch_size
  - processing_time
  - success_rate
  - retry_count
  - error_rate
  
order_metrics:
  - time_in_queue
  - processing_duration
  - state_transitions
  - failure_reasons
  
system_metrics:
  - cpu_usage
  - memory_usage
  - database_connections
  - api_quota_remaining
```

### Logging-strategi

```python
import structlog

logger = structlog.get_logger()

# Structured logging för spårbarhet
logger.info(
    "batch_processing_started",
    batch_id=batch_id,
    order_count=len(orders),
    worker_count=worker_count,
    timestamp=datetime.utcnow().isoformat()
)

# Correlation IDs för distributed tracing
with logger.contextvars(correlation_id=generate_correlation_id()):
    await process_batch(batch_id, orders)
```

## Säkerhetskopiering och återställning

### Backup-strategi

```yaml
backup_schedule:
  continuous:
    - audit_log (streaming replication)
    - order_states (WAL shipping)
  
  hourly:
    - batch_checkpoints
    - preflight_matrices
  
  daily:
    - full_database
    - article_content
    - delivery_receipts
  
  weekly:
    - system_configuration
    - customer_data
```

### Disaster Recovery

```markdown
## Recovery Time Objective (RTO): 4 timmar
## Recovery Point Objective (RPO): 1 timme

1. **Data Loss Scenario**
   - Restore från senaste backup
   - Replay WAL logs
   - Reprocess failed batches
   
2. **Service Outage**
   - Failover till standby
   - Redirect traffic
   - Resume processing
   
3. **Corruption Detection**
   - Halt processing
   - Identify scope
   - Restore clean state
   - Reprocess affected
```

## Batch-schemaläggning

### Optimal körningstider

```yaml
schedule:
  preflight_generation:
    times: ["08:00", "14:00", "20:00"]
    max_batch: 25
    timeout: 30m
    
  content_writing:
    times: ["09:00", "15:00", "21:00"]
    max_batch: 10
    timeout: 2h
    
  qc_validation:
    times: ["11:00", "17:00", "23:00"]
    max_batch: 50
    timeout: 1h
    
  delivery:
    times: ["12:00", "18:00", "00:00"]
    max_batch: 100
    timeout: 30m
```

### Prioritering

```python
def calculate_priority(order: Order) -> int:
    """Calculate order priority for batch scheduling"""
    
    priority = 100  # Base priority
    
    # Customer tier
    if order.customer.tier == "premium":
        priority += 50
    elif order.customer.tier == "standard":
        priority += 20
    
    # Age penalty
    hours_waiting = (datetime.now() - order.created_at).hours
    priority -= min(hours_waiting * 2, 50)
    
    # Deadline boost
    if order.deadline:
        hours_until_deadline = (order.deadline - datetime.now()).hours
        if hours_until_deadline < 24:
            priority += 100
        elif hours_until_deadline < 72:
            priority += 50
    
    return max(priority, 1)  # Never go below 1
```

## State Management

### Order State Machine

```python
from enum import Enum
from typing import Optional

class OrderState(Enum):
    PENDING = "pending"
    PREFLIGHT = "preflight"
    WRITING = "writing"
    QC = "qc"
    APPROVED = "approved"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OrderStateMachine:
    TRANSITIONS = {
        OrderState.PENDING: [OrderState.PREFLIGHT, OrderState.CANCELLED],
        OrderState.PREFLIGHT: [OrderState.WRITING, OrderState.FAILED],
        OrderState.WRITING: [OrderState.QC, OrderState.FAILED],
        OrderState.QC: [OrderState.APPROVED, OrderState.WRITING, OrderState.FAILED],
        OrderState.APPROVED: [OrderState.DELIVERED, OrderState.FAILED],
        OrderState.DELIVERED: [],  # Terminal state
        OrderState.FAILED: [OrderState.PENDING],  # Can retry
        OrderState.CANCELLED: []  # Terminal state
    }
    
    @classmethod
    def can_transition(cls, from_state: OrderState, to_state: OrderState) -> bool:
        return to_state in cls.TRANSITIONS.get(from_state, [])
```

### Idempotens-nyckel

```python
def generate_idempotency_key(operation: str, **params) -> str:
    """Generate deterministic key for idempotent operations"""
    
    # Sort params for consistency
    sorted_params = sorted(params.items())
    
    # Create canonical string
    canonical = f"{operation}:" + ":".join(
        f"{k}={v}" for k, v in sorted_params
    )
    
    # Return hash
    return hashlib.sha256(canonical.encode()).hexdigest()

# Usage
key = generate_idempotency_key(
    "create_preflight",
    order_id=order.id,
    version="1.0"
)
```

## Best Practices

### DO's
- ✅ Använd transaktioner för all state-ändring
- ✅ Implementera circuit breakers för externa tjänster
- ✅ Logga före och efter varje operation
- ✅ Använd correlation IDs genomgående
- ✅ Testa failure scenarios regelbundet

### DON'Ts
- ❌ Processera utan checkpoints
- ❌ Ignorera partial failures
- ❌ Hårdkoda batch-storlekar
- ❌ Skippa idempotens-kontroller
- ❌ Glömma cleanup av gamla data

## Prestandaoptimering

### Batch vs Stream
```yaml
use_batch_when:
  - volume > 100/hour
  - latency_tolerance > 10min
  - homogeneous_processing
  
use_stream_when:
  - real_time_required
  - heterogeneous_data
  - volume < 10/hour
```

### Caching-strategi
```python
from functools import lru_cache
from aiocache import cached

@cached(ttl=3600)  # 1 hour
async def get_publisher_profile(domain: str):
    """Cache publisher profiles to reduce DB load"""
    return await db.fetch_publisher_profile(domain)

@lru_cache(maxsize=1000)
def calculate_risk_score(portfolio: dict) -> float:
    """Cache risk calculations for identical portfolios"""
    return complex_risk_calculation(portfolio)
```

Denna guide uppdateras kontinuerligt baserat på produktionserfarenheter och skalningsbehov.
