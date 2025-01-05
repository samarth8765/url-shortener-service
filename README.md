# URL Shortener Service

## Overview

The URL Shortener Service is a lightweight application designed to convert long URLs into shorter, unique URLs. This service also tracks access statistics and supports expiration for short URLs. Additional features include rate-limiting to prevent abuse and scheduled cleanup of expired URLs.

## Key Features

1. Shorten URLs:
   - Submit a long URL to receive a unique short URL. If no expiration is provided, the short URL defaults to a 30-day expiration.
2. Redirection:
   - Accessing the short URL redirects the user to the original long URL.
3. Access Count Tracking:
   - Track the number of times a short URL has been accessed.
4. Caching:
   - Improve performance by caching short URLs and their corresponding long URLs using Redis.
5. Rate-Limiting:
   - Limit the number of requests from a single IP to 100 requests per minute to prevent abuse.
6. Scheduled Cleanup: - Automatically remove expired URLs from both the database and Redis every hour using APScheduler.

## Routes and Endpoints

1.  Shorten a URL

    - Endpoint: `POST http://localhost:8080/shorten`
    - Description: Submit a long URL to create a short URL. If the expires_at field is not provided, the short URL defaults to a 30-day expiration.

      `Request Body`

      ```json
      {
        "original_url": "https://example.com",
        "expires_at": "2025-02-01T00:00:00" // Optional
      }
      ```

      `Response Body`

      ```json
      {
        "original_url": "https://example.com",
        "short_url": "6bec2f3",
        "created_at": "2025-01-05T19:01:53.136072",
        "expires_at": "2025-02-04T19:01:53.136072",
        "expired": false,
        "access_count": 0
      }
      ```

2.  Redirect to Original URL

    - Endpoint: `GET http://localhost:8080/:short_url`
    - Description: Redirect to the original URL associated with the given short URL.

      ### Example

            Request: GET localhost:8080/6bec2f3
            Response: Redirects to https://example.com.

3.  Get Access Count

    - Endpoint: `GET http://localhost:8080/access_count/:short_url`
    - Description: Retrieve the access count, original URL, and expiration time for a given short URL.

      ```json
      {
        "short_url": "6bec2f3",
        "access_count": 28,
        "original_url": "https://github.com/samarth8765/music-library-api/blob/master/docker-compose.yaml",
        "expires_at": "2025-02-04T19:01:53.136072"
      }
      ```

## Approach

### URL Shortening

- A unique short URL is generated using the MD5 hash of the original URL. The first 7 characters of the hash are used as the short URL.
- If the same long URL is submitted again, the existing short URL is reused.

### Caching with Redis

- Redis is used to cache the mapping between short URLs and long URLs to improve read performance.
- Cache entries have a TTL equal to the minimum of:
  - The remaining time until expiration.
  - 24 hours (default cache duration).

### Tracking Access Count

- Every time a short URL is accessed, the access_count field in the database is incremented.

### Expiration Handling

- URLs are marked as expired once their expiration date has passed. Expired URLs are removed from the cache during scheduled cleanup tasks.

### Rate-Limiting

- Middleware is implemented to limit requests from a single IP to 100 requests per minute. Requests exceeding the limit receive a 429 Too Many Requests response.

### Scheduled Cleanup

- Expired URLs are automatically cleaned up every hour using APScheduler. The cleanup task:
  - Identifies expired URLs in the database.
  - Removes expired URLs from both the database and Redis.

## Design Decisions

1.  Database: SQLite
    - SQLite is used for persistent storage of the URL mappings and access statistics. It is a lightweight and simple solution suitable for this application.
2.  Caching: Redis
    - Redis is used as a caching layer to reduce database queries and improve read performance.
      Frequently accessed short URLs are stored in Redis with a TTL (Time-to-Live).
3.  Short URL Generation
    - Short URLs are generated using the MD5 hash of the original URL, and the first 7 characters of the hash are used.
      Reasoning: MD5 is fast and deterministic, making it a good fit for this use case.
4.  Rate-Limiting
    - Rate limiting is implemented using Redis to maintain request counters for each IP address.
      This ensures that excessive usage by a single IP does not overwhelm the service.
5.  Scheduler for Cleanup
    - APScheduler is used to automate cleanup tasks. The scheduler runs in the background and removes expired URLs every hour.

## Challenges Faced

1. Potential MD5 Hash Collisions:

   - MD5 is deterministic, and while the chance of a collision in 7 characters is low, it is not zero.
   - A more robust hashing algorithm like SHA256 or a counter-based approach can reduce the risk further, but MD5 was chosen for simplicity and speed.

2. Scalability:

   - SQLite is sufficient for small-scale applications but may become a bottleneck with higher traffic.
   - A production-level implementation could use PostgreSQL or another relational database for scalability.

3. Concurrent Requests:

- The application uses a simple single-threaded approach. For handling high concurrency, scaling with workers or introducing a message queue might be necessary.

## How to Run the Application

Using Docker Compose

1. Ensure Docker and Docker Compose are installed on your system.
2. Run the application:
   ```bash
   docker compose up --build
   ```
3. The service will be available at http://localhost:8000.
