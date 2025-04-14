// models/User.js

const mongoose = require("mongoose");
const bcrypt = require("bcrypt");

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, "Name is required"],
    trim: true
  },
  email: {
    type: String,
    required: [true, "Email is required"],
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: [true, "Password is required"]
  },
  likes: {
    type: [String],
    default: []
  },
  dislikes: {
    type: [String],
    default: []
  },
  favorites: {
    type: [String],
    default: []
  },
  dailySchedule: [
    {
      date: {
        type: Date,
        required: true
      },
      events: {
        type: String,
        required: true
      }
    }
  ],
  upcomingEvents: [
    {
      eventName: {
        type: String,
        required: true
      },
      eventDate: {
        type: Date,
        required: true
      },
      eventDetails: {
        type: String,
        default: ""
      }
    }
  ],
  communicationStyle: {
    type: String,
    default: ""
  },
  voiceClips: [
    {
      clipUrl: {
        type: String,
        required: true
      },
      duration: {
        type: Number // Duration in seconds
      },
      recordedAt: {
        type: Date,
        default: Date.now
      }
    }
  ],
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Pre-save hook to hash password if modified or new
userSchema.pre("save", async function (next) {
  if (!this.isModified("password")) return next();
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to compare candidate password with hashed password
userSchema.methods.comparePassword = async function (candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

module.exports = mongoose.model("User", userSchema);
