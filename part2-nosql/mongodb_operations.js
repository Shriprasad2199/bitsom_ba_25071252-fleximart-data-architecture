/*
  FlexiMart MongoDB Operations (Part 2.2)
  Run with:
    mongosh < part2-nosql/mongodb_operations.js

  Assumptions:
  - products_catalog.json is stored at: part2-nosql/products_catalog.json
  - The JSON file is an ARRAY of documents (so we can insertMany)
*/

// ---------------------------------------------------------
// Use / create database
// ---------------------------------------------------------
use("fleximart_nosql");

// ---------------------------------------------------------
// Operation 1: Load Data (Import JSON into collection 'products')
// ---------------------------------------------------------
// Approach: Read products_catalog.json using Node's fs module and insertMany()
// This works reliably when running the script via mongosh --file.

db.products.drop(); // reset for repeatable runs

const fs = require("fs");
const path = require("path");

// IMPORTANT: run mongosh from the REPO ROOT so this resolves correctly
const jsonPath = path.resolve("part2-nosql", "products_catalog.json");

const jsonText = fs.readFileSync(jsonPath, "utf8");
const products = JSON.parse(jsonText);

if (!Array.isArray(products)) {
  throw new Error("products_catalog.json must be a JSON array of product documents.");
}

const insertResult = db.products.insertMany(products);
print(`Inserted ${Object.keys(insertResult.insertedIds).length} documents into fleximart_nosql.products`);

// ---------------------------------------------------------
// Operation 2: Basic Query
// Find all products in "Electronics" category with price < 50000
// Return only: name, price, stock
// ---------------------------------------------------------
print("\nOperation 2: Electronics products with price < 50000 (name, price, stock)\n");

db.products.find(
  { category: "Electronics", price: { $lt: 50000 } },
  { _id: 0, name: 1, price: 1, stock: 1 }
).forEach(doc => printjson(doc));

// ---------------------------------------------------------
// Operation 3: Review Analysis
// Find all products that have average rating >= 4.0
// Use aggregation to calculate average from reviews array
// ---------------------------------------------------------
print("\nOperation 3: Products with average rating >= 4.0\n");

db.products.aggregate([
  { $addFields: { avg_rating: { $avg: "$reviews.rating" } } },
  { $match: { avg_rating: { $gte: 4.0 } } },
  {
    $project: {
      _id: 0,
      product_id: 1,
      name: 1,
      category: 1,
      avg_rating: { $round: ["$avg_rating", 2] }
    }
  },
  { $sort: { avg_rating: -1, name: 1 } }
]).forEach(doc => printjson(doc));

// ---------------------------------------------------------
// Operation 4: Update Operation
// Add a new review to product "ELEC001"
// Review: {user: "U999", rating: 4, comment: "Good value", date: ISODate()}
// ---------------------------------------------------------
print("\nOperation 4: Add a new review to ELEC001\n");

db.products.updateOne(
  { product_id: "ELEC001" },
  {
    $push: {
      reviews: {
        user_id: "U999",
        username: "U999",
        rating: 4,
        comment: "Good value",
        date: new Date()
      }
    }
  }
);

// Verification (this is the part you should add/replace)
print("\nOperation 4: Verify ELEC001 after adding review\n");

printjson(
  db.products.findOne(
    { product_id: "ELEC001" },
    { _id: 0, product_id: 1, name: 1, reviews: 1 }
  )
);

// ---------------------------------------------------------
// Operation 5: Complex Aggregation
// Calculate average price by category
// Return: category, avg_price, product_count
// Sort by avg_price descending
// ---------------------------------------------------------
print("\nOperation 5: Average price by category\n");

db.products.aggregate([
  {
    $group: {
      _id: "$category",
      avg_price: { $avg: "$price" },
      product_count: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 0,
      category: "$_id",
      avg_price: { $round: ["$avg_price", 2] },
      product_count: 1
    }
  },
  { $sort: { avg_price: -1 } }
]).forEach(doc => printjson(doc));
