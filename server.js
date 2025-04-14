const express = require("express");
const cors = require("cors");
const connectDB = require("./db"); // your MongoDB connection file
const userRoutes = require("./routes/userRoutes");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 4000;

connectDB(); // Establish connection to MongoDB

app.use(cors());
app.use(express.json());

app.use("/api/users", userRoutes);

app.listen(PORT, () => {
  console.log(`✅ Node server running at http://localhost:${PORT}`);
});
