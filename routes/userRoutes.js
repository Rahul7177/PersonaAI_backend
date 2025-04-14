const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const User = require("../models/User");
const requireAuth = require("../middleware/authMiddleware");
const authenticate = require('../middleware/authenticate');

const router = express.Router();

// @route    POST /api/users/signup
// @desc     Register a new user
router.post("/signup", async (req, res) => {
  const { name, email, password } = req.body;

  try {
    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: "Email already registered" });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create new user with empty fields for later updates
    const newUser = new User({
      name,
      email,
      password: hashedPassword,
      bio: "",
      interests: [],
      schedule: [],
      personalityTraits: [],
      preferences: {},
      voiceProfile: "",
    });

    await newUser.save();
    res.status(201).json({ message: "User registered successfully" });
  } catch (err) {
    console.error("Signup error:", err);
    res.status(500).json({ error: "Server error during signup" });
  }
});

// @route    POST /api/users/login
// @desc     Authenticate user & get token
router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    // Check user
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    // Check password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    // Create JWT
    const token = jwt.sign(
      { id: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: "7d" }
    );

    res.status(200).json({
      message: "Login successful",
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
      },
    });
  } catch (err) {
    console.error("Login error:", err);
    res.status(500).json({ error: "Server error during login" });
  }
});

// POST /api/users/updateProfile
router.post("/updateProfile", async (req, res) => {
  const { id, likes, dislikes, favorites, dailySchedule, upcomingEvents, communicationStyle } = req.body;

  try {
    const updatedUser = await User.findByIdAndUpdate(
      id,
      {
        likes: likes ? likes.split(",").map(s => s.trim()) : [],
        dislikes: dislikes ? dislikes.split(",").map(s => s.trim()) : [],
        favorites: favorites ? favorites.split(",").map(s => s.trim()) : [],
        dailySchedule: dailySchedule ? [{ events: dailySchedule, date: new Date() }] : [],
        upcomingEvents: Array.isArray(upcomingEvents)
          ? upcomingEvents.map(event => ({
              eventName: event.eventName || "",
              eventDate: event.eventDate ? new Date(event.eventDate) : new Date()
            }))
          : [],
        communicationStyle: communicationStyle || "",
        updatedAt: Date.now()
      },
      { new: true }
    );

    res.status(200).json({ message: "Profile updated successfully", user: updatedUser });
  } catch (error) {
    console.error("Update Profile Error:", error);
    res.status(500).json({ error: "Server error updating profile" });
  }
});

router.post('/updateUserData', authenticate, async (req, res) => {
  try {
    const userId = req.user.id;
    const {
      name,
      likes,
      dislikes,
      favorites,
      dailySchedule,
      upcomingEvents
    } = req.body;

    const updatedUser = await User.findByIdAndUpdate(
      userId,
      {
        name,
        likes,
        dislikes,
        favorites,
        dailySchedule,
        upcomingEvents,
        updatedAt: new Date()
      },
      { new: true }
    );

    if (!updatedUser) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({ message: 'User data updated successfully', user: updatedUser });
  } catch (error) {
    console.error('Update error:', error);
    res.status(500).json({ message: 'Server error while updating user data' });
  }
});


module.exports = router;
