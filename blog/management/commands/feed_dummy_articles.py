from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Article, Comment
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Feeds polished, realistic technical articles and discussions into the Living Journal.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing editorial authors..."))

        # Create or fetch authors
        authors_data = [
            {"username": "abdullah", "email": "abdullah@postify.journal", "first_name": "Abdullah", "last_name": "Niaz"},
            {"username": "elena_vasquez", "email": "elena@postify.journal", "first_name": "Elena", "last_name": "Vasquez"},
            {"username": "marcus_chen", "email": "marcus@postify.journal", "first_name": "Marcus", "last_name": "Chen"},
            {"username": "sophia_alvarez", "email": "sophia@postify.journal", "first_name": "Sophia", "last_name": "Alvarez"},
            {"username": "david_kim", "email": "david@postify.journal", "first_name": "David", "last_name": "Kim"},
        ]

        users = {}
        for author in authors_data:
            user, created = User.objects.get_or_create(username=author["username"])
            if created:
                user.set_password("PostifyEditorial2024!")
                user.email = author["email"]
                user.first_name = author["first_name"]
                user.last_name = author["last_name"]
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  + Created author @{user.username}"))
            else:
                users[user.username] = user
            users[author["username"]] = user

        # Dummy Tech Articles Data
        articles_data = [
            {
                "title": "The Philosophy of Concurrent State: Designing Resilient Distributed Systems",
                "desc": "An architectural examination of event-driven concurrency, idempotency guarantees, and handling network partitions in modern distributed backends.",
                "category": ["python", "web develpment"],
                "author": "abdullah",
                "days_ago": 1,
                "content": """## Introduction

When software architectures scale beyond single-node boundaries, the illusions of linear time, uniform memory access, and instantaneous consistency evaporate. In modern distributed systems, state is not an immutable monument; it is a fluid consensus negotiated across asynchronous networks.

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

To engineer systems that thrive amidst inevitable network partitions, engineers must transition from defensive locking mechanisms toward **event-driven choreography** and **idempotent reconciliation loops**.

---

## The Fallacy of Distributed Transactions

Traditional ACID transactions rely on two-phase locking protocols (`2PC`). While mathematically sound in localized topologies, `2PC` incurs catastrophic latency overheads when coordinated across geographical zones.

```python
import asyncio
from typing import Protocol, Any

class MessageBroker(Protocol):
    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        ...

class IdempotentEventHandler:
    def __init__(self, broker: MessageBroker, deduplication_cache: set[str]):
        self.broker = broker
        self._seen_events = deduplication_cache

    async def handle_event(self, event_id: str, payload: dict[str, Any]) -> bool:
        if event_id in self._seen_events:
            # Drop redundant duplicate event cleanly
            return False
            
        self._seen_events.add(event_id)
        await self._process_domain_mutation(payload)
        return True

    async def _process_domain_mutation(self, payload: dict[str, Any]) -> None:
        await asyncio.sleep(0.05)  # Atomic transactional work
```

### Core Architectural Guarantees

1. **At-Least-Once Delivery**: Systems must anticipate identical messages arriving out of chronological order.
2. **Deterministic Hash Ingestion**: Ingest keys ensure that repeated payloads produce identical state trees.
3. **Outbox Pattern**: Guarantee that database persistence and event publishing succeed or fail atomically.

---

## Synthesis

Distributed concurrency requires accepting ambiguity. By trading synchronous blocking calls for asynchronous stream processing and robust idempotency, backend services achieve resilient elasticity capable of weathering arbitrary node degradation."""
            },
            {
                "title": "Modern JavaScript Runtime Semantics: Microtasks, Macrotasks, and the Event Loop",
                "desc": "Demystifying the V8 execution pipeline, call stack semantics, and how asynchronous scheduling primitives impact browser rendering latency.",
                "category": ["javascript", "web develpment"],
                "author": "elena_vasquez",
                "days_ago": 2,
                "content": """## The Choreography of Single-Threaded Concurrency

JavaScript is famously described as a single-threaded runtime with an asynchronous execution loop. However, the exact boundary between the synchronous call stack, the **Microtask Queue** (Promises, `queueMicrotask`), and the **Macrotask Queue** (`setTimeout`, `setImmediate`, I/O) remains a frequent source of latency anomalies in frontend applications.

```javascript
// High-priority microtask queue orchestration
console.log('1: Synchronous Call Stack');

setTimeout(() => {
  console.log('4: Macrotask Queue (Timer Fired)');
}, 0);

queueMicrotask(() => {
  console.log('2: Microtask Scheduled Directly');
});

Promise.resolve().then(() => {
  console.log('3: Promise Microtask Resolved');
});
```

### Execution Priority Hierarchy

* **Call Stack:** Immediate frame execution until empty.
* **Microtask Ingestion:** Empties all queued microtasks entirely before yielding control.
* **Animation Frames (`requestAnimationFrame`):** Executed right before style recalculations and layout compositing.
* **Macrotask Ingestion:** Exactly one task dequeued per cycle, followed by microtask re-evaluation.

> "A single unbounded microtask cascade will starve the rendering thread, locking up browser responsiveness even if CPU usage appears distributed."

---

## Engineering Recommendations

1. Never schedule recursive microtasks without explicit cooperational yield points using `await new Promise(requestAnimationFrame)`.
2. Use `scheduler.yield()` in modern Chromium runtimes to split long-running parsing tasks without relinquishing execution priority to unrelated background tabs.
3. Measure frame budget margins in Chrome DevTools Performance panel under 60fps / 120fps display constraints."""
            },
            {
                "title": "React Server Components & Streaming SSR: The Convergence of Client & Server",
                "desc": "How streaming architecture, React Server Components (RSC), and selective hydration fundamentally redefine the boundaries of frontend engineering.",
                "category": ["react", "javascript"],
                "author": "marcus_chen",
                "days_ago": 3,
                "content": """## The Architectural Shift Beyond Client-Side Bundling

For over a decade, single-page application (SPA) architectures pushed increasing amounts of computational burden into client browser bundles. As dependencies grew, initial parse times, memory pressure, and Time-to-Interactive (TTI) degraded on mobile hardware.

**React Server Components (RSC)** represent a paradigm correction. They allow components to execute exclusively on the server, generating a serialized virtual DOM payload that streams progressively into the client without delivering a single byte of server-side component JavaScript.

```tsx
// Server Component: zero client bundle impact
import { db } from '@/infrastructure/database';
import { Suspense } from 'react';
import { ArticleReadingCard } from './ArticleReadingCard';
import { SkeletonPlaceholder } from './SkeletonPlaceholder';

export async function DispatchFeed() {
  const stories = await db.article.findMany({
    orderBy: { publishedAt: 'desc' },
    take: 10,
  });

  return (
    <section className="feed-container">
      <Suspense fallback={<SkeletonPlaceholder count={3} />}>
        {stories.map((story) => (
          <ArticleReadingCard key={story.id} story={story} />
        ))}
      </Suspense>
    </section>
  );
}
```

### Primary Advantages

* **Zero-Bundle Dependencies:** Heavy libraries like markdown parsers or date formatting suites remain entirely on the server.
* **Direct Database Co-location:** Eliminates client-server network waterfall cascades.
* **Preserved Client State:** Client-side form focus, inputs, and animations persist uninterrupted as new server payload chunks stream in."""
            },
            {
                "title": "Designing Type-Safe Domain Models with Modern Python 3.12+",
                "desc": "Leveraging Python's advanced type system, structural subtyping with Protocols, and generic type aliases to build maintainable domain boundaries.",
                "category": ["python"],
                "author": "sophia_alvarez",
                "days_ago": 5,
                "content": """## The Evolution of Pythonic Typing

Python's typing ecosystem has matured from simple runtime annotations into an expressive compile-time formal verification system. With Python 3.12, the introduction of PEP 695 (Type Parameter Syntax) and ergonomic generic aliases brings Python's type safety close to languages like TypeScript and Rust while preserving its dynamic elegance.

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')

class Repository(Protocol[T]):
    # Structural protocol defining persistent storage contracts
    def get_by_id(self, entity_id: str) -> T | None: ...
    def save(self, entity: T) -> None: ...

@dataclass(frozen=True, slots=True)
class ArticleMetadata:
    identifier: str
    author_handle: str
    word_count: int
    inscribed_at: datetime

    def estimate_reading_duration(self) -> int:
        return max(1, self.word_count // 200)
```

### Key Practices for Production Domain Models

1. **Immutability by Default:** Use `frozen=True` and `slots=True` on dataclasses to enforce value semantics and eliminate memory overhead.
2. **Structural Subtyping over Deep Inheritance:** Prefer `typing.Protocol` over abstract base classes (`ABC`). Protocols eliminate brittle inheritance hierarchies while ensuring strict interface compliance.
3. **Pattern Matching with Narrowing:** Combine Python 3.10+ `match/case` with algebraic data types for exhaustive state handling."""
            },
            {
                "title": "The Resilient Web: CSS Subgrid, Modern Container Queries & Fluid Typography",
                "desc": "Transitioning away from viewport-centric media queries towards intrinsically responsive, component-driven editorial layouts with CSS Subgrid.",
                "category": ["web develpment"],
                "author": "david_kim",
                "days_ago": 6,
                "content": """## Beyond the Viewport Boundary

For years, responsive design forced developers to write layout rules based strictly on the user's viewport width. This model broke when building modular, reusable components: a card placed in a 300px sidebar required different CSS classes than the same card placed in an 800px main column.

With the universal baseline support of **CSS Container Queries** (`@container`) and **CSS Subgrid**, the web platform finally empowers intrinsic component responsiveness.

```css
/* Container Context Registration */
.editorial-column {
  container-type: inline-size;
  container-name: dispatch-card;
}

/* Fluid Typographic Scaler */
.dispatch-title {
  font-size: clamp(1.4rem, 2.5cqi + 0.5rem, 2.8rem);
  line-height: 1.15;
  font-family: var(--font-serif);
}

/* Intrinsic Layout Adaptation */
@container dispatch-card (min-width: 540px) {
  .card-inner-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    grid-template-rows: subgrid;
    gap: 24px;
  }
}
```

> "Subgrid allows nested grid children to participate in the sizing of the parent grid tracks, unlocking pixel-perfect vertical alignment across asymmetric editorial rows."

### Best Practices

* **Container Query Units (`cqi`, `cqb`):** Size typography and paddings proportional to the component's container rather than the viewport.
* **Progressive Enhancement:** Always provide a solid flexbox or standard grid fallback for older enterprise environments."""
            },
            {
                "title": "Zero-Allocation Networking in Systems Software: Inquiries in High-Throughput IO",
                "desc": "Investigating ring buffers, kernel bypass techniques, and memory management strategies for sub-millisecond network applications.",
                "category": ["other"],
                "author": "abdullah",
                "days_ago": 8,
                "content": """## The Cost of Memory Allocation on the Critical Path

At ten thousand requests per second, standard heap allocations (`malloc`/`free`) trigger cache line invalidations and garbage collection pauses that destroy tail latency (p99.9). In high-throughput network architectures, memory management must be zero-allocation during steady-state request processing.

### Key Strategies

* **Circular Ring Buffers:** Pre-allocated, cache-aligned contiguous byte buffers that avoid dynamic heap resizing during packet ingestion.
* **Kernel Bypass with `io_uring`:** Submitting batches of read and write requests directly through shared memory submission and completion rings, eliminating syscall context switches.
* **Zero-Copy Serialization:** Parsing byte headers in-place via pointer offsets rather than deserializing payloads into intermediate heap objects."""
            },
            {
                "title": "Mastering React Concurrency: Transitions, Suspense, and Optimistic UI",
                "desc": "A comprehensive handbook on coordinating non-blocking state updates with useTransition and implementing fluid, optimistic mutations.",
                "category": ["react", "web develpment"],
                "author": "elena_vasquez",
                "days_ago": 10,
                "content": """## Non-Blocking Renders in Interactive Applications

Before React 18, state updates were synchronous and non-interruptible. A large table re-sort or complex graph re-computation would freeze the main thread, causing keystrokes, scroll events, and button clicks to drop frames.

React's Concurrent Mode fundamentally decouples urgent user inputs from non-urgent background transitions.

```tsx
import { useState, useTransition, useOptimistic } from 'react';

export function BookmarkToggle({ articleId, initialSaved }: { articleId: string; initialSaved: boolean }) {
  const [isSaved, setIsSaved] = useState(initialSaved);
  const [isPending, startTransition] = useTransition();

  // Optimistic UI state renders instantly while network request proceeds
  const [optimisticSaved, setOptimisticSaved] = useOptimistic(
    isSaved,
    (state, newState: boolean) => newState
  );

  const handleToggle = async () => {
    startTransition(async () => {
      setOptimisticSaved(!optimisticSaved);
      const res = await fetch(`/save/${articleId}`, { method: 'POST' });
      const data = await res.json();
      setIsSaved(data.saved);
    });
  };

  return (
    <button onClick={handleToggle} className={optimisticSaved ? 'saved' : ''} aria-busy={isPending}>
      {optimisticSaved ? 'Saved to Journal' : 'Bookmark'}
    </button>
  );
}
```

### Essential Principles

1. Treat typing, hovering, and pressing as **urgent updates**.
2. Wrap filtering, sorting, page changes, and tab transitions in `startTransition`.
3. Provide immediate visual feedback via optimistic primitives, handling network failures with graceful rollbacks."""
            }
        ]

        # Populate articles and comments
        created_count = 0
        for item in articles_data:
            author = users.get(item["author"], users["abdullah"])
            article_date = timezone.now() - timedelta(days=item["days_ago"], hours=random.randint(1, 12))

            article, created = Article.objects.get_or_create(
                title=item["title"],
                defaults={
                    "owner": author,
                    "desc": item["desc"],
                    "content": item["content"],
                    "category": item["category"],
                    "created": article_date,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"+ Inscribed dispatch: '{article.title[:45]}...'"))

            # Seed realistic upvotes
            voters = random.sample(list(users.values()), k=random.randint(2, len(users)))
            for voter in voters:
                article.upvote.add(voter)

            # Seed realistic bookmarks
            bookmarkers = random.sample(list(users.values()), k=random.randint(1, 3))
            for b_user in bookmarkers:
                article.bookmarks.add(b_user)

            # Seed discussion comments if none exist
            if article.article.count() == 0:
                discussion_samples = [
                    (
                        users["marcus_chen"],
                        "The breakdown of microtask starvation mirrors an incident we debugged last month with an unbounded Promise cascade. Excellent writeup."
                    ),
                    (
                        users["sophia_alvarez"],
                        "The emphasis on idempotency over two-phase locking is critical. In distributed setups, networks will partition—designing for reconciliation is the only sustainable strategy."
                    ),
                    (
                        users["david_kim"],
                        "The CSS Subgrid examples are pristine. It is refreshing to see intrinsic component sizing replace bloated viewport utility classes."
                    ),
                    (
                        users["elena_vasquez"],
                        "Particularly appreciate the practical code snippet illustrating Protocol structural typing. Clean separation of concerns."
                    )
                ]

                # Pick 2-3 comments per article
                selected_comments = random.sample(discussion_samples, k=random.randint(2, 3))
                for commenter, text in selected_comments:
                    Comment.objects.create(
                        owner=commenter,
                        article=article,
                        content=text,
                        created=article_date + timedelta(hours=random.randint(1, 5))
                    )

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully seeded {created_count} new technical articles with authentic discussions, votes, and bookmarks."))
