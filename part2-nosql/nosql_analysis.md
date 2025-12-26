# NoSQL Database Analysis for FlexiMart (Part 2.1)

## Section A: Limitations of Relational Databases (RDBMS)

Relational databases such as MySQL are well suited for structured and stable data models, but they face limitations when handling highly diverse and evolving product catalogs. In FlexiMart’s case, different product types require different attributes. For example, laptops require specifications such as RAM, processor, and storage, whereas shoes require size, color, and material. In a relational schema, accommodating these variations typically leads to wide tables with many nullable columns or multiple subtype tables, both of which increase complexity and reduce clarity.

Frequent schema changes present another challenge. Each time a new product type or attribute is introduced, the database schema must be altered, which can be disruptive and costly in production environments. Schema migrations also increase the risk of errors and downtime.

Additionally, storing customer reviews in a relational database often requires separate tables and complex joins. Reviews naturally form nested, hierarchical data structures, and representing them relationally leads to increased query complexity and reduced performance for read-heavy workloads.

---

## Section B: Benefits of Using MongoDB

MongoDB addresses these challenges through its flexible, document-oriented data model. Instead of enforcing a rigid schema, MongoDB allows each product to be stored as a JSON-like document with attributes specific to that product type. This flexibility makes it easy to store laptops, shoes, groceries, and future product categories within the same collection without schema redesign.

Embedded documents are another key advantage. Customer reviews, ratings, and seller details can be stored directly inside the product document as nested objects or arrays. This design aligns naturally with how product data is accessed in applications and eliminates the need for expensive joins.

MongoDB also supports horizontal scalability through sharding, allowing data to be distributed across multiple servers. This makes it suitable for handling large and growing product catalogs with high read and write throughput, which is essential for an expanding e-commerce platform like FlexiMart.

---

## Section C: Trade-offs and Limitations of MongoDB

Despite its flexibility, MongoDB has notable trade-offs compared to MySQL. First, it provides weaker transactional guarantees by default. While MongoDB supports multi-document transactions, they are more complex and less performant than transactions in relational databases, making MongoDB less suitable for financial or order-processing workloads.

Second, the lack of enforced schema can lead to inconsistent data if not carefully managed at the application level. Without strict constraints, different documents may store similar attributes in different formats, increasing the risk of data quality issues and complicating analytics.
